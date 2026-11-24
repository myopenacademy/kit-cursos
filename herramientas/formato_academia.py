#!/usr/bin/env python3
"""Comprueba que un curso cumple FORMATO.md (versión 1) y se puede instalar en MyOpenAcademy.

Revisa, sin ejecutar nada del curso:
  - curso.json: campos, identificadores (forma, que no se repitan y que no desaparezca ninguno
    publicado sin su equivalencia, comparando con la última versión etiquetada en Git), y que cada
    fichero declarado existe (salvo los módulos y retos que todavía no están disponibles) y cada
    módulo de las carpetas de fase está declarado.
  - Títulos del curso, las fases, los módulos, los ejercicios y los retos en texto plano.
  - Cada módulo: título, cabecera, secciones en orden, ejercicios con los títulos de curso.json,
    pistas y solución de cada ejercicio, y preguntas de repaso.
  - Los retos de cada fase, las etapas del proyecto, el glosario, 00-indice.md y los ficheros
    obligatorios.
  - Enlaces del mismo curso y a otros cursos (con sus anclas), imágenes, diagramas Mermaid y HTML.
  - Que el texto de cada «📁 **Código:**» y su destino sean la misma carpeta (aviso).
  - Listas de tareas de Markdown (- [ ], - [x]) fuera de los bloques de código, que la academia todavía no
    dibuja (aviso).
  - Correos fuera del código: <ana@example.com> o <mailto:…>, que CommonMark y GitHub convierten en un enlace
    mailto:, los correos sueltos (ana@example.com), que GitHub también enlaza, y los enlaces [texto](mailto:…), que la academia no admite (aviso).
  - Los huecos [RELLENAR: …] de las plantillas que queden sin rellenar.

Lo que FORMATO.md dice con «debe» es un ERROR (el curso no se instala) y lo que dice con «conviene»,
un AVISO (se instala, pero conviene corregirlo). Cada línea dice el fichero, la línea y qué falta.

De codigo/ solo mira lo que no viaja con Git, con avisos (con Git, lo que guarda Git; sin Git, el disco):
ficheros de texto con CRLF o que no saldrían con LF en un clon en Windows, carpetas vacías, scripts que una
sesión lanza con ./ sin permiso de ejecución, y permisos que un clon no tendría. Una carpeta .git (un repositorio) dentro de codigo/ es un ERROR: Git no guarda su contenido. Y los .env: un .env real
(.env, .env.local… cualquiera salvo .env.example) es un ERROR, porque la academia solo admite .env.example; y un
valor de .env.example con pinta de secreto real (una clave de GitHub, AWS, Stripe…, una clave privada, un JWT,
una contraseña en una URL, o una clave larga y aleatoria en una variable SECRET, TOKEN, PASSWORD, KEY…) es un
AVISO, que dice la línea y la variable, nunca el valor. El código lo verifican las
demás herramientas del kit (verificar_codigo.py --commit, como un clon). No dibuja los diagramas
(comprobar_mermaid.py).

Uso, desde la raíz del curso (con el kit en la carpeta hermana ../kit-cursos/):
    python3 ../kit-cursos/herramientas/formato_academia.py            # el curso de la carpeta actual
    python3 ../kit-cursos/herramientas/formato_academia.py ../curso-x # otro curso
    python3 ../kit-cursos/herramientas/formato_academia.py --help     # esta ayuda

Termina con código 0 si no hay errores (aunque haya avisos), con 1 si hay algún error, y con 2 si los
argumentos están mal (una opción desconocida o una carpeta que no existe), sin revisar nada.
Necesita Python 3.11 o posterior, sin librerías adicionales.
"""
import json
import os
import posixpath
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

VERSION_FORMATO = 1

SECCIONES = [
    "Qué aprenderás",
    "1. Teoría",
    "2. Ejemplos de código",
    "3. Errores típicos",
    "4. Buenas prácticas",
    "5. Ejercicios prácticos resueltos",
    "6. Chuleta",
    "7. Preguntas de repaso",
]
NIVELES_EJERCICIOS = ["🟢 Básico", "🟡 Intermedio", "🔴 Avanzado", "🏆 Caso real"]
CABECERA = ["Versiones", "Conviene saber antes", "Tiempo estimado", "Nivel"]
CABECERA_OBLIGATORIA = {"Conviene saber antes", "Tiempo estimado", "Nivel"}
TRANSICIONES = {"preguntas-de-repaso"}
OBLIGATORIOS = ["README.md", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md"]
GENERADOS = ["00-indice.md", "99-chuleta-global.md"]
CARPETAS_IGNORADAS = {".git", ".verificacion", "herramientas", "node_modules", "codigo"}
# Ficheros de trabajo de quien escribe el curso: no son contenido y la academia no los muestra
FICHEROS_DE_TRABAJO = {"CLAUDE.md", "PLAN-CURSO.md", "ESTADO.md"}

CAMPOS = {
    "curso": {"formato", "tipo", "id", "titulo", "descripcion", "version", "idioma", "repositorio",
              "conviene_saber_antes", "partes", "fases", "proyecto", "equivalencias", "transicion", "ruta_minima"},
    "parte": {"id", "titulo", "fases"},
    "fase": {"id", "carpeta", "titulo", "retos", "retos_disponibles", "modulos"},
    "módulo": {"id", "fichero", "titulo", "disponible", "ejercicios"},
    "ejercicio": {"id", "titulo"},
    "proyecto": {"tipo", "titulo", "etapas", "modulo"},
    "etapa": {"id", "fichero", "titulo"},
    "equivalencia": {"desde", "antes", "ahora", "motivo"},
    "ruta mínima": {"modulos", "etapas", "plantilla"},
}

# Los huecos que admite la plantilla de RUTA-MINIMA.md («plantilla» de «ruta_minima», FORMATO.md 3.2): los
# rellena generar_ruta_minima.py. {{modulos}} es obligatorio.
HUECOS_RUTA_MINIMA = {"resumen", "modulos", "proyecto", "consultas"}
HUECO = re.compile(r"\{\{([^{}]*)\}\}")

ID_CURSO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
CARPETA_FASE = re.compile(r"^fase-(\d{2})-[a-z0-9]+(-[a-z0-9]+)*$")
FICHERO_NUMERADO = re.compile(r"^(\d{2})-[a-z0-9]+(-[a-z0-9]+)*\.md$")
GITHUB = re.compile(r"^https://github\.com/([^/]+)/([^/#?]+)(?:/(blob|tree)/([^/]+)(/[^#?]*)?)?(?:#(.*))?$")
VALLA = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
ENCABEZADO = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")
# Como CommonMark: un tramo de comillas invertidas es entero (no empieza a mitad de otro) y se cierra con otro igual de largo
CODIGO_EN_LINEA = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
ENLACE = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?([^)\s>]*)>?(?:\s+\"[^\"]*\")?\s*\)")
ETIQUETA = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)(?=[\s/>])([^>]*)>")
# Un elemento de una lista de tareas de GitHub: «- [ ] …», «* [x] …», «1. [X] …» (también dentro de una cita)
TAREA = re.compile(r"^[ \t]*(?:>[ \t]*)*(?:[-*+]|[0-9]{1,9}[.)])[ \t]+\[[ xX]\](?:[ \t]|$)")
# Un enlace automático de correo de CommonMark: <ana@example.com> (la forma exacta de la especificación 0.31.2)
# o <mailto:…> (un esquema no distingue mayúsculas). Con «\<» delante no es enlace.
CORREO_AUTOMATICO = re.compile(
    r"(?<!\\)<(?:[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*|[mM][aA][iI][lL][tT][oO]:[^\s<>]*)>")
# Un correo suelto, que GitHub enlaza (enlaces automáticos de GFM): ana@example.com. No cuenta seguido de «:»
# (git@github.com:usuario/repo.git es una dirección de SSH), ni detrás de «/» o «:» (parte de una URL), ni dentro
# de <…>, que ya avisa CORREO_AUTOMATICO.
CORREO_SUELTO = re.compile(r"(?<![A-Za-z0-9.+_@<:/-])[A-Za-z0-9.+_-]+@(?:[A-Za-z0-9_-]+\.)+[A-Za-z0-9_-]*[A-Za-z0-9]"
                           r"(?![A-Za-z0-9_@:-]|\.[A-Za-z0-9_-])")
AVISO_CORREO = ("la academia no admite enlaces mailto:; escribe el correo en código "
                "(`Ana García <ana@example.com>`) (FORMATO.md, apartado 10.7)")
DETALLES = re.compile(r"<details\b[^>]*>|</details\s*>|<summary>(.*?)</summary>")
RELLENAR = re.compile(r"\[RELLENAR\b")
ENTIDAD = re.compile(r"&(#?[a-zA-Z0-9]+);")

FORMATO_EN_TITULO = [
    (re.compile(r"`"), "código entre comillas invertidas"),
    (re.compile(r"\*"), "negrita o cursiva con *"),
    (re.compile(r"__|(^|[^\w])_[^_\s]([^_]*[^_\s])?_($|[^\w])"), "negrita o cursiva con _"),
    (re.compile(r"~~"), "tachado"),
    (re.compile(r"\[[^\]]*\]\([^)]*\)"), "un enlace"),
    (re.compile(r"<[a-zA-Z/][^>]*>"), "HTML"),
]

# El HTML que admite la academia, como su saneador (ContentSanitizer de Code Academy, visto el 8 de noviembre
# de 2026): estas etiquetas se quedan tal cual, solo con estos atributos.
HTML_ADMITIDO = {"p", "blockquote", "hr", "br", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "table",
                 "thead", "tbody", "tr", "th", "td", "pre", "code", "em", "strong", "del", "kbd", "sup", "sub",
                 "details", "summary"}
ATRIBUTOS_ADMITIDOS = {"th": {"align"}, "td": {"align"}, "ol": {"start"}, "code": {"class"}}
# Formato sin efecto: la academia quita la etiqueta (sin atributos) y deja su texto. Es un aviso.
HTML_INERTE = {"span", "div", "u", "b", "i", "s", "mark", "ins", "small", "big", "tt", "font", "center", "strike",
               "abbr", "acronym", "cite", "q", "var", "samp", "dfn", "bdi", "bdo", "ruby", "rp", "rt", "wbr",
               "figure", "figcaption", "section", "article", "header", "footer", "main", "aside", "nav", "hgroup",
               "address", "time", "dl", "dt", "dd"}
IMAGENES = {".png", ".jpg", ".jpeg", ".svg"}
ENLACE_CODIGO = "📁 **Código:**"
ENTIDADES_MERMAID = {"quot", "lt", "gt", "amp"}


# --------------------------------------------------------------------------------------------------
# Informe
# --------------------------------------------------------------------------------------------------

class Informe:
    def __init__(self):
        self.errores = []
        self.avisos = []

    def error(self, fichero, linea, mensaje):
        self.errores.append((str(fichero), linea or 0, mensaje))

    def aviso(self, fichero, linea, mensaje):
        self.avisos.append((str(fichero), linea or 0, mensaje))

    @staticmethod
    def _linea(fichero, linea, tipo, mensaje):
        donde = f"{fichero}:{linea}" if linea else fichero
        return f"{donde}: {tipo}: {mensaje}"

    def imprimir(self, resumen):
        for tipo, lista in (("ERROR", self.errores), ("AVISO", self.avisos)):
            for fichero, linea, mensaje in sorted(lista, key=lambda e: (e[0], e[1])):
                print(self._linea(fichero, linea, tipo, mensaje))
        if self.errores or self.avisos:
            print()
        print(resumen)
        e, a = len(self.errores), len(self.avisos)
        cuenta = f"{e} error{'es' if e != 1 else ''} y {a} aviso{'s' if a != 1 else ''}"
        if self.errores:
            print(f"❌ El curso no cumple FORMATO.md (versión {VERSION_FORMATO}): {cuenta}. No se puede instalar.")
        else:
            print(f"✅ El curso cumple FORMATO.md (versión {VERSION_FORMATO}): {cuenta}.")


# --------------------------------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------------------------------

class Markdown:
    """Un fichero Markdown leído una vez: sus líneas, cuáles son de código y sus encabezados."""

    def __init__(self, ruta, rel):
        self.ruta, self.rel = ruta, rel
        self.texto = ruta.read_text(encoding="utf-8")
        self.lineas = self.texto.split("\n")
        self.en_codigo = [False] * len(self.lineas)
        self.bloques = []           # (primera línea, última línea, lenguaje), índices desde 0
        abierto = None
        for i, linea in enumerate(self.lineas):
            m = VALLA.match(linea)
            if abierto is None:
                if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                    abierto = (i, m.group(1), m.group(2).strip().split(" ")[0].lower())
                    self.en_codigo[i] = True
            else:
                self.en_codigo[i] = True
                inicio, valla, lenguaje = abierto
                if m and m.group(1)[0] == valla[0] and len(m.group(1)) >= len(valla) and not m.group(2).strip():
                    self.bloques.append((inicio, i, lenguaje))
                    abierto = None
        self.sin_cerrar = abierto[0] if abierto else None
        if abierto:
            self.bloques.append((abierto[0], len(self.lineas) - 1, abierto[2]))
        self.encabezados = []       # (índice, nivel, texto)
        for i, linea in enumerate(self.lineas):
            if not self.en_codigo[i]:
                m = ENCABEZADO.match(linea)
                if m:
                    self.encabezados.append((i, len(m.group(1)), m.group(2)))

    def texto_sin_codigo(self, i):
        """La línea i sin el código en línea (lo sustituye por espacios), o vacía si es de un bloque."""
        if self.en_codigo[i]:
            return ""
        return CODIGO_EN_LINEA.sub(lambda m: " " * len(m.group(0)), self.lineas[i])

    def anclas(self):
        if not hasattr(self, "_anclas"):
            vistas, self._anclas = {}, set()
            for _, _, texto in self.encabezados:
                base = ancla(texto)
                n = vistas.get(base, 0)
                self._anclas.add(base if n == 0 else f"{base}-{n}")
                vistas[base] = n + 1
        return self._anclas


ENV_EJEMPLO = ".env.example"
ENV_LINEA = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")
# Valores que se ven falsos: no avisan aunque la variable se llame SECRET o TOKEN
FALSO = re.compile(r"cambia|cámbia|tu[_-]|tus[_-]|aqu[ií]|ejemplo|example|changeme|change[_-]?me|placeholder|dummy|"
                   r"fake|falso|secreto[_-]?de|xxx|\*\*\*|\.\.\.|…|<[^>]*>|\$\{|^\$|rellenar|todo|replace|your[_-]",
                   re.IGNORECASE)
# Formatos de claves reales conocidas (a 16 de noviembre de 2026)
SECRETOS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"), "una clave privada"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "una clave de acceso de AWS"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{22,}"), "un token de GitHub"),
    (re.compile(r"\bglpat-[A-Za-z0-9_-]{20}\b"), "un token de GitLab"),
    (re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}"), "un token de Slack"),
    (re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{16,}"), "una clave de Stripe"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "una clave de Google"),
    (re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}"), "una clave de API de IA"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "un JWT"),
]
URL_CON_CLAVE = re.compile(r"^[a-z][a-z0-9+.-]*://[^/:@\s]+:([^@\s]+)@", re.IGNORECASE)
VARIABLE_SECRETA = re.compile(r"SECRET|TOKEN|PASSWORD|PASSWD|PASS\b|PWD|API_?KEY|PRIVATE|CREDENTIAL|_KEY\b|^KEY\b|"
                              r"CONTRASE[ÑN]A|CLAVE|SECRETO|PRIVAD",
                              re.IGNORECASE)


def secreto_real(variable, valor):
    """Qué parece el valor de una variable de un .env.example si tiene pinta de secreto real, o None."""
    if not valor or FALSO.search(valor):
        return None
    for patron, que in SECRETOS:
        if patron.search(valor):
            return que
    url = URL_CON_CLAVE.match(valor)
    if url and not FALSO.search(url.group(1)):
        return "una URL con contraseña"
    # Una clave larga y aleatoria (letras y cifras mezcladas, sin espacios) en una variable de secretos
    if (VARIABLE_SECRETA.search(variable) and len(valor) >= 16 and " " not in valor
            and re.search(r"[0-9]", valor) and re.search(r"[A-Za-z]", valor) and len(set(valor)) >= 10):
        return "una clave larga y aleatoria"
    return None


def en_codigo(rel):
    """Si la ruta relativa está dentro de una carpeta codigo/ del curso."""
    return "codigo" in rel.split("/")[:-1]


def ancla(encabezado):
    """El ancla que genera GitHub para un encabezado (la misma regla que comprobar_enlaces.py del curso
    de Java, quitando antes el Markdown de enlaces, código y HTML)."""
    trozos = re.split(r"(`+[^`]*`+)", encabezado)       # el código en línea se queda tal cual
    texto = "".join(t if t.startswith("`") else re.sub(r"<[^>]+>", "", re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t))
                    for t in trozos)
    texto = re.sub(r"[^\w\- ]", "", texto.strip().lower())
    return texto.replace(" ", "-")


def etiquetas_mermaid(linea):
    """Los textos de las etiquetas de una línea de Mermaid: entre comillas, corchetes, paréntesis, llaves,
    barras (las de las flechas) y lo que sigue a « : » (mensajes y relaciones)."""
    textos = re.findall(r'"([^"]*)"', linea)
    sin_comillas = re.sub(r'"[^"]*"', '""', linea)
    textos += re.findall(r"\[([^\]]*)\]|\(([^)]*)\)|\{([^}]*)\}|\|([^|]*)\|", sin_comillas)
    textos += re.findall(r"\s:\s*(.+)$", sin_comillas)
    planos = []
    for t in textos:
        planos.extend([x for x in t if x] if isinstance(t, tuple) else [t])
    return planos


def previstos_de(objetivo, rel):
    """Los ficheros de módulos y retos todavía no disponibles del curso al que pertenece la ruta rel
    (resuelta en objetivo), leídos de su curso.json. Para los enlaces a otros cursos."""
    raiz = objetivo
    for _ in Path(rel).parts:
        raiz = raiz.parent
    try:
        datos = json.loads((raiz / "curso.json").read_text(encoding="utf-8"))
        previstos = set()
        for fase in datos.get("fases", []):
            if fase.get("retos_disponibles") is False and isinstance(fase.get("retos"), str):
                previstos.add(fase["retos"])
            for modulo in fase.get("modulos", []):
                if modulo.get("disponible") is False and isinstance(modulo.get("fichero"), str):
                    previstos.add(modulo["fichero"])
        return previstos
    except (OSError, json.JSONDecodeError, AttributeError):
        return set()


def formato_en_titulo(titulo):
    for patron, que in FORMATO_EN_TITULO:
        if patron.search(titulo):
            return que
    return None


def orden_alfabetico(texto):
    """La clave para ordenar en español: sin tildes ni mayúsculas, pero con la ñ entre la n y la o."""
    return sin_tildes("".join("n~" if c in "ñÑ" else c for c in texto))      # «~» va detrás de la «z»


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").casefold()


def recorrer_detalles(md, desde, hasta, informe=None):
    """Los <summary> de primer nivel entre las líneas desde y hasta (sin incluir): [(línea, texto)].
    Si hay informe, avisa de los <details> sin cerrar y de las líneas en blanco que faltan."""
    resumenes, profundidad, abiertos = [], 0, []
    for i in range(desde, hasta):
        linea = md.texto_sin_codigo(i)
        for m in DETALLES.finditer(linea):
            etiqueta = m.group(0)
            if etiqueta.startswith("<details"):
                profundidad += 1
                abiertos.append(i)
            elif etiqueta.startswith("</details"):
                if profundidad == 0:
                    if informe:
                        informe.error(md.rel, i + 1, "</details> sin su <details>")
                    continue
                profundidad -= 1
                abiertos.pop()
                if informe and linea.strip() == "</details>" and i > 0 and md.lineas[i - 1].strip():
                    informe.aviso(md.rel, i + 1, "deja una línea en blanco antes de </details> (si no, GitHub no muestra bien el Markdown de dentro)")
            else:
                if profundidad == 1:
                    resumenes.append((i, m.group(1).strip()))
                if informe and linea.strip() == m.group(0) and i + 1 < len(md.lineas) and md.lineas[i + 1].strip():
                    informe.aviso(md.rel, i + 1, "deja una línea en blanco después de <summary>…</summary> (si no, GitHub no muestra bien el Markdown de dentro)")
    if informe:
        for i in abiertos:
            informe.error(md.rel, i + 1, "<details> sin cerrar")
    return resumenes


# --------------------------------------------------------------------------------------------------
# El curso
# --------------------------------------------------------------------------------------------------

class Curso:
    def __init__(self, raiz, informe):
        self.raiz = raiz
        self.informe = informe
        self.datos = None
        self.texto_json = ""
        self.ids = {}                   # id → descripción
        self.ficheros_modulo = {}       # ruta relativa → módulo
        self.previstos = set()          # rutas relativas de módulos y retos todavía no disponibles
        self.md = {}

    # -- utilidades -------------------------------------------------------------------------------

    def leer(self, rel):
        rel = Path(rel)
        if rel not in self.md:
            self.md[rel] = Markdown(self.raiz / rel, rel.as_posix())
        return self.md[rel]

    def linea_json(self, *valores):
        """La línea de curso.json donde aparece el primero de los valores que se encuentre."""
        for valor in valores:
            if valor is None:
                continue
            aguja = json.dumps(valor, ensure_ascii=False) if not isinstance(valor, str) or not valor.startswith('"') else valor
            pos = self.texto_json.find(aguja)
            if pos >= 0:
                return self.texto_json.count("\n", 0, pos) + 1
        return 1

    def error_json(self, linea, mensaje):
        self.informe.error("curso.json", linea, mensaje)

    def aviso_json(self, linea, mensaje):
        self.informe.aviso("curso.json", linea, mensaje)

    def campos_desconocidos(self, objeto, tipo, donde, linea):
        for clave in sorted(set(objeto) - CAMPOS[tipo]):
            self.aviso_json(self.linea_json(f'"{clave}"') if linea == 1 else linea,
                            f"{donde}: campo desconocido «{clave}» (se ignora; ¿está bien escrito?)")

    def texto(self, objeto, clave, donde, linea, obligatorio=True):
        valor = objeto.get(clave)
        if valor is None:
            if obligatorio:
                self.error_json(linea, f"{donde}: falta el campo «{clave}»")
            return None
        if not isinstance(valor, str) or not valor.strip():
            self.error_json(linea, f"{donde}: «{clave}» debe ser un texto no vacío")
            return None
        return valor

    def lista(self, objeto, clave, donde, linea, obligatorio=True):
        valor = objeto.get(clave)
        if valor is None:
            if obligatorio:
                self.error_json(linea, f"{donde}: falta el campo «{clave}»")
            return []
        if not isinstance(valor, list):
            self.error_json(linea, f"{donde}: «{clave}» debe ser una lista")
            return []
        return valor

    def titulo(self, objeto, donde, linea):
        titulo = self.texto(objeto, "titulo", donde, linea)
        if titulo:
            que = formato_en_titulo(titulo)
            if que:
                self.error_json(self.linea_json(titulo, linea) if False else linea,
                                f"{donde}: el título «{titulo}» lleva formato Markdown ({que}); los títulos son texto plano")
        return titulo

    def identificador(self, objeto, donde, linea):
        ident = objeto.get("id")
        if ident is None:
            self.error_json(linea, f"{donde}: falta el campo «id»")
            return None
        prefijo = self.datos.get("id") if isinstance(self.datos.get("id"), str) else ""
        if not isinstance(ident, str) or not re.fullmatch(re.escape(prefijo) + r"\.[a-z0-9]+([.-][a-z0-9]+)*", ident):
            self.error_json(linea, f"{donde}: el identificador «{ident}» debe ser «{prefijo}.» y un nombre "
                                   "(solo minúsculas sin tildes, cifras, guiones y puntos)")
            return ident if isinstance(ident, str) else None
        if ident in self.ids:
            self.error_json(linea, f"{donde}: el identificador «{ident}» ya lo usa {self.ids[ident]}")
        else:
            self.ids[ident] = donde
        return ident

    # -- curso.json --------------------------------------------------------------------------------

    def cargar(self):
        ruta = self.raiz / "curso.json"
        if not ruta.is_file():
            self.informe.error("curso.json", 0, "no existe: es la identidad del curso (FORMATO.md, apartado 3)")
            return False
        self.texto_json = ruta.read_text(encoding="utf-8")
        try:
            self.datos = json.loads(self.texto_json)
        except json.JSONDecodeError as e:
            self.informe.error("curso.json", e.lineno, f"no es un JSON válido: {e.msg} (columna {e.colno})")
            return False
        if not isinstance(self.datos, dict):
            self.informe.error("curso.json", 1, "debe ser un objeto JSON ({ … })")
            return False
        return True

    def comprobar_json(self):
        d = self.datos
        formato = d.get("formato")
        if formato is None:
            self.error_json(1, "falta el campo «formato» (la versión de FORMATO.md que cumple el curso)")
        elif not isinstance(formato, int) or isinstance(formato, bool) or formato < 1:
            self.error_json(self.linea_json('"formato"'), "«formato» debe ser un número entero (hoy, 1)")
        elif formato > VERSION_FORMATO:
            self.error_json(self.linea_json('"formato"'), f"el curso usa la versión {formato} del formato y este kit solo conoce "
                                                          f"hasta la {VERSION_FORMATO}: actualiza el kit")
        tipo = d.get("tipo")
        if tipo != "curso":
            self.error_json(self.linea_json('"tipo"'), f"«tipo» debe ser \"curso\" (es {json.dumps(tipo, ensure_ascii=False)})")
        ident = d.get("id")
        if not isinstance(ident, str) or not ID_CURSO.match(ident):
            self.error_json(self.linea_json('"id"'), f"el «id» del curso ({json.dumps(ident, ensure_ascii=False)}) debe ser corto, "
                                                     "en minúsculas, sin tildes ni espacios (por ejemplo, \"java\")")
            d["id"] = ident if isinstance(ident, str) else ""
        titulo = self.texto(d, "titulo", "el curso", self.linea_json('"titulo"'))
        if titulo and formato_en_titulo(titulo):
            self.error_json(self.linea_json('"titulo"'), f"el título del curso lleva formato Markdown ({formato_en_titulo(titulo)}); "
                                                         "los títulos son texto plano")
        self.texto(d, "descripcion", "el curso", self.linea_json('"descripcion"'))
        version = self.texto(d, "version", "el curso", self.linea_json('"version"'))
        if version and not SEMVER.match(version):
            self.error_json(self.linea_json('"version"'), f"«version» ({version}) debe ser MAYOR.MENOR.PARCHE, por ejemplo 1.0.0")
        self.texto(d, "idioma", "el curso", self.linea_json('"idioma"'))
        repositorio = self.texto(d, "repositorio", "el curso", self.linea_json('"repositorio"'))
        if repositorio and not re.match(r"^https://github\.com/[^/]+/[^/]+/?$", repositorio):
            self.error_json(self.linea_json('"repositorio"'), f"«repositorio» ({repositorio}) debe ser la dirección del repositorio "
                                                              "en GitHub: https://github.com/<cuenta>/<repositorio>")
        for curso in self.lista(d, "conviene_saber_antes", "el curso", self.linea_json('"conviene_saber_antes"')):
            if not isinstance(curso, str) or not ID_CURSO.match(curso):
                self.error_json(self.linea_json('"conviene_saber_antes"'),
                                f"«conviene_saber_antes»: {json.dumps(curso, ensure_ascii=False)} no es el id de un curso")
        self.campos_desconocidos(d, "curso", "el curso", 1)
        for t in self.lista(d, "transicion", "el curso", self.linea_json('"transicion"'), obligatorio=False):
            if t not in TRANSICIONES:
                self.error_json(self.linea_json('"transicion"'), f"«transicion»: «{t}» no existe (hoy solo se admite "
                                                                 f"{', '.join(sorted(TRANSICIONES))})")

        fases = self.lista(d, "fases", "el curso", self.linea_json('"fases"'))
        if not fases and "fases" in d:
            self.error_json(self.linea_json('"fases"'), "el curso debe tener al menos una fase")
        self.fases = [f for f in fases if isinstance(f, dict)]
        if len(self.fases) != len(fases):
            self.error_json(self.linea_json('"fases"'), "cada fase debe ser un objeto { … }")
        carpetas, anterior = set(), 0
        for n, fase in enumerate(self.fases, 1):
            self.comprobar_fase(fase, n, carpetas)
            m = CARPETA_FASE.match(str(fase.get("carpeta", "")))
            if m:
                if int(m.group(1)) <= anterior:
                    self.aviso_json(self.linea_json(fase.get("carpeta")), f"la carpeta «{fase['carpeta']}» no sigue el orden de "
                                                                          "las fases (conviene numerarlas en orden)")
                anterior = int(m.group(1))
        self.comprobar_partes()
        self.comprobar_proyecto()
        self.comprobar_ruta_minima()
        self.comprobar_equivalencias()

    def comprobar_fase(self, fase, n, carpetas):
        linea = self.linea_json(fase.get("id"), fase.get("carpeta"))
        donde = f"fase {n}"
        ident = self.identificador(fase, donde, linea)
        if ident:
            donde = f"fase «{ident}»"
            self.ids[ident] = donde
        self.campos_desconocidos(fase, "fase", donde, linea)
        self.titulo(fase, donde, linea)
        carpeta = self.texto(fase, "carpeta", donde, linea)
        if carpeta:
            if not CARPETA_FASE.match(carpeta):
                self.error_json(linea, f"{donde}: la carpeta «{carpeta}» debe llamarse fase-NN-nombre (minúsculas, sin tildes, "
                                       "sin espacios)")
            if carpeta in carpetas:
                self.error_json(linea, f"{donde}: la carpeta «{carpeta}» ya la usa otra fase")
            carpetas.add(carpeta)
        modulos = self.lista(fase, "modulos", donde, linea)
        if not modulos and "modulos" in fase:
            self.error_json(linea, f"{donde}: la fase debe tener al menos un módulo")
        fase["_modulos"] = [m for m in modulos if isinstance(m, dict)]
        if len(fase["_modulos"]) != len(modulos):
            self.error_json(linea, f"{donde}: cada módulo debe ser un objeto {{ … }}")
        anterior = 0
        for modulo in fase["_modulos"]:
            self.comprobar_modulo(modulo, fase, carpeta)
            fichero = modulo.get("fichero")
            if isinstance(fichero, str):
                m = FICHERO_NUMERADO.match(Path(fichero).name)
                if m:
                    if int(m.group(1)) <= anterior:
                        self.aviso_json(self.linea_json(fichero), f"«{fichero}» no sigue el orden de los módulos de la fase "
                                                                  "(conviene numerarlos en orden)")
                    anterior = int(m.group(1))
        # Retos
        retos = fase.get("retos")
        disponibles = fase.get("retos_disponibles", True)
        if not isinstance(disponibles, bool):
            self.error_json(linea, f"{donde}: «retos_disponibles» debe ser true o false")
            disponibles = True
        if retos is None:
            if "retos_disponibles" in fase:
                self.error_json(linea, f"{donde}: «retos_disponibles» sin «retos» (pon la ruta prevista de su retos.md)")
            elif not self.solo_proyecto(fase):
                self.aviso_json(linea, f"{donde}: la fase no tiene retos (conviene que cada fase los tenga)")
        elif not isinstance(retos, str):
            self.error_json(linea, f"{donde}: «retos» debe ser la ruta de su retos.md")
        else:
            if carpeta and retos != f"{carpeta}/retos.md":
                self.error_json(self.linea_json(retos, linea), f"{donde}: «retos» debe ser «{carpeta}/retos.md» (es «{retos}»)")
            elif not disponibles:
                self.previstos.add(retos)
                if (self.raiz / retos).exists():
                    self.aviso_json(self.linea_json(retos, linea), f"{donde}: «{retos}» ya existe, pero sigue con "
                                                                   "\"retos_disponibles\": false (la academia no lo mostrará)")
                elif not self.solo_proyecto(fase):
                    self.aviso_json(self.linea_json(retos, linea), f"{donde}: los retos todavía no están escritos")
            elif not (self.raiz / retos).is_file():
                self.error_json(self.linea_json(retos, linea), f"{donde}: no existe «{retos}» (si todavía no está escrito, "
                                                               "añade \"retos_disponibles\": false)")
            else:
                fase["_retos"] = retos

    def solo_proyecto(self, fase):
        proyecto = self.datos.get("proyecto")
        return (isinstance(proyecto, dict) and proyecto.get("tipo") == "modulo"
                and [m.get("id") for m in fase.get("_modulos", [])] == [proyecto.get("modulo")])

    def comprobar_modulo(self, modulo, fase, carpeta):
        linea = self.linea_json(modulo.get("id"), modulo.get("fichero"))
        ident = self.identificador(modulo, "un módulo", linea)
        donde = f"módulo «{ident}»"
        if ident:
            self.ids[ident] = donde
        self.campos_desconocidos(modulo, "módulo", donde, linea)
        self.titulo(modulo, donde, linea)
        disponible = modulo.get("disponible", True)
        if not isinstance(disponible, bool):
            self.error_json(linea, f"{donde}: «disponible» debe ser true o false")
            disponible = True
        modulo["_disponible"] = disponible
        fichero = modulo.get("fichero")
        if fichero is None:
            if disponible:
                self.error_json(linea, f"{donde}: falta el campo «fichero»")
            else:
                self.aviso_json(linea, f"{donde}: conviene poner ya su «fichero» previsto, para cerrar los nombres antes de escribir")
        elif not isinstance(fichero, str):
            self.error_json(linea, f"{donde}: «fichero» debe ser una ruta")
        else:
            ruta = Path(fichero)
            if carpeta and (ruta.parent.as_posix() != carpeta or not FICHERO_NUMERADO.match(ruta.name)):
                self.error_json(linea, f"{donde}: «{fichero}» debe estar en la carpeta de su fase y llamarse NN-nombre.md "
                                       f"({carpeta}/NN-nombre.md)")
            if fichero in self.ficheros_modulo:
                self.error_json(linea, f"{donde}: el fichero «{fichero}» ya lo usa otro módulo")
            self.ficheros_modulo[fichero] = modulo
            if disponible:
                if not (self.raiz / fichero).is_file():
                    self.error_json(linea, f"{donde}: no existe «{fichero}» (si todavía no está escrito, añade \"disponible\": false)")
            else:
                self.previstos.add(fichero)
                if (self.raiz / fichero).exists():
                    self.aviso_json(linea, f"{donde}: «{fichero}» ya existe, pero sigue con \"disponible\": false "
                                           "(la academia no lo mostrará)")
        titulos = set()
        for ejercicio in self.lista(modulo, "ejercicios", donde, linea):
            if not isinstance(ejercicio, dict):
                self.error_json(linea, f"{donde}: cada ejercicio debe ser un objeto {{ \"id\": …, \"titulo\": … }}")
                continue
            lin = self.linea_json(ejercicio.get("id"), linea)
            ide = self.identificador(ejercicio, f"un ejercicio de {donde}", lin)
            self.campos_desconocidos(ejercicio, "ejercicio", f"ejercicio «{ide}»", lin)
            t = self.titulo(ejercicio, f"ejercicio «{ide}»", lin)
            if t in titulos:
                self.error_json(lin, f"{donde}: dos ejercicios con el título «{t}» (el título debe distinguirlos)")
            titulos.add(t)

    def comprobar_partes(self):
        if "partes" not in self.datos:
            return
        linea = self.linea_json('"partes"')
        ids_fases = [f.get("id") for f in self.fases]
        vistas = {}
        for parte in self.lista(self.datos, "partes", "el curso", linea):
            if not isinstance(parte, dict):
                self.error_json(linea, "cada parte debe ser un objeto { … }")
                continue
            lin = self.linea_json(parte.get("id"), linea)
            ident = self.identificador(parte, "una parte", lin)
            donde = f"parte «{ident}»"
            self.campos_desconocidos(parte, "parte", donde, lin)
            self.titulo(parte, donde, lin)
            for f in self.lista(parte, "fases", donde, lin):
                if f not in ids_fases:
                    self.error_json(lin, f"{donde}: la fase «{f}» no existe")
                elif f in vistas:
                    self.error_json(lin, f"{donde}: la fase «{f}» ya está en la parte «{vistas[f]}» (cada fase va en una sola)")
                else:
                    vistas[f] = ident
        for f in ids_fases:
            if f and f not in vistas:
                self.error_json(self.linea_json(f), f"la fase «{f}» no está en ninguna parte (si hay partes, cada fase va en una)")
        self.comprobar_tramos_de_partes(linea, ids_fases, vistas)

    def comprobar_tramos_de_partes(self, linea, ids_fases, vistas):
        """Cada parte, un tramo de fases seguidas en el orden del curso, y las partes, una tras otra (revisión 1.1)."""
        posicion = {f: n for n, f in enumerate(ids_fases) if f}
        anterior = None                                   # (id, primera posición) de la parte anterior con fases
        for parte in self.lista(self.datos, "partes", "el curso", linea):
            if not isinstance(parte, dict) or not isinstance(parte.get("fases"), list):
                continue
            ident = parte.get("id")
            lin = self.linea_json(ident, linea)
            if not parte["fases"]:
                self.error_json(lin, f"parte «{ident}»: no tiene fases (cada parte agrupa al menos una)")
                continue
            # solo las fases que existen y son de esta parte (las demás ya tienen su error)
            suyas = [f for f in parte["fases"] if f in posicion and vistas.get(f) == ident]
            if not suyas:
                continue
            desorden = next(((a, b) for a, b in zip(suyas, suyas[1:]) if posicion[b] < posicion[a]), None)
            if desorden:
                self.error_json(lin, f"parte «{ident}»: sus fases no van en el orden del curso "
                                     f"(«{desorden[0]}» va antes que «{desorden[1]}»)")
            else:
                for a, b in zip(suyas, suyas[1:]):
                    if posicion[b] != posicion[a] + 1:
                        medio = ids_fases[posicion[a] + 1]
                        de = f", de la parte «{vistas[medio]}»" if medio in vistas else ""
                        self.error_json(lin, f"parte «{ident}»: sus fases no van seguidas "
                                             f"(entre «{a}» y «{b}» está «{medio}»{de})")
                        break
            primera = min(posicion[f] for f in suyas)
            if anterior and primera < anterior[1]:
                self.error_json(lin, f"la parte «{anterior[0]}» va delante de «{ident}» en «partes», "
                                     "pero sus fases van detrás")
            anterior = (ident, primera)

    def comprobar_proyecto(self):
        proyecto = self.datos.get("proyecto")
        linea = self.linea_json('"proyecto"')
        self.etapas = []
        if proyecto is None:
            self.error_json(1, "falta el campo «proyecto»: todo curso debe tener un proyecto para el portfolio del alumno "
                               "(FORMATO.md, apartado 8)")
            return
        if not isinstance(proyecto, dict):
            self.error_json(linea, "«proyecto» debe ser un objeto { … }")
            return
        self.campos_desconocidos(proyecto, "proyecto", "el proyecto", linea)
        tipo = proyecto.get("tipo")
        if tipo == "modulo":
            modulo = proyecto.get("modulo")
            if not any(m.get("id") == modulo for f in self.fases for m in f.get("_modulos", [])):
                self.error_json(linea, f"el proyecto: el módulo «{modulo}» no existe en «fases»")
        elif tipo == "etapas":
            self.titulo(proyecto, "el proyecto", linea)
            etapas = self.lista(proyecto, "etapas", "el proyecto", linea)
            if not etapas and "etapas" in proyecto:
                self.error_json(linea, "el proyecto: debe tener al menos una etapa")
            for etapa in etapas:
                if not isinstance(etapa, dict):
                    self.error_json(linea, "el proyecto: cada etapa debe ser un objeto { … }")
                    continue
                lin = self.linea_json(etapa.get("id"), linea)
                ident = self.identificador(etapa, "una etapa", lin)
                donde = f"etapa «{ident}»"
                self.campos_desconocidos(etapa, "etapa", donde, lin)
                self.titulo(etapa, donde, lin)
                fichero = self.texto(etapa, "fichero", donde, lin)
                if fichero:
                    ruta = Path(fichero)
                    if ruta.parent.as_posix() != "proyecto" or not FICHERO_NUMERADO.match(ruta.name):
                        self.error_json(lin, f"{donde}: «{fichero}» debe estar en proyecto/ y llamarse NN-nombre.md")
                    elif not (self.raiz / fichero).is_file():
                        self.error_json(lin, f"{donde}: no existe «{fichero}»")
                    else:
                        self.etapas.append(fichero)
        else:
            self.error_json(linea, f"el proyecto: «tipo» debe ser \"etapas\" o \"modulo\" (es {json.dumps(tipo, ensure_ascii=False)})")

    def comprobar_ruta_minima(self):
        """El campo opcional «ruta_minima» (FORMATO.md 3.2): de él sale RUTA-MINIMA.md con generar_ruta_minima.py."""
        ruta = self.datos.get("ruta_minima")
        if ruta is None:
            return
        linea = self.linea_json('"ruta_minima"')
        if not isinstance(ruta, dict):
            self.error_json(linea, "«ruta_minima» debe ser un objeto { \"modulos\": [ … ], \"etapas\": [ … ], "
                                   "\"plantilla\": … } (FORMATO.md, apartado 3.2)")
            return
        self.campos_desconocidos(ruta, "ruta mínima", "ruta mínima", linea)
        modulos = {m.get("id") for f in self.fases for m in f.get("_modulos", [])}
        proyecto = self.datos.get("proyecto")
        etapas = proyecto.get("etapas") if isinstance(proyecto, dict) else None
        etapas = {e.get("id") for e in etapas if isinstance(e, dict)} if isinstance(etapas, list) else set()
        for clave, que, existentes, obligatorio in (("modulos", "el módulo", modulos, True),
                                                    ("etapas", "la etapa", etapas, False)):
            lista = self.lista(ruta, clave, "«ruta_minima»", linea, obligatorio=obligatorio)
            if clave == "modulos" and not lista and isinstance(ruta.get("modulos"), list):
                self.error_json(linea, "«ruta_minima»: «modulos» debe tener al menos un módulo")
            vistos = set()
            for ident in lista:
                if not isinstance(ident, str):
                    self.error_json(linea, f"«ruta_minima»: en «{clave}», {json.dumps(ident, ensure_ascii=False)} "
                                           "no es un identificador")
                    continue
                if ident in vistos:
                    self.error_json(linea, f"«ruta_minima»: «{ident}» está dos veces en «{clave}»")
                elif ident not in existentes:
                    self.error_json(linea, f"«ruta_minima»: {que} «{ident}» no existe en el curso")
                vistos.add(ident)
        plantilla = self.texto(ruta, "plantilla", "«ruta_minima»", linea, obligatorio=False)
        if plantilla:
            fichero = self.raiz / plantilla
            if "/" in plantilla or "\\" in plantilla or not plantilla.endswith(".md"):
                self.error_json(linea, f"«ruta_minima»: la plantilla «{plantilla}» debe ser un fichero .md de la raíz del curso")
            elif not fichero.is_file():
                self.error_json(linea, f"«ruta_minima»: no existe «{plantilla}» (la plantilla de RUTA-MINIMA.md)")
            else:
                self.comprobar_plantilla_ruta_minima(plantilla)
        if not (self.raiz / "RUTA-MINIMA.md").is_file():
            self.aviso_json(linea, "«ruta_minima»: falta RUTA-MINIMA.md; genéralo con generar_ruta_minima.py del kit "
                                   "(FORMATO.md, apartado 4)")

    def comprobar_plantilla_ruta_minima(self, plantilla):
        admitidos = ", ".join("{{" + h + "}}" for h in sorted(HUECOS_RUTA_MINIMA))
        hay_modulos = False
        texto = (self.raiz / plantilla).read_text(encoding="utf-8")
        for n, linea in enumerate(texto.splitlines(), 1):
            for m in HUECO.finditer(linea):
                if m.group(1) == "modulos":
                    hay_modulos = True
                elif m.group(1) not in HUECOS_RUTA_MINIMA:
                    self.informe.error(plantilla, n, f"el hueco {m.group(0)} no existe (se admiten {admitidos})")
        if not hay_modulos:
            self.informe.error(plantilla, 1, "falta {{modulos}}, el hueco donde va la lista de módulos de la ruta mínima")

    def comprobar_equivalencias(self):
        linea = self.linea_json('"equivalencias"')
        self.antes = set()
        lista = self.lista(self.datos, "equivalencias", "el curso", linea)
        for eq in lista:
            if isinstance(eq, dict) and isinstance(eq.get("antes"), str):
                self.antes.add(eq["antes"])
        for eq in lista:
            if not isinstance(eq, dict):
                self.error_json(linea, "cada equivalencia debe ser un objeto { \"desde\": …, \"antes\": …, \"ahora\": [ … ] }")
                continue
            lin = self.linea_json(eq.get("antes"), linea)
            antes = eq.get("antes")
            donde = f"equivalencia de «{antes}»"
            self.campos_desconocidos(eq, "equivalencia", donde, lin)
            desde = self.texto(eq, "desde", donde, lin)
            if desde and not SEMVER.match(desde):
                self.error_json(lin, f"{donde}: «desde» ({desde}) debe ser una versión MAYOR.MENOR.PARCHE")
            if not isinstance(antes, str):
                self.error_json(lin, "una equivalencia sin «antes» (el identificador que ya no existe)")
            elif antes in self.ids:
                self.error_json(lin, f"{donde}: «{antes}» sigue existiendo; una equivalencia es para los que ya no existen")
            ahora = eq.get("ahora")
            if not isinstance(ahora, list):
                self.error_json(lin, f"{donde}: «ahora» debe ser una lista (vacía si se retira)")
                continue
            for nuevo in ahora:
                if nuevo not in self.ids and nuevo not in self.antes:
                    self.error_json(lin, f"{donde}: «{nuevo}» no existe en el curso")
            if not ahora and not (isinstance(eq.get("motivo"), str) and eq["motivo"].strip()):
                self.error_json(lin, f"{donde}: un identificador retirado («ahora» vacío) debe llevar «motivo»")

    def comprobar_publicados(self):
        """Que no desaparezca ningún identificador publicado sin su equivalencia (comparando con la última
        versión etiquetada en Git, vX.Y.Z)."""
        try:
            etiquetas = subprocess.run(["git", "-C", str(self.raiz), "tag", "--list", "v*", "--sort=-v:refname"],
                                       capture_output=True, text=True, check=True).stdout.split()
        except (OSError, subprocess.CalledProcessError):
            return "sin Git: no se ha comparado con la última versión publicada"
        etiquetas = [e for e in etiquetas if SEMVER.match(e[1:])]
        if not etiquetas:
            return "sin versiones etiquetadas todavía"
        etiqueta = etiquetas[0]
        try:
            anterior = json.loads(subprocess.run(["git", "-C", str(self.raiz), "show", f"{etiqueta}:curso.json"],
                                                 capture_output=True, text=True, check=True).stdout)
        except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
            self.aviso_json(1, f"no he podido leer el curso.json de la versión {etiqueta} para compararlo")
            return f"comparado con {etiqueta}: sin curso.json legible"
        publicados = set()
        for fase in anterior.get("fases", []):
            publicados.add(fase.get("id"))
            for modulo in fase.get("modulos", []):
                publicados.add(modulo.get("id"))
                publicados.update(e.get("id") for e in modulo.get("ejercicios", []))
        publicados.update(p.get("id") for p in anterior.get("partes", []))
        proyecto = anterior.get("proyecto", {})
        if isinstance(proyecto, dict):
            publicados.update(e.get("id") for e in proyecto.get("etapas", []))
        for ident in sorted(i for i in publicados if isinstance(i, str)):
            if ident not in self.ids and ident not in self.antes:
                self.error_json(self.linea_json('"equivalencias"'),
                                f"«{ident}» estaba en la versión {etiqueta} y ya no existe: añade su equivalencia "
                                "(FORMATO.md, apartado 11.2)")
        version = self.datos.get("version", "")
        if SEMVER.match(str(version)) and tuple(map(int, version.split("."))) < tuple(map(int, etiqueta[1:].split("."))):
            self.aviso_json(self.linea_json('"version"'), f"la versión {version} es anterior a la última publicada ({etiqueta})")
        return f"comparado con {etiqueta}"

    # -- ficheros y carpetas -----------------------------------------------------------------------

    def comprobar_estructura(self):
        for nombre in OBLIGATORIOS:
            if not (self.raiz / nombre).is_file():
                self.informe.error(nombre, 0, "falta: es obligatorio en todo curso (FORMATO.md, apartado 4)")
        for nombre in GENERADOS:
            if not (self.raiz / nombre).is_file():
                self.informe.aviso(nombre, 0, "falta: se genera desde curso.json (FORMATO.md, apartado 4)")
        if not (self.raiz / "ROADMAP.md").is_file():
            self.informe.aviso("ROADMAP.md", 0, "falta: conviene que el curso tenga su ruta de aprendizaje")
        glosario = self.raiz / "glosario.md"
        if self.datos.get("id") == "inicial":
            if glosario.is_file():
                self.comprobar_glosario()
            else:
                self.informe.aviso("glosario.md", 0, "falta: el curso inicial tiene el glosario común (FORMATO.md, apartado 9)")
        elif glosario.is_file():
            self.comprobar_glosario()          # el glosario propio del curso (FORMATO.md, apartado 9)
        declaradas = {f.get("carpeta") for f in self.fases}
        for carpeta in sorted(p for p in self.raiz.glob("fase-*") if p.is_dir()):
            if carpeta.name not in declaradas:
                self.informe.error(carpeta.name + "/", 0, "carpeta de fase que no está en curso.json")
        for fase in self.fases:
            carpeta = fase.get("carpeta")
            if not isinstance(carpeta, str) or not (self.raiz / carpeta).is_dir():
                if isinstance(carpeta, str) and (any(m.get("_disponible") for m in fase.get("_modulos", []))):
                    self.informe.error(carpeta + "/", 0, "no existe la carpeta de la fase")
                continue
            for hijo in sorted((self.raiz / carpeta).iterdir()):
                rel = f"{carpeta}/{hijo.name}"
                if hijo.is_dir():
                    if hijo.name not in {"codigo", "img"}:
                        self.informe.aviso(rel + "/", 0, "carpeta que no prevé el formato (en una fase solo van codigo/ e img/)")
                elif hijo.suffix == ".md":
                    if hijo.name != "retos.md" and rel not in self.ficheros_modulo:
                        self.informe.error(rel, 0, "módulo que no está en curso.json")
                    elif hijo.name == "retos.md" and fase.get("retos") != rel:
                        self.informe.error(rel, 0, "retos que no están declarados en curso.json («retos» de su fase)")
        proyecto = self.raiz / "proyecto"
        if proyecto.is_dir():
            for md in sorted(proyecto.glob("*.md")):
                if f"proyecto/{md.name}" not in self.etapas and md.name != "README.md":
                    tipo = self.datos.get("proyecto", {}).get("tipo") if isinstance(self.datos.get("proyecto"), dict) else None
                    self.informe.error(f"proyecto/{md.name}", 0, "etapa del proyecto que no está en curso.json"
                                       + (" (el proyecto es de tipo \"modulo\": aquí no van etapas)" if tipo == "modulo" else ""))

    # -- módulos -----------------------------------------------------------------------------------

    def comprobar_modulos(self):
        transicion = set(self.datos.get("transicion") or []) if isinstance(self.datos.get("transicion"), list) else set()
        for nfase, fase in enumerate(self.fases, 1):
            for modulo in fase.get("_modulos", []):
                fichero = modulo.get("fichero")
                if modulo.get("_disponible") and isinstance(fichero, str) and (self.raiz / fichero).is_file():
                    self.comprobar_modulo_md(self.leer(fichero), modulo, fase, transicion)
            if fase.get("_retos"):
                self.comprobar_retos(self.leer(fase["_retos"]), fase)

    def comprobar_modulo_md(self, md, modulo, fase, transicion):
        inf = self.informe
        lineas = md.lineas
        # Título
        primera = next((i for i, l in enumerate(lineas) if l.strip()), None)
        m = re.match(r"^# (\d{2})\.(\d{2}) (.+?)\s*$", lineas[primera]) if primera is not None else None
        if not m:
            inf.error(md.rel, (primera or 0) + 1, "la primera línea debe ser el título: «# NN.NN Título»")
        else:
            titulo = m.group(3)
            if titulo != modulo.get("titulo"):
                inf.error(md.rel, primera + 1, f"el título «{titulo}» no es el de curso.json («{modulo.get('titulo')}»)")
            elif formato_en_titulo(titulo):
                inf.error(md.rel, primera + 1, f"el título lleva formato Markdown ({formato_en_titulo(titulo)}); "
                                               "los títulos son texto plano")
            nf = CARPETA_FASE.match(str(fase.get("carpeta", "")))
            nm = FICHERO_NUMERADO.match(Path(str(modulo.get("fichero"))).name)
            if nf and nm and (m.group(1), m.group(2)) != (nf.group(1), nm.group(1)):
                inf.aviso(md.rel, primera + 1, f"el número {m.group(1)}.{m.group(2)} no coincide con la fase y el fichero "
                                               f"({nf.group(1)}.{nm.group(1)})")
        # Cabecera
        if primera is not None:
            self.comprobar_cabecera(md, primera + 1)
        # Secciones
        secciones = [(i, t) for i, nivel, t in md.encabezados if nivel == 2]
        nombres = [t for _, t in secciones]
        posiciones = {}
        esperado = 0
        for i, t in secciones:
            if t in SECCIONES:
                k = SECCIONES.index(t)
                if t in posiciones:
                    inf.error(md.rel, i + 1, f"la sección «{t}» está repetida")
                elif k < esperado:
                    inf.error(md.rel, i + 1, f"la sección «{t}» está fuera de su sitio (orden: {' · '.join(SECCIONES)})")
                else:
                    posiciones[t] = i
                    esperado = k + 1
            else:
                parecida = next((s for s in SECCIONES if sin_tildes(s.split(". ")[-1]) in sin_tildes(t)), None)
                pista = f" (¿«{parecida}»?)" if parecida else ""
                inf.error(md.rel, i + 1, f"sección «{t}» que no está en la plantilla del módulo{pista}")
        for s in SECCIONES:
            if s not in nombres:
                if s == "7. Preguntas de repaso" and "preguntas-de-repaso" in transicion:
                    inf.aviso(md.rel, 0, "faltan las preguntas de repaso («## 7. Preguntas de repaso»; el curso está en transición)")
                else:
                    inf.error(md.rel, 0, f"falta la sección «## {s}»")
        limites = sorted(posiciones.values()) + [len(lineas)]

        def rango(seccion):
            if seccion not in posiciones:
                return None
            inicio = posiciones[seccion]
            siguiente = min((i for i, _, _ in [(j, 0, 0) for j, n, _ in md.encabezados if n <= 2] if i > inicio),
                            default=len(lineas))
            return inicio, siguiente

        # Subapartados numerados (FORMATO.md, 5.1): los de estas cuatro secciones; los demás, no
        for s in ("1. Teoría", "2. Ejemplos de código", "3. Errores típicos", "4. Buenas prácticas"):
            r = rango(s)
            if not r:
                continue
            numero = s.split(".")[0]
            for i, nivel, t in md.encabezados:
                if r[0] < i < r[1] and nivel == 3 and not re.match(rf"^{numero}\.\d+\. ", t):
                    inf.aviso(md.rel, i + 1, f"los subapartados de «{s}» se numeran: «### {numero}.1. …»")
        # Ejercicios
        r = rango("5. Ejercicios prácticos resueltos")
        if r:
            self.comprobar_ejercicios(md, modulo, r)
        # Preguntas de repaso
        r = rango("7. Preguntas de repaso")
        if r:
            self.comprobar_preguntas(md, r)
        # Navegación
        if not any("📚" in l and "00-indice.md" in l for l in lineas[-8:]):
            inf.aviso(md.rel, len(lineas), "falta la navegación del final (⬅️ Anterior · 📚 Índice · ➡️ Siguiente)")
        recorrer_detalles(md, 0, len(lineas), inf)

    def comprobar_cabecera(self, md, desde):
        inf, lineas = self.informe, md.lineas
        i = desde
        while i < len(lineas) and not lineas[i].strip():
            i += 1
        vistos = {}
        while i < len(lineas) and lineas[i].startswith(">"):
            m = re.match(r"^>\s*\*\*(.+?):\*\*\s*(.*?)\s*$", lineas[i])
            if not m:
                if lineas[i].strip("> \t"):
                    inf.aviso(md.rel, i + 1, "línea de la cabecera que no es «> **Dato:** valor»")
            else:
                clave, valor = m.group(1), m.group(2)
                if clave == "Requisitos previos":
                    inf.error(md.rel, i + 1, "«Requisitos previos» ahora se llama «Conviene saber antes»")
                    clave = "Conviene saber antes"
                if clave not in CABECERA:
                    inf.aviso(md.rel, i + 1, f"dato de la cabecera desconocido: «{clave}» (son {', '.join(CABECERA)})")
                vistos[clave] = (i, valor)
            i += 1
        for clave in CABECERA:
            if clave in CABECERA_OBLIGATORIA and clave not in vistos:
                inf.error(md.rel, desde + 1, f"falta «> **{clave}:**» en la cabecera del módulo")
        if "Tiempo estimado" in vistos:
            j, valor = vistos["Tiempo estimado"]
            if not re.fullmatch(r"1 hora|\d+(,\d+)? horas", valor) or valor in ("1 horas",):
                inf.error(md.rel, j + 1, f"«Tiempo estimado: {valor}» debe ser «1 hora», «1,5 horas», «5 horas»…")
        if "Nivel" in vistos:
            j, valor = vistos["Nivel"]
            if not re.fullmatch(r"(Básico|Intermedio|Avanzado) · (Núcleo|Ampliación)", valor):
                inf.error(md.rel, j + 1, f"«Nivel: {valor}» debe ser «Básico», «Intermedio» o «Avanzado», «·» y «Núcleo» o «Ampliación»")
        if "Conviene saber antes" in vistos:
            j, valor = vistos["Conviene saber antes"]
            partes = valor.split(" · ")
            if valor != "Nada" and not all(re.fullmatch(r"\[[^\]]+\]\([^)\s]+\)", p.strip()) for p in partes):
                inf.error(md.rel, j + 1, "«Conviene saber antes» debe ser «Nada» o enlaces a módulos separados por « · »")

    def comprobar_ejercicios(self, md, modulo, rango):
        inf = self.informe
        inicio, fin = rango
        dentro = [(i, n, t) for i, n, t in md.encabezados if inicio < i < fin]
        niveles, ejercicios = [], []
        for k, (i, nivel, t) in enumerate(dentro):
            if nivel == 3:
                if t not in NIVELES_EJERCICIOS:
                    inf.error(md.rel, i + 1, f"nivel de ejercicios desconocido: «### {t}» (son {', '.join(NIVELES_EJERCICIOS)})")
                else:
                    if niveles and NIVELES_EJERCICIOS.index(t) <= NIVELES_EJERCICIOS.index(niveles[-1]):
                        inf.error(md.rel, i + 1, f"el nivel «{t}» está fuera de orden o repetido")
                    niveles.append(t)
            elif nivel == 4:
                m = re.fullmatch(r"Ejercicio (\d+) · (.+)", t)
                if not m:
                    inf.error(md.rel, i + 1, f"«#### {t}» no es un ejercicio: debe ser «#### Ejercicio N · Título»")
                    continue
                final = next((j for j, n, _ in dentro[k + 1:] if n <= 4), fin)
                ejercicios.append((i, int(m.group(1)), m.group(2), final))
        for nivel in NIVELES_EJERCICIOS:
            if nivel not in niveles:
                inf.aviso(md.rel, inicio + 1, f"no hay ejercicios de nivel «{nivel}» (conviene que haya de los cuatro niveles)")
        if not ejercicios:
            inf.error(md.rel, inicio + 1, "la sección de ejercicios no tiene ningún «#### Ejercicio N · Título»")
        esperados = [e.get("titulo") for e in modulo.get("ejercicios", []) if isinstance(e, dict)]
        reales = [t for _, _, t, _ in ejercicios]
        for posicion, (i, n, titulo, final) in enumerate(ejercicios, 1):
            if n != posicion:
                inf.aviso(md.rel, i + 1, f"el ejercicio {n} es el {posicion}.º de la sección (N es su posición)")
            que = formato_en_titulo(titulo)
            if que:
                inf.error(md.rel, i + 1, f"el título del ejercicio {n} lleva formato Markdown ({que}); los títulos son texto plano")
            if titulo not in esperados:
                inf.error(md.rel, i + 1, f"el ejercicio {n}, «{titulo}», no está en curso.json (el título debe coincidir "
                                         "exactamente; si es nuevo, añádelo con su id)")
            self.comprobar_pistas_y_solucion(md, i, final, f"el ejercicio {n}")
        for titulo in esperados:
            if titulo not in reales:
                inf.error(md.rel, inicio + 1, f"falta el ejercicio «{titulo}» de curso.json")
        comunes = [t for t in reales if t in esperados]
        if comunes != [t for t in esperados if t in reales]:
            inf.error(md.rel, inicio + 1, "los ejercicios no están en el mismo orden que en curso.json")

    def comprobar_pistas_y_solucion(self, md, desde, hasta, que):
        inf = self.informe
        resumenes = recorrer_detalles(md, desde + 1, hasta)
        pistas = [(i, t) for i, t in resumenes if re.fullmatch(r"Pista \d+", t)]
        soluciones = [(i, t) for i, t in resumenes if t == "Ver solución"]
        if not soluciones:
            inf.error(md.rel, desde + 1, f"falta la solución de {que} («<summary>Ver solución</summary>» en un <details>)")
            return
        if len(soluciones) > 1:
            inf.error(md.rel, soluciones[1][0] + 1, f"{que} tiene más de una solución")
        if not pistas:
            inf.aviso(md.rel, desde + 1, f"{que} no tiene pistas (conviene darlas antes de la solución)")
        for i, t in pistas:
            if i > soluciones[0][0]:
                inf.error(md.rel, i + 1, f"en {que}, «{t}» está después de la solución (las pistas van antes)")
        for k, (i, t) in enumerate(pistas, 1):
            if t != f"Pista {k}":
                inf.aviso(md.rel, i + 1, f"en {que}, «{t}» debería ser «Pista {k}»")

    def comprobar_preguntas(self, md, rango):
        inf = self.informe
        inicio, fin = rango
        preguntas = [i for i in range(inicio + 1, fin) if not md.en_codigo[i] and re.match(r"^\d+\. \S", md.lineas[i])]
        if not preguntas:
            inf.error(md.rel, inicio + 1, "la sección de preguntas de repaso no tiene ninguna pregunta (una lista numerada)")
            return
        for k, i in enumerate(preguntas):
            final = preguntas[k + 1] if k + 1 < len(preguntas) else fin
            resumenes = recorrer_detalles(md, i, final)
            respuestas = [j for j, t in resumenes if t == "Ver respuesta"]
            if not respuestas:
                inf.error(md.rel, i + 1, f"la pregunta {k + 1} no tiene respuesta («<summary>Ver respuesta</summary>» en un <details>)")
            elif not any("](#" in md.lineas[j] for j in range(respuestas[0], final)):
                inf.aviso(md.rel, i + 1, f"la respuesta de la pregunta {k + 1} no enlaza al apartado donde se explica (conviene)")

    def comprobar_retos(self, md, fase):
        inf = self.informe
        primera = next((i for i, l in enumerate(md.lineas) if l.strip()), 0)
        m = re.match(r"^# Retos de la fase (\d{2}) — (.+?)\s*$", md.lineas[primera]) if md.lineas else None
        if not m:
            inf.error(md.rel, primera + 1, "la primera línea debe ser «# Retos de la fase NN — Título de la fase»")
        else:
            if m.group(2) != fase.get("titulo"):
                inf.error(md.rel, primera + 1, f"«{m.group(2)}» no es el título de la fase en curso.json («{fase.get('titulo')}»)")
            nf = CARPETA_FASE.match(str(fase.get("carpeta", "")))
            if nf and nf.group(1) != m.group(1):
                inf.aviso(md.rel, primera + 1, f"el número de fase {m.group(1)} no coincide con su carpeta ({nf.group(1)})")
        retos = [(i, t) for i, n, t in md.encabezados if n == 2]
        if not retos:
            inf.error(md.rel, primera + 1, "no hay ningún reto («## Reto N · Título»)")
        for k, (i, t) in enumerate(retos):
            mr = re.fullmatch(r"Reto (\d+) · (.+)", t)
            if not mr:
                inf.error(md.rel, i + 1, f"«## {t}» no es un reto: debe ser «## Reto N · Título»")
                continue
            que = formato_en_titulo(mr.group(2))
            if que:
                inf.error(md.rel, i + 1, f"el título del reto {mr.group(1)} lleva formato Markdown ({que}); los títulos son texto plano")
            if int(mr.group(1)) != k + 1:
                inf.aviso(md.rel, i + 1, f"el reto {mr.group(1)} es el {k + 1}.º del fichero (N es su posición)")
            final = retos[k + 1][0] if k + 1 < len(retos) else len(md.lineas)
            self.comprobar_pistas_y_solucion(md, i, final, f"el reto {mr.group(1)}")
        recorrer_detalles(md, 0, len(md.lineas), inf)

    def comprobar_indice(self):
        if not (self.raiz / "00-indice.md").is_file():
            return
        md = self.leer("00-indice.md")
        fases = [(i, t) for i, n, t in md.encabezados if n == 2 and t.startswith("Fase ")]
        for i, t in fases:
            if not re.fullmatch(r"Fase \d{2} — .+", t):
                self.informe.error(md.rel, i + 1, f"«## {t}» debe ser «## Fase NN — Título»")
        reales = [re.sub(r"^Fase \d{2} — ", "", t) for _, t in fases]
        esperados = [f.get("titulo") for f in self.fases]
        if reales != esperados:
            self.informe.error(md.rel, 0, "las fases del índice no coinciden con curso.json (regenera el índice): "
                                          f"tiene {reales}, y curso.json {esperados}")

    def comprobar_glosario(self):
        """Letras y términos en orden alfabético español (la ñ, entre la n y la o), cada término en su letra y
        ningún término ni ninguna letra repetidos (FORMATO.md, apartado 9: los términos se definen una vez)."""
        md = self.leer("glosario.md")
        letra, anterior, letra_anterior = None, "", ""
        letras, terminos = {}, {}
        for i, n, t in md.encabezados:
            if n == 2:
                clave_letra = orden_alfabetico(t)
                if clave_letra in letras:
                    self.informe.aviso(md.rel, i + 1, f"la letra «{t}» está repetida (ya está en la línea {letras[clave_letra]})")
                elif clave_letra < letra_anterior:
                    self.informe.aviso(md.rel, i + 1, f"la letra «{t}» no está en orden alfabético")
                letras.setdefault(clave_letra, i + 1)
                letra, anterior, letra_anterior = t, "", clave_letra
            elif n == 3:
                clave = orden_alfabetico(t)
                if clave in terminos:
                    self.informe.error(md.rel, i + 1, f"el término «{t}» está repetido (ya está en la línea {terminos[clave]}): "
                                                      "cada término se define una vez")
                    continue
                terminos[clave] = i + 1
                if letra and not clave.startswith(orden_alfabetico(letra)):
                    self.informe.aviso(md.rel, i + 1, f"el término «{t}» no empieza por la letra de su sección («{letra}»)")
                if clave < anterior:
                    self.informe.aviso(md.rel, i + 1, f"el término «{t}» no está en orden alfabético")
                anterior = clave

    # -- todos los Markdown: enlaces, imágenes, Mermaid, HTML y huecos -----------------------------------

    # -- codigo/ como lo recibirá el alumno ---------------------------------------------------------
    # Un clon (y la academia, que instala desde un commit) solo recibe lo que guarda Git: ni carpetas vacías,
    # ni más permisos que «ejecutable o no», y los saltos de línea según .gitattributes. Todo son avisos: el
    # fallo real lo da verificar_codigo.py --commit, que verifica una copia como la de un clon.

    def git(self, *argumentos):
        """La salida de una orden de Git en la raíz del curso, o None si no hay Git o no es un repositorio."""
        try:
            return subprocess.run(["git", "-C", str(self.raiz), *argumentos], capture_output=True, text=True,
                                  check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            return None

    def comprobar_codigo_en_git(self):
        """Saltos de línea, carpetas vacías y permisos de los ficheros de codigo/ (FORMATO.md, apartado 7)."""
        salida = self.git("ls-files", "--eol", "-z", "--cached", "--others", "--exclude-standard")
        anidados = set()                                        # repositorios que Git guarda como submódulo
        if salida is None:                                      # sin Git: solo el disco
            presentes = [p.relative_to(self.raiz).as_posix() for p in sorted(self.raiz.rglob("*"))
                         if p.is_file() and en_codigo(p.relative_to(self.raiz).as_posix())]
            for rel in presentes:
                self.aviso_crlf(rel, sin_git=True)
            modos = {}
        else:
            presentes = self.comprobar_saltos_de_linea(salida)
            modos = {}                                          # ruta → ¿Git la guarda como ejecutable?
            for entrada in filter(None, (self.git("ls-files", "-s", "-z") or "").split("\0")):
                datos, _, rel = entrada.partition("\t")
                modos[rel] = datos.split()[0] == "100755"
                if datos.split()[0] == "160000" and en_codigo(rel + "/x"):
                    anidados.add(rel)
        self.comprobar_repositorios_anidados(anidados)
        self.comprobar_carpetas_vacias(set(presentes))
        self.comprobar_env(presentes)
        if os.name != "nt":                                     # en Windows el disco no tiene esos permisos
            lanzados = self.comprobar_lanzados_con_punto(presentes, modos)
            self.comprobar_permisos(presentes, modos, lanzados, salida is not None)

    def comprobar_repositorios_anidados(self, anidados):
        """Una carpeta .git dentro de codigo/ (FORMATO.md, apartado 7): Git no guarda su contenido, así que en un clon
        (y en la academia) el ejemplo llega vacío o como un submódulo. Error: los repositorios se crean en la sesión."""
        for p in self.raiz.rglob(".git"):
            rel = p.relative_to(self.raiz).as_posix()
            if en_codigo(rel) and ".git" not in Path(rel).parts[:-1]:
                anidados.add(Path(rel).parent.as_posix())
        for carpeta in sorted(anidados):
            self.informe.error(carpeta + "/", 0, "un repositorio de Git dentro de codigo/ (una carpeta .git, o un "
                                                 "submódulo): Git no guarda su contenido, así que no llega a un clon ni "
                                                 "a la academia. Quita la carpeta .git y crea el repositorio dentro de "
                                                 "la sesión (git init) (FORMATO.md, apartado 7)")

    def comprobar_env(self, presentes):
        """Los .env de codigo/ (FORMATO.md, apartado 7): un .env real, error (la academia solo admite .env.example y
        excluye los demás; y puede llevar secretos); uno que Git ignora, aviso (no llega a un clon ni a la academia,
        pero está en el disco). En .env.example, aviso por cada valor con pinta de secreto real."""
        guardados = set(presentes)
        en_disco = {p.relative_to(self.raiz).as_posix() for p in self.raiz.rglob(".env*")
                    if p.is_file() and en_codigo(p.relative_to(self.raiz).as_posix())}
        for rel in sorted(guardados | en_disco):
            nombre = Path(rel).name.lower()
            if nombre != ".env" and not nombre.startswith(".env."):
                continue
            if nombre == ENV_EJEMPLO:
                if Path(rel).name != ENV_EJEMPLO:
                    self.informe.error(rel, 0, f"se llama «{Path(rel).name}»: la academia solo admite «{ENV_EJEMPLO}», "
                                               "en minúsculas")
                else:
                    self.comprobar_env_ejemplo(rel)
            elif rel in guardados:
                self.informe.error(rel, 0, f"un {Path(rel).name} real en codigo/: la academia solo admite {ENV_EJEMPLO} "
                                           "(excluye los demás) y puede llevar secretos. Renómbralo a .env.example, con "
                                           "valores de ejemplo, o, si el ejemplo necesita el .env, créalo en la sesión "
                                           "(cp .env.example .env)")
            else:
                self.informe.aviso(rel, 0, f"un {Path(rel).name} en codigo/ que Git ignora: no llega a un clon ni a la "
                                           f"academia, pero está en tu disco; si el ejemplo lo necesita, créalo en la "
                                           f"sesión desde {ENV_EJEMPLO}")

    def comprobar_env_ejemplo(self, rel):
        try:
            lineas = (self.raiz / rel).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return
        for n, linea in enumerate(lineas, 1):
            m = ENV_LINEA.match(linea)
            if not m:
                continue
            variable, valor = m.group(1), m.group(2).strip()
            if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "'\"":
                valor = valor[1:-1]
            elif " #" in valor:
                valor = valor.split(" #", 1)[0].rstrip()
            que = secreto_real(variable, valor)
            if que:
                self.informe.aviso(rel, n, f"{variable} tiene pinta de secreto real ({que}): en un .env.example van "
                                           "valores de ejemplo que se vean falsos (cambia-esto, tu-clave-aqui, vacío…), "
                                           "nunca uno de verdad; si lo era, anúlalo donde se creó")

    def comprobar_saltos_de_linea(self, salida):
        """Con CRLF, bash falla ($'\\r': orden no encontrada) y grep, cut o read ven un \\r al final de cada línea.
        Dos avisos: un fichero con CRLF en lo que guarda Git (o, si no es suyo todavía, en lo que guardaría), y
        ficheros que no saldrían con LF en un clon con core.autocrlf=true (lo normal en Git for Windows), porque
        al curso le falta «* text=auto eol=lf» en su .gitattributes. Los marcados con -text no avisan.
        Devuelve los ficheros de codigo/ que Git guarda o guardaría."""
        presentes, sin_lf = [], []
        for entrada in filter(None, salida.split("\0")):
            datos, _, rel = entrada.partition("\t")
            if not en_codigo(rel):
                continue
            presentes.append(rel)
            campos = dict(c.split("/", 1) for c in datos.split()[:2])        # i/… (índice) y w/… (disco)
            atributos = datos.split("attr/", 1)[1].split() if "attr/" in datos else []
            if "-text" in atributos:
                continue                                                    # CRLF a propósito, o binario
            texto = any(a == "text" or a.startswith("text=") for a in atributos)
            # Lo que guarda Git: el índice, y lo del disco si Git no lo va a normalizar al añadirlo
            guardado = ([campos.get("i")] if campos.get("i") else []) + ([] if texto else [campos.get("w")])
            if {"crlf", "mixed"} & set(guardado):
                self.aviso_crlf(rel)
            if "eol=lf" not in atributos and {"lf", "crlf", "mixed"} & {campos.get("i"), campos.get("w")}:
                sin_lf.append(rel)
        if sin_lf:
            ejemplo = sin_lf[0] + (f" y {len(sin_lf) - 1} más" if len(sin_lf) > 1 else "")
            self.informe.aviso(".gitattributes", 0,
                               f"algún fichero de texto de codigo/ no saldría con LF en un clon en Windows ({ejemplo}): "
                               "con core.autocrlf=true, lo normal en Git for Windows, se rompen los scripts y los datos "
                               "que leen; añade «* text=auto eol=lf» al .gitattributes del curso, como el de la plantilla "
                               "del kit (FORMATO.md, apartado 7)")
        return presentes

    def aviso_crlf(self, rel, sin_git=False):
        """Avisa de que rel tiene CRLF, con la primera línea que lo tiene en el disco. Sin Git, lo mira en el disco."""
        try:
            datos = (self.raiz / rel).read_bytes()
        except OSError:
            datos = b""
        if sin_git and (b"\0" in datos[:8000] or b"\r\n" not in datos):
            return                                                          # binario, o sin CRLF
        linea = datos[:datos.find(b"\r\n")].count(b"\n") + 1 if b"\r\n" in datos else 0
        self.informe.aviso(rel, linea, "saltos de línea CRLF (de Windows): con ellos bash falla ($'\\r': orden no "
                                       "encontrada) y grep, cut o read ven un \\r al final de cada línea. Guárdalo con LF "
                                       "(en VS Code, «CRLF» abajo a la derecha) o, con «* text=auto eol=lf» en "
                                       ".gitattributes, «git add --renormalize .»; si es a propósito, márcalo con -text "
                                       "en .gitattributes (FORMATO.md, apartado 7)")

    def comprobar_carpetas_vacias(self, presentes):
        """Git no guarda carpetas: una carpeta de codigo/ sin ningún fichero que Git guarde (vacía, o con todo
        ignorado) no existe en un clon. Se avisa solo de la de más arriba."""
        con_algo = {"/".join(Path(rel).parts[:n]) for rel in presentes for n in range(1, len(Path(rel).parts))}
        avisadas = []
        for carpeta in sorted(p for p in self.raiz.rglob("*") if p.is_dir()):
            rel = carpeta.relative_to(self.raiz).as_posix()
            if not en_codigo(rel + "/x") or rel in con_algo or any(rel.startswith(a + "/") for a in avisadas):
                continue
            if ".git" in Path(rel).parts or ".verificacion" in Path(rel).parts:
                continue
            avisadas.append(rel)
            self.informe.aviso(rel + "/", 0,
                               "carpeta que no existirá en un clon del curso: Git no guarda las carpetas vacías (ni las "
                               "que solo tienen ficheros ignorados). Mejor, créala dentro de la sesión (mkdir); si no, "
                               "pon dentro un fichero .gitkeep, sabiendo que ls -a, find y du lo muestran y que un "
                               "rmdir de esa carpeta fallaría porque no está vacía (FORMATO.md, apartado 7)")

    def ejecutable(self, rel, modos):
        """Si Git guarda rel como ejecutable (o, si no es suyo todavía, si lo es en el disco)."""
        if rel in modos:
            return modos[rel]
        try:
            return bool((self.raiz / rel).stat().st_mode & 0o100)
        except OSError:
            return True

    def comprobar_lanzados_con_punto(self, presentes, modos):
        """Un script que una sesión lanza con ./ necesita el permiso de ejecución, y en un clon solo lo tiene si Git
        lo guarda así. Si la sesión hace un chmod de ese fichero (antes o después), es lo que enseña: no avisa.
        En las sesiones encadenadas (sesion-1.txt, sesion-2.txt…), vale el chmod de cualquiera de la cadena: se
        teclean en la misma terminal. Devuelve los scripts de los que ha avisado."""
        avisados = set()

        def texto(rel):
            try:
                return (self.raiz / rel).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                return ""

        for sesion in (rel for rel in presentes if re.fullmatch(r"sesion(-[\w-]+)?\.txt", Path(rel).name)):
            carpeta = Path(sesion).parent
            try:
                lineas = (self.raiz / sesion).read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for n, linea in enumerate(lineas, 1):
                if not linea.strip() or linea.lstrip().startswith("#"):
                    continue
                for nombre in re.findall(r"(?:^|&&|\|\||[;|(])\s*\./([^\s;&|<>()]+)", linea):
                    rel = (carpeta / nombre).as_posix()
                    if rel not in presentes or self.ejecutable(rel, modos):
                        continue                                    # lo crea la sesión, o ya es ejecutable
                    cadena = [r for r in presentes if Path(r).parent == carpeta and re.fullmatch(r"sesion-\d+\.txt", Path(r).name)]
                    tratado = "\n".join(lineas if sesion not in cadena else [texto(r) for r in cadena])
                    if re.search(r"\bchmod\b[^\n]*" + re.escape(Path(nombre).name), tratado):
                        continue                    # la sesión trata sus permisos (p. ej., enseña «Permiso denegado»)
                    avisados.add(rel)
                    self.informe.aviso(sesion, n,
                                       f"«./{nombre}» necesita permiso de ejecución y {rel} no lo tiene en lo que guarda "
                                       "Git: en un clon saldría «Permiso denegado». Dáselo con «git update-index "
                                       f"--chmod=+x {rel}» (o «chmod +x» y «git add»), o haz el chmod dentro de la sesión "
                                       "(FORMATO.md, apartado 7)")
        return avisados

    def comprobar_permisos(self, presentes, modos, lanzados, con_git):
        """Git solo guarda si un fichero es ejecutable o no: un clon lo tendrá con lectura y escritura para su
        propietario. Se miran solo los permisos del propietario (los del grupo dependen de cada equipo)."""
        mira_ejecucion = con_git and (self.git("config", "--bool", "core.fileMode") or "true").strip() != "false"
        for rel in presentes:
            try:
                modo = (self.raiz / rel).stat().st_mode
            except OSError:
                continue
            if not (modo & 0o400 and modo & 0o200):
                self.informe.aviso(rel, 0, "en el disco no tiene permiso de lectura o de escritura para su propietario, "
                                           "y Git no guarda eso: en un clon tendrá los dos. Si el ejemplo necesita otros "
                                           "permisos, ponlos con chmod dentro de la sesión (FORMATO.md, apartado 7)")
            elif mira_ejecucion and rel in modos and rel not in lanzados and bool(modo & 0o100) != modos[rel]:
                que = ("es ejecutable en el disco y Git lo guarda sin permiso de ejecución" if modo & 0o100 else
                       "no es ejecutable en el disco y Git lo guarda como ejecutable")
                self.informe.aviso(rel, 0, f"{que}: un clon lo tendrá como lo guarda Git; haz el commit del permiso "
                                           "(git add) o ponlo como estaba (FORMATO.md, apartado 7)")

    def markdown_del_curso(self):
        for ruta in sorted(self.raiz.rglob("*.md")):
            rel = ruta.relative_to(self.raiz)
            if CARPETAS_IGNORADAS & set(rel.parts[:-1]) or rel.as_posix() in FICHEROS_DE_TRABAJO:
                continue
            yield self.leer(rel)

    def comprobar_markdown(self):
        for md in self.markdown_del_curso():
            if md.sin_cerrar is not None:
                self.informe.error(md.rel, md.sin_cerrar + 1, "bloque de código sin cerrar")
            for i in range(len(md.lineas)):
                linea = md.texto_sin_codigo(i)
                if not linea:
                    continue
                for k, m in enumerate(ENLACE.finditer(linea)):
                    self.comprobar_enlace(md, i, m.group(1) == "!", m.group(2), m.group(3))
                    if k == 0 and md.lineas[i].startswith(ENLACE_CODIGO):
                        # El texto, tal cual (en linea, el código en línea está tapado con espacios)
                        self.comprobar_enlace_de_codigo(md, i, md.lineas[i][m.start(2):m.end(2)], m.group(3))
                self.comprobar_html(md, i, linea)
                if TAREA.match(linea):
                    self.informe.aviso(md.rel, i + 1, "lista de tareas (- [ ] / - [x]): la academia todavía no las dibuja "
                                                      "(se ve «[ ]» como texto); fuera de un bloque de código, usa una "
                                                      "lista normal")
                sin_destinos = ENLACE.sub(lambda m: m.group(1) + "[" + m.group(2) + "]" + " " * (len(m.group(0)) - len(m.group(2)) - 2 - len(m.group(1))), linea)
                for m in CORREO_SUELTO.finditer(sin_destinos):
                    self.informe.aviso(md.rel, i + 1, f"{m.group(0)} fuera de código: GitHub lo convierte en un enlace "
                                                      f"mailto: (la academia lo deja como texto), y {AVISO_CORREO}")
                for m in CORREO_AUTOMATICO.finditer(linea):
                    self.informe.aviso(md.rel, i + 1, f"{m.group(0)} fuera de código: CommonMark y GitHub lo "
                                                      f"convierten en un enlace mailto:, y {AVISO_CORREO}")
            for inicio, fin, lenguaje in md.bloques:
                if lenguaje == "mermaid":
                    self.comprobar_mermaid(md, inicio, fin)
            for i, l in enumerate(md.lineas):
                if RELLENAR.search(l):
                    self.informe.aviso(md.rel, i + 1, "queda un hueco de la plantilla sin rellenar ([RELLENAR: …])")
        for i, l in enumerate(self.texto_json.split("\n")):
            if RELLENAR.search(l):
                self.aviso_json(i + 1, "queda un hueco de la plantilla sin rellenar ([RELLENAR: …])")

    def comprobar_enlace(self, md, i, imagen, texto, destino):
        inf = self.informe
        if imagen:
            if destino.startswith("data:"):
                inf.error(md.rel, i + 1, "imagen incrustada (data:): guárdala como fichero en img/")
                return
            if re.match(r"^[a-z]+:", destino):
                inf.error(md.rel, i + 1, f"imagen de otra web ({destino}): guárdala en la carpeta img/ de la fase")
                return
            if not texto.strip():
                inf.error(md.rel, i + 1, f"la imagen {destino} no tiene texto alternativo: ![descripción]({destino})")
            if Path(destino).suffix.lower() not in IMAGENES:
                inf.error(md.rel, i + 1, f"imagen {destino}: solo se admiten PNG, JPG o SVG")
        if destino.lower().startswith("mailto:"):
            self.informe.aviso(md.rel, i + 1, f"enlace a {destino}: {AVISO_CORREO}")
            return
        if not destino:
            return
        if re.match(r"^https?://", destino):
            self.comprobar_enlace_externo(md, i, destino)
            return
        if re.match(r"^[a-z]+:", destino):
            inf.aviso(md.rel, i + 1, f"enlace con un esquema poco habitual: {destino}")
            return
        ruta, _, seccion = destino.partition("#")
        ruta = unquote(ruta)
        objetivo = (md.ruta.parent / ruta).resolve() if ruta else md.ruta
        try:
            rel = objetivo.relative_to(self.raiz.resolve()).as_posix()
        except ValueError:
            inf.error(md.rel, i + 1, f"el enlace {destino} sale del curso: a otro curso se enlaza con su dirección de GitHub "
                                     "(FORMATO.md, apartado 10.2)")
            return
        if imagen and not objetivo.exists():
            inf.error(md.rel, i + 1, f"no existe la imagen {destino}")
            return
        if imagen:
            if "img" not in Path(rel).parts:
                inf.aviso(md.rel, i + 1, f"la imagen {destino} conviene que esté en la carpeta img/ de la fase")
            return
        self.comprobar_destino(md, i, destino, objetivo, rel, unquote(seccion))

    def comprobar_enlace_de_codigo(self, md, i, texto, destino):
        """El texto de un «📁 **Código:**» y su destino deben ser la misma carpeta (FORMATO.md, apartado 7): la
        academia puede dar el ZIP del proyecto entero, pero el texto dice la carpeta del enlace."""
        visible = texto.strip().strip("`").strip()
        if not visible or not destino or re.match(r"^[a-z]+:", destino):
            return
        if posixpath.normpath(visible) != posixpath.normpath(unquote(destino.partition("#")[0])):
            self.informe.aviso(md.rel, i + 1, f"«📁 Código»: el texto dice «{visible}» y el enlace lleva a «{destino}» "
                                              "(deben ser la misma carpeta)")

    def comprobar_destino(self, md, i, destino, objetivo, rel, seccion, otro_curso=None):
        inf = self.informe
        if not objetivo.exists():
            previstos = self.previstos if otro_curso is None else previstos_de(objetivo, rel)
            if rel in previstos:
                retos = rel.endswith("/retos.md")
                que = "a unos retos pendientes" if retos else "a un módulo pendiente"
                campo = "retos_disponibles" if retos else "disponible"
                inf.aviso(md.rel, i + 1, f"enlace {que} (\"{campo}\": false en curso.json"
                                         + (f" de {otro_curso}" if otro_curso else "") + f"): {destino}"
                                         + (f"; su ancla #{seccion} no se podrá comprobar hasta que esté escrito" if seccion else ""))
            else:
                inf.error(md.rel, i + 1, f"no existe {destino}" + (f" (en {otro_curso})" if otro_curso else "")
                                         + (" y no es ningún módulo previsto en curso.json"
                                            if rel.endswith(".md") and rel.startswith("fase-") else ""))
            return
        if seccion and objetivo.suffix == ".md" and objetivo.is_file():
            if otro_curso is None:
                destino_md = self.leer(rel)
            else:
                destino_md = Markdown(objetivo, rel)
            if seccion not in destino_md.anclas():
                inf.error(md.rel, i + 1, f"no existe la sección #{seccion} en {rel}" + (f" de {otro_curso}" if otro_curso else ""))

    def comprobar_enlace_externo(self, md, i, destino):
        inf = self.informe
        m = GITHUB.match(destino)
        if not m:
            return
        cuenta, repositorio, modo, rama, ruta, seccion = m.groups()
        propio = str(self.datos.get("repositorio", "")).rstrip("/")
        es_propio = propio.lower() == f"https://github.com/{cuenta}/{repositorio}".lower()
        hermana = self.raiz.resolve().parent / repositorio
        es_curso = es_propio or cuenta.lower() == "myopenacademy" or (hermana / "curso.json").is_file()
        if not es_curso or not modo:
            return
        if rama != "main":
            inf.error(md.rel, i + 1, f"el enlace {destino} debe apuntar a la rama main")
            return
        if es_propio:
            inf.aviso(md.rel, i + 1, f"el enlace {destino} es a este mismo curso: usa un enlace relativo")
            base, nombre = self.raiz.resolve(), "este curso"
        elif hermana.is_dir():
            base, nombre = hermana, f"../{repositorio}/"
        else:
            inf.aviso(md.rel, i + 1, f"no he podido revisar {destino}: no está la carpeta hermana ../{repositorio}/")
            return
        ruta = unquote((ruta or "").lstrip("/"))
        objetivo = (base / ruta).resolve()
        self.comprobar_destino(md, i, destino, objetivo, ruta or ".", unquote(seccion or ""),
                               otro_curso=None if es_propio else nombre)

    def comprobar_html(self, md, i, linea):
        inf = self.informe
        for m in ETIQUETA.finditer(linea):
            cierre, nombre, atributos = m.group(1), m.group(2).lower(), m.group(3)
            if cierre:
                continue
            pares = re.findall(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)(?:\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+)))?", atributos)
            attrs = {a.lower(): (v1 or v2 or v3) for a, v1, v2, v3 in pares}
            if nombre in HTML_ADMITIDO:
                raros = [a for a, v in attrs.items() if a not in ATRIBUTOS_ADMITIDOS.get(nombre, set())
                         or (nombre == "code" and not re.fullmatch(r"language-[a-z0-9+#-]+", v or ""))]
                if raros:
                    inf.error(md.rel, i + 1, f"<{nombre}> con atributos que la academia no admite ({', '.join(raros)}): "
                                             "hace fallar la instalación")
            elif nombre == "a":
                raros = [a for a in attrs if a != "href"]
                if raros:
                    inf.error(md.rel, i + 1, f"<a> con atributos que la academia no admite ({', '.join(raros)}): "
                                             "hace fallar la instalación")
                else:
                    inf.aviso(md.rel, i + 1, "<a>: la academia quita los enlaces escritos en HTML; usa [texto](destino)")
            elif nombre in HTML_INERTE:
                if attrs:
                    inf.error(md.rel, i + 1, f"<{nombre}> con atributos ({', '.join(attrs)}): hace fallar la instalación")
                else:
                    inf.aviso(md.rel, i + 1, f"<{nombre}>: la academia quita esta etiqueta al instalar y deja su texto "
                                             "(escríbelo en Markdown)")
            else:
                pista = " (las imágenes van con ![texto](img/…))" if nombre in {"img", "picture", "svg"} else ""
                inf.error(md.rel, i + 1, f"<{nombre}> no se admite: hace fallar la instalación{pista}")

    def comprobar_mermaid(self, md, inicio, fin):
        inf = self.informe
        cuerpo = list(range(inicio + 1, fin))
        primera = next((j for j in cuerpo if md.lineas[j].strip()), None)
        if primera is not None and md.lineas[primera].strip() == "---":
            inf.error(md.rel, primera + 1, "diagrama Mermaid con frontmatter (---): la academia lo mostraría como código")
        for j in cuerpo:
            linea = md.lineas[j]
            if "%%{" in linea:
                inf.error(md.rel, j + 1, "diagrama Mermaid con directivas (%%{ … }%%): no se admiten")
            if re.match(r"^\s*click\s", linea):
                inf.error(md.rel, j + 1, "diagrama Mermaid con interacciones (click): no se admiten")
            if "url(" in linea or "@import" in linea:
                inf.error(md.rel, j + 1, "diagrama Mermaid con url() o @import: no se admiten")
            if re.search(r"<img\b", linea, re.I):
                inf.error(md.rel, j + 1, "diagrama Mermaid con imágenes: no se admiten")
            if re.search(r"<\s*/?\s*(b|i|strong|em)\s*>", linea, re.I) or any(
                    re.search(r"\*\*|__|\*[^*\s]([^*]*[^*\s])?\*|(^|\s)_[^_\s]([^_]*[^_\s])?_(\s|$)", etiqueta)
                    for etiqueta in etiquetas_mermaid(linea)):
                inf.error(md.rel, j + 1, "diagrama Mermaid con negrita o cursiva en una etiqueta: no se admiten")
            for e in ENTIDAD.finditer(linea):
                if e.group(1) not in ENTIDADES_MERMAID:
                    inf.error(md.rel, j + 1, f"diagrama Mermaid con la entidad &{e.group(1)};: solo se admiten "
                                             "&quot; &lt; &gt; y &amp;")


# --------------------------------------------------------------------------------------------------

def argumentos(argv):
    ayuda = __doc__.strip()
    rutas = []
    for a in argv:
        if a in ("-h", "--help"):
            print(ayuda)
            sys.exit(0)
        if a.startswith("-"):
            print(f"Opción desconocida: {a}\n\nUso: python3 formato_academia.py [carpeta del curso]   (--help para la ayuda)",
                  file=sys.stderr)
            sys.exit(2)
        rutas.append(a)
    if len(rutas) > 1:
        print("Indica una sola carpeta de curso.", file=sys.stderr)
        sys.exit(2)
    raiz = Path(rutas[0] if rutas else ".")
    if not raiz.is_dir():
        print(f"No existe la carpeta {raiz}: no se ha revisado nada.", file=sys.stderr)
        sys.exit(2)
    return raiz


def comprobar(raiz):
    """Comprueba el curso de la carpeta raiz y devuelve (informe, resumen)."""
    informe = Informe()
    curso = Curso(raiz.resolve(), informe)
    if not curso.cargar():
        return informe, "No se ha podido leer curso.json: no se ha revisado nada más."
    curso.comprobar_json()
    publicados = curso.comprobar_publicados()
    curso.comprobar_estructura()
    curso.comprobar_modulos()
    curso.comprobar_indice()
    curso.comprobar_markdown()
    curso.comprobar_codigo_en_git()
    modulos = [m for f in curso.fases for m in f.get("_modulos", [])]
    disponibles = sum(1 for m in modulos if m.get("_disponible"))
    ejercicios = sum(len(m.get("ejercicios", [])) for m in modulos if isinstance(m.get("ejercicios"), list))
    def plural(n, uno, varios):
        return f"{n} {uno if n == 1 else varios}"
    resumen = (f"Curso «{curso.datos.get('id')}» {curso.datos.get('version')}: {plural(len(curso.fases), 'fase', 'fases')}, "
               f"{plural(len(modulos), 'módulo', 'módulos')} ({disponibles} disponible{'' if disponibles == 1 else 's'}), "
               f"{plural(ejercicios, 'ejercicio', 'ejercicios')}; {publicados}.")
    return informe, resumen


def main():
    raiz = argumentos(sys.argv[1:])
    informe, resumen = comprobar(raiz)
    informe.imprimir(resumen)
    sys.exit(1 if informe.errores else 0)


if __name__ == "__main__":
    main()
