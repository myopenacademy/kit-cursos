"""Pruebas de formato_academia.py.

Cada prueba copia el curso de ejemplo bueno (cursos/bueno/) a una carpeta temporal, lo estropea de una
forma concreta y comprueba que formato_academia.py da justo ese error o ese aviso.

Desde la raíz del kit:
    python3 -m unittest discover -s herramientas/pruebas -v
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
HERRAMIENTAS = PRUEBAS.parent
sys.path.insert(0, str(HERRAMIENTAS))
sys.path.insert(0, str(HERRAMIENTAS / "nucleo"))
import formato_academia  # noqa: E402
import generar_indice  # noqa: E402

BUENO = PRUEBAS / "cursos" / "bueno"
DESTINO = PRUEBAS / "cursos" / "ejemplo-destino"
ENLACE_DESTINO = "https://github.com/myopenacademy/ejemplo-destino/blob/main/"
MODULO = "fase-01-primeros-pasos/01-ficheros-json.md"
RETOS = "fase-01-primeros-pasos/retos.md"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="formato-academia-"))
        self.raiz = self.tmp / "curso-ejemplo"
        shutil.copytree(BUENO, self.raiz)
        shutil.copytree(DESTINO, self.tmp / "ejemplo-destino")     # el otro curso, en su carpeta hermana

    def tearDown(self):
        shutil.rmtree(self.tmp)

    # -- cambiar el curso ---------------------------------------------------------------------------

    def json(self):
        return json.loads((self.raiz / "curso.json").read_text(encoding="utf-8"))

    def guardar_json(self, datos):
        (self.raiz / "curso.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    def cambiar(self, rel, antes, despues):
        ruta = self.raiz / rel
        texto = ruta.read_text(encoding="utf-8")
        self.assertIn(antes, texto, f"la prueba está mal: no encuentro «{antes}» en {rel}")
        ruta.write_text(texto.replace(antes, despues, 1), encoding="utf-8")

    def escribir(self, rel, texto):
        ruta = self.raiz / rel
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")

    def modulo(self, datos):
        return datos["fases"][0]["modulos"][0]

    def regenerar_indice(self):
        texto, _, _ = generar_indice.generar(self.raiz)
        (self.raiz / "00-indice.md").write_text(texto, encoding="utf-8")

    # -- comprobar ----------------------------------------------------------------------------------

    def comprobar(self):
        informe, _ = formato_academia.comprobar(self.raiz)
        self.errores = [f"{f}:{l}: {m}" for f, l, m in informe.errores]
        self.avisos = [f"{f}:{l}: {m}" for f, l, m in informe.avisos]

    def hay(self, lista, *trozos):
        return any(all(t in linea for t in trozos) for linea in lista)

    def assertError(self, *trozos):
        self.comprobar()
        self.assertTrue(self.hay(self.errores, *trozos), f"falta el error {trozos}; errores: {self.errores}")

    def assertAviso(self, *trozos):
        self.comprobar()
        self.assertTrue(self.hay(self.avisos, *trozos), f"falta el aviso {trozos}; avisos: {self.avisos}")

    def assertSinErrores(self):
        self.comprobar()
        self.assertEqual(self.errores, [])


class CursoBueno(Base):
    def test_el_curso_bueno_no_tiene_errores(self):
        self.assertSinErrores()

    def test_solo_los_avisos_esperados(self):
        self.comprobar()
        self.assertEqual(len(self.avisos), 2, self.avisos)
        self.assertTrue(all("no he podido revisar" in a or "módulo pendiente" in a for a in self.avisos), self.avisos)


class CursoJson(Base):
    def test_sin_curso_json(self):
        (self.raiz / "curso.json").unlink()
        self.assertError("curso.json", "no existe")

    def test_json_mal_escrito_dice_la_linea(self):
        self.cambiar("curso.json", '"tipo": "curso",', '"tipo": "curso"')
        self.assertError("curso.json:4:", "no es un JSON válido")

    def test_version_del_formato_desconocida(self):
        d = self.json(); d["formato"] = 2; self.guardar_json(d)
        self.assertError("solo conoce", "actualiza el kit")

    def test_tipo_distinto_de_curso(self):
        d = self.json(); d["tipo"] = "pack"; self.guardar_json(d)
        self.assertError("«tipo» debe ser")

    def test_id_del_curso_mal_formado(self):
        d = self.json(); d["id"] = "Mi Curso"; self.guardar_json(d)
        self.assertError("el «id» del curso")

    def test_falta_un_campo_obligatorio(self):
        d = self.json(); del d["descripcion"]; self.guardar_json(d)
        self.assertError("falta el campo «descripcion»")

    def test_version_que_no_es_semver(self):
        d = self.json(); d["version"] = "1.0"; self.guardar_json(d)
        self.assertError("MAYOR.MENOR.PARCHE")

    def test_campo_desconocido_es_aviso(self):
        d = self.json(); d["fases"][0]["retos_disponible"] = False; self.guardar_json(d)
        self.assertAviso("campo desconocido «retos_disponible»")

    def test_identificador_sin_el_prefijo_del_curso(self):
        d = self.json(); self.modulo(d)["id"] = "otro.ficheros-json"; self.guardar_json(d)
        self.assertError("«otro.ficheros-json» debe ser «ejemplo.»")

    def test_identificador_repetido(self):
        d = self.json(); d["fases"][0]["modulos"][1]["id"] = "ejemplo.ficheros-json"; self.guardar_json(d)
        self.assertError("«ejemplo.ficheros-json» ya lo usa")

    def test_transicion_desconocida(self):
        d = self.json(); d["transicion"] = ["sin-chuleta"]; self.guardar_json(d)
        self.assertError("«transicion»: «sin-chuleta» no existe")

    def test_parte_con_una_fase_que_no_existe(self):
        d = self.json(); d["partes"][0]["fases"] = ["ejemplo.fase.otra"]; self.guardar_json(d)
        self.assertError("la fase «ejemplo.fase.otra» no existe")


class Titulos(Base):
    def test_titulo_de_modulo_con_formato_en_curso_json(self):
        d = self.json(); self.modulo(d)["titulo"] = "Ficheros `JSON`"; self.guardar_json(d)
        self.assertError("curso.json", "formato Markdown", "comillas invertidas")

    def test_titulo_de_ejercicio_con_cursiva(self):
        self.cambiar(MODULO, "#### Ejercicio 2 · La coma de más", "#### Ejercicio 2 · La *coma* de más")
        d = self.json(); self.modulo(d)["ejercicios"][1]["titulo"] = "La *coma* de más"; self.guardar_json(d)
        self.assertError(MODULO, "el título del ejercicio 2 lleva formato Markdown")

    def test_titulo_del_curso_con_negrita(self):
        d = self.json(); d["titulo"] = "Curso **de ejemplo**"; self.guardar_json(d)
        self.assertError("el título del curso lleva formato Markdown")

    def test_guion_bajo_dentro_de_una_palabra_no_es_formato(self):
        self.assertIsNone(formato_academia.formato_en_titulo("Configura JAVA_HOME"))
        self.assertIsNotNone(formato_academia.formato_en_titulo("El método __init__"))
        self.assertIsNotNone(formato_academia.formato_en_titulo("Un _poco_ de cursiva"))

    def test_titulo_del_modulo_distinto_de_curso_json(self):
        self.cambiar(MODULO, "# 01.01 Ficheros JSON", "# 01.01 Ficheros de JSON")
        self.assertError(MODULO + ":1:", "no es el de curso.json")


class FicherosYCarpetas(Base):
    def test_modulo_que_no_esta_en_curso_json(self):
        self.escribir("fase-01-primeros-pasos/03-suelto.md", "# 01.03 Suelto\n")
        self.assertError("fase-01-primeros-pasos/03-suelto.md", "módulo que no está en curso.json")

    def test_carpeta_de_fase_no_declarada(self):
        self.escribir("fase-02-otra/01-algo.md", "# 02.01 Algo\n")
        self.assertError("fase-02-otra/", "carpeta de fase que no está en curso.json")

    def test_modulo_disponible_que_no_existe(self):
        (self.raiz / MODULO).unlink()
        self.assertError("no existe «fase-01-primeros-pasos/01-ficheros-json.md»", "\"disponible\": false")

    def test_fichero_fuera_de_su_fase(self):
        d = self.json(); d["fases"][0]["modulos"][1]["fichero"] = "fase-09-otra/02-ficheros-yaml.md"; self.guardar_json(d)
        self.assertError("debe estar en la carpeta de su fase")

    def test_modulo_no_disponible_sin_fichero_es_aviso(self):
        d = self.json(); del d["fases"][0]["modulos"][1]["fichero"]; self.guardar_json(d)
        self.assertAviso("conviene poner ya su «fichero» previsto")

    def test_modulo_no_disponible_que_ya_existe_es_aviso(self):
        self.escribir("fase-01-primeros-pasos/02-ficheros-yaml.md", "# 01.02 Ficheros YAML\n")
        self.assertAviso("ya existe, pero sigue con \"disponible\": false")

    def test_falta_un_fichero_obligatorio(self):
        (self.raiz / "LICENSE").unlink()
        self.assertError("LICENSE", "es obligatorio")

    def test_falta_el_indice_es_aviso(self):
        (self.raiz / "00-indice.md").unlink()
        self.assertAviso("00-indice.md", "se genera desde curso.json")

    def test_indice_con_otras_fases(self):
        self.cambiar("00-indice.md", "## Fase 01 — Primeros pasos", "## Fase 01 — Primeros pasitos")
        self.assertError("00-indice.md", "no coinciden con curso.json")

    def test_hueco_de_plantilla_sin_rellenar(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.", "- [RELLENAR: buenas prácticas]")
        self.assertAviso(MODULO, "hueco de la plantilla")

    def test_ficheros_de_trabajo_no_se_revisan(self):
        self.escribir("ESTADO.md", "# Estado\n\n- `git switch` <rama> y [roto](no-existe.md) [RELLENAR: x]\n")
        self.assertSinErrores()
        self.assertFalse(self.hay(self.avisos, "ESTADO.md"))


class Retos(Base):
    def test_retos_con_otra_ruta(self):
        d = self.json(); d["fases"][0]["retos"] = "fase-01-primeros-pasos/mis-retos.md"; self.guardar_json(d)
        self.assertError("«retos» debe ser «fase-01-primeros-pasos/retos.md»")

    def test_retos_disponibles_que_no_existen(self):
        (self.raiz / RETOS).unlink()
        self.assertError("no existe «fase-01-primeros-pasos/retos.md»", "retos_disponibles")

    def test_retos_no_disponibles_es_aviso(self):
        (self.raiz / RETOS).unlink()
        d = self.json(); d["fases"][0]["retos_disponibles"] = False; self.guardar_json(d)
        self.regenerar_indice()
        self.assertSinErrores()
        self.assertAviso("los retos todavía no están escritos")

    def test_retos_disponibles_sin_retos(self):
        d = self.json(); del d["fases"][0]["retos"]; d["fases"][0]["retos_disponibles"] = False; self.guardar_json(d)
        self.assertError("«retos_disponibles» sin «retos»")

    def test_fase_sin_retos_es_aviso(self):
        d = self.json(); del d["fases"][0]["retos"]; self.guardar_json(d)
        self.assertAviso("la fase no tiene retos")

    def test_fase_que_solo_tiene_el_proyecto_final_no_avisa(self):
        d = self.json()
        d["fases"].append({"id": "ejemplo.fase.proyecto-final", "carpeta": "fase-02-proyecto-final", "titulo": "Proyecto final",
                           "modulos": [{"id": "ejemplo.mi-repositorio", "fichero": "fase-02-proyecto-final/01-mi-repositorio.md",
                                        "titulo": "Mi repositorio", "disponible": False, "ejercicios": []}]})
        d["partes"][0]["fases"].append("ejemplo.fase.proyecto-final")
        d["proyecto"] = {"tipo": "modulo", "modulo": "ejemplo.mi-repositorio"}
        self.guardar_json(d)
        shutil.rmtree(self.raiz / "proyecto")
        self.regenerar_indice()
        self.assertSinErrores()
        self.assertFalse(self.hay(self.avisos, "proyecto-final", "retos"), self.avisos)

    def test_reto_sin_solucion(self):
        self.cambiar(RETOS, "<summary>Ver solución</summary>", "<summary>Solución</summary>")
        self.assertError(RETOS, "falta la solución de el reto 1")

    def test_titulo_de_retos_con_otra_fase(self):
        self.cambiar(RETOS, "# Retos de la fase 01 — Primeros pasos", "# Retos de la fase 01 — Otra cosa")
        self.assertError(RETOS, "no es el título de la fase")

    def test_encabezado_que_no_es_un_reto(self):
        self.cambiar(RETOS, "## Reto 1 · Un catálogo de productos", "## Un catálogo de productos")
        self.assertError(RETOS, "no es un reto")


class Proyecto(Base):
    def test_sin_proyecto(self):
        d = self.json(); del d["proyecto"]; self.guardar_json(d)
        self.assertError("todo curso debe tener un proyecto")

    def test_proyecto_de_tipo_modulo_con_un_modulo_que_no_existe(self):
        d = self.json(); d["proyecto"] = {"tipo": "modulo", "modulo": "ejemplo.no-existe"}; self.guardar_json(d)
        self.assertError("el módulo «ejemplo.no-existe» no existe")

    def test_etapa_que_no_existe(self):
        (self.raiz / "proyecto/01-primer-catalogo.md").unlink()
        self.assertError("no existe «proyecto/01-primer-catalogo.md»")

    def test_etapa_no_declarada(self):
        self.escribir("proyecto/02-segunda.md", "# Etapa 2\n")
        self.assertError("proyecto/02-segunda.md", "etapa del proyecto que no está en curso.json")


class ConGit(Base):
    """Base para las pruebas que necesitan el curso en un repositorio de Git."""
    def git(self, *args):
        subprocess.run(["git", "-C", str(self.raiz), *args], check=True, capture_output=True,
                       env={"GIT_AUTHOR_NAME": "Prueba", "GIT_AUTHOR_EMAIL": "p@ejemplo.org", "GIT_COMMITTER_NAME": "Prueba",
                            "GIT_COMMITTER_EMAIL": "p@ejemplo.org", "HOME": str(self.tmp), "PATH": "/usr/bin:/bin"})

    def publicar(self):
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "v1")
        self.git("tag", "v1.0.0")


class Versiones(ConGit):
    def test_identificador_publicado_que_desaparece(self):
        self.publicar()
        d = self.json(); self.modulo(d)["ejercicios"][1]["id"] = "ejemplo.ficheros-json.coma"; self.guardar_json(d)
        self.assertError("«ejemplo.ficheros-json.la-coma-de-mas» estaba en la versión v1.0.0", "equivalencia")

    def test_con_su_equivalencia_no_hay_error(self):
        self.publicar()
        d = self.json()
        self.modulo(d)["ejercicios"][1]["id"] = "ejemplo.ficheros-json.coma"
        d["version"] = "2.0.0"
        d["equivalencias"] = [{"desde": "2.0.0", "antes": "ejemplo.ficheros-json.la-coma-de-mas",
                               "ahora": ["ejemplo.ficheros-json.coma"]}]
        self.guardar_json(d)
        self.assertSinErrores()

    def test_equivalencia_de_un_id_que_sigue_existiendo(self):
        d = self.json()
        d["equivalencias"] = [{"desde": "1.0.0", "antes": "ejemplo.ficheros-json", "ahora": []}]
        self.guardar_json(d)
        self.assertError("sigue existiendo")

    def test_retirada_sin_motivo(self):
        d = self.json()
        d["equivalencias"] = [{"desde": "1.0.0", "antes": "ejemplo.applets", "ahora": []}]
        self.guardar_json(d)
        self.assertError("debe llevar «motivo»")


class Modulo(Base):
    def test_falta_el_nivel_en_la_cabecera(self):
        self.cambiar(MODULO, "> **Nivel:** Básico · Núcleo\n", "")
        self.assertError(MODULO, "falta «> **Nivel:**»")

    def test_tiempo_mal_escrito(self):
        self.cambiar(MODULO, "> **Tiempo estimado:** 2 horas", "> **Tiempo estimado:** 2h")
        self.assertError(MODULO + ":5:", "Tiempo estimado")

    def test_requisitos_previos_ahora_es_conviene_saber_antes(self):
        self.cambiar(MODULO, "**Conviene saber antes:**", "**Requisitos previos:**")
        self.assertError(MODULO + ":4:", "ahora se llama «Conviene saber antes»")

    def test_conviene_saber_antes_sin_enlaces(self):
        self.cambiar(MODULO, "> **Conviene saber antes:** [Mi primer", "> **Conviene saber antes:** saber algo de [Mi primer")
        self.assertError(MODULO, "«Nada» o enlaces a módulos")

    def test_falta_una_seccion(self):
        self.cambiar(MODULO, "## 6. Chuleta", "## Resumen")
        self.assertError(MODULO, "falta la sección «## 6. Chuleta»")

    def test_seccion_fuera_de_orden(self):
        texto = (self.raiz / MODULO).read_text(encoding="utf-8")
        texto = texto.replace("## 3. Errores típicos", "## TMP").replace("## 4. Buenas prácticas", "## 3. Errores típicos")
        self.escribir(MODULO, texto.replace("## TMP", "## 4. Buenas prácticas"))
        self.assertError(MODULO, "fuera de su sitio")

    def test_sin_preguntas_de_repaso(self):
        texto = (self.raiz / MODULO).read_text(encoding="utf-8")
        self.escribir(MODULO, texto[:texto.index("## 7. Preguntas de repaso")] + "---\n📚 [Índice](../00-indice.md)\n")
        self.assertError(MODULO, "falta la sección «## 7. Preguntas de repaso»")

    def test_sin_preguntas_en_transicion_es_aviso(self):
        texto = (self.raiz / MODULO).read_text(encoding="utf-8")
        self.escribir(MODULO, texto[:texto.index("## 7. Preguntas de repaso")] + "---\n📚 [Índice](../00-indice.md)\n")
        d = self.json(); d["transicion"] = ["preguntas-de-repaso"]; self.guardar_json(d)
        self.assertSinErrores()
        self.assertAviso("faltan las preguntas de repaso")

    def test_pregunta_sin_respuesta(self):
        self.cambiar(MODULO, "<summary>Ver respuesta</summary>", "<summary>Respuesta</summary>")
        self.assertError(MODULO, "la pregunta 1 no tiene respuesta")

    def test_subapartado_de_teoria_sin_numerar_es_aviso(self):
        self.cambiar(MODULO, "### 1.2. Objetos y listas", "### Objetos y listas")
        self.cambiar(MODULO, "(#12-objetos-y-listas)", "(#objetos-y-listas)")
        self.assertAviso(MODULO, "se numeran: «### 1.1. …»")

    def test_subapartado_de_la_chuleta_sin_numerar_no_avisa(self):
        self.comprobar()
        self.assertFalse(self.hay(self.avisos, "6. Chuleta"), self.avisos)

    def test_details_sin_cerrar(self):
        self.cambiar(MODULO, "Mira el final.\n\n</details>", "Mira el final.\n")
        self.assertError(MODULO, "<details> sin cerrar")

    def test_bloque_de_codigo_sin_cerrar(self):
        self.escribir(MODULO, (self.raiz / MODULO).read_text(encoding="utf-8") + "\n```json\n{}\n")
        self.assertError(MODULO, "bloque de código sin cerrar")


class Ejercicios(Base):
    def test_ejercicio_que_no_esta_en_curso_json(self):
        self.cambiar(MODULO, "#### Ejercicio 1 · Un pedido de la tienda", "#### Ejercicio 1 · Un pedido")
        self.assertError(MODULO, "«Un pedido», no está en curso.json")
        self.assertError(MODULO, "falta el ejercicio «Un pedido de la tienda»")

    def test_ejercicios_en_otro_orden(self):
        d = self.json(); self.modulo(d)["ejercicios"].reverse(); self.guardar_json(d)
        self.assertError(MODULO, "no están en el mismo orden")

    def test_ejercicio_sin_solucion(self):
        self.cambiar(MODULO, "Sobra la coma del final", "Sobra la coma")
        self.cambiar(MODULO, "Mira el final.\n\n</details>\n\n<details>\n<summary>Ver solución</summary>",
                     "Mira el final.\n\n</details>\n\n<details>\n<summary>Más</summary>")
        self.assertError(MODULO, "falta la solución de el ejercicio 2")

    def test_pista_despues_de_la_solucion(self):
        self.cambiar(MODULO, "#### Ejercicio 2 · La coma de más\n\nEncuentra el error de `{\"a\": 1,}`.\n\n<details>\n<summary>Pista 1</summary>\n\nMira el final.\n\n</details>\n",
                     "#### Ejercicio 2 · La coma de más\n\nEncuentra el error de `{\"a\": 1,}`.\n")
        self.cambiar(MODULO, "lo explica [3.1](#31-la-coma-de-más).\n\n</details>\n",
                     "lo explica [3.1](#31-la-coma-de-más).\n\n</details>\n\n<details>\n<summary>Pista 1</summary>\n\nMira.\n\n</details>\n")
        self.assertError(MODULO, "está después de la solución")

    def test_ejercicio_sin_pistas_es_aviso(self):
        self.cambiar(MODULO, "<details>\n<summary>Pista 1</summary>\n\nMira el final.\n\n</details>\n", "")
        self.assertAviso(MODULO, "el ejercicio 2 no tiene pistas")

    def test_details_anidado_en_la_solucion_no_cuenta(self):
        self.assertSinErrores()     # el ejercicio 1 tiene un <details> dentro de la solución

    def test_nivel_desconocido(self):
        self.cambiar(MODULO, "### 🟡 Intermedio", "### Intermedio")
        self.assertError(MODULO, "nivel de ejercicios desconocido")

    def test_encabezado_de_ejercicio_mal_escrito(self):
        self.cambiar(MODULO, "#### Ejercicio 2 · La coma de más", "#### Ejercicio 2: La coma de más")
        self.assertError(MODULO, "no es un ejercicio")


class Enlaces(Base):
    def test_enlace_roto(self):
        self.cambiar(MODULO, "](../00-indice.md)", "](../00-indise.md)")
        self.assertError(MODULO, "no existe ../00-indise.md")

    def test_ancla_rota(self):
        self.cambiar(MODULO, "(#12-objetos-y-listas)", "(#12-objetos)")
        self.assertError(MODULO, "no existe la sección #12-objetos")

    def test_ancla_con_codigo_y_genericos(self):
        self.assertEqual(formato_academia.ancla("2.2. Una clase genérica: `Page<T>`"), "22-una-clase-genérica-paget")
        self.assertEqual(formato_academia.ancla("Ejercicio 6 · El error"), "ejercicio-6--el-error")

    def test_enlace_a_un_modulo_pendiente_es_aviso(self):
        self.assertAviso(MODULO, "enlace a un módulo pendiente", "02-ficheros-yaml.md")

    def test_enlace_a_un_modulo_pendiente_con_ancla_avisa_del_ancla(self):
        self.cambiar(MODULO, "[Ficheros YAML](02-ficheros-yaml.md)", "[Ficheros YAML](02-ficheros-yaml.md#11-qué-es-yaml)")
        self.assertAviso(MODULO, "módulo pendiente", "su ancla #11-qué-es-yaml no se podrá comprobar")

    def test_enlace_a_un_fichero_que_no_esta_en_curso_json_es_error(self):
        self.cambiar(MODULO, "[Ficheros YAML](02-ficheros-yaml.md)", "[Ficheros YAML](02-ficheros-yml.md)")
        self.assertError(MODULO, "no existe 02-ficheros-yml.md", "no es ningún módulo previsto")

    def test_enlace_relativo_que_sale_del_curso(self):
        self.cambiar(MODULO, "](../00-indice.md)", "](../../curso-inicial/README.md)")
        self.assertError(MODULO, "sale del curso")

    def test_enlaces_a_otro_curso_buenos(self):
        # un módulo con ancla y un término del glosario de ejemplo-destino, en su carpeta hermana
        self.assertSinErrores()
        self.assertFalse(self.hay(self.avisos, "ejemplo-destino"), self.avisos)

    def test_enlace_a_otro_curso_con_ancla_rota(self):
        self.cambiar(MODULO, "#11-qué-es-un-repositorio", "#no-existe")
        self.assertError(MODULO, "no existe la sección #no-existe", "de ../ejemplo-destino/")

    def test_enlace_a_un_termino_del_glosario_que_no_existe(self):
        self.cambiar(MODULO, "glosario.md#repositorio", "glosario.md#rapositorio")
        self.assertError(MODULO, "no existe la sección #rapositorio en glosario.md de ../ejemplo-destino/")

    def test_enlace_a_un_modulo_pendiente_de_otro_curso(self):
        destino = self.tmp / "ejemplo-destino" / "curso.json"
        d = json.loads(destino.read_text(encoding="utf-8"))
        d["fases"][0]["modulos"].append({"id": "ejemplo-destino.ramas", "fichero": "fase-01-tu-primer-proyecto/02-ramas.md",
                                         "titulo": "Ramas", "disponible": False, "ejercicios": []})
        destino.write_text(json.dumps(d), encoding="utf-8")
        self.cambiar(MODULO, "01-mi-primer-repositorio.md#11-qué-es-un-repositorio", "02-ramas.md")
        self.assertAviso(MODULO, "módulo pendiente", "de ../ejemplo-destino/")

    def test_enlace_a_otro_curso_sin_la_carpeta_hermana_es_aviso(self):
        shutil.rmtree(self.tmp / "ejemplo-destino")
        self.assertAviso(MODULO, "no he podido revisar", "../ejemplo-destino/")

    def test_enlace_a_otro_curso_en_otra_rama(self):
        self.cambiar(MODULO, ENLACE_DESTINO, ENLACE_DESTINO.replace("/main/", "/dev/"))
        self.assertError(MODULO, "debe apuntar a la rama main")


class Imagenes(Base):
    def test_imagen_de_otra_web(self):
        self.cambiar(MODULO, "(img/estructura.svg)", "(https://ejemplo.org/a.png)")
        self.assertError(MODULO, "imagen de otra web")

    def test_imagen_sin_texto_alternativo(self):
        self.cambiar(MODULO, "![Estructura de un objeto JSON]", "![]")
        self.assertError(MODULO, "no tiene texto alternativo")

    def test_imagen_gif(self):
        self.escribir("fase-01-primeros-pasos/img/a.gif", "GIF89a")
        self.cambiar(MODULO, "(img/estructura.svg)", "(img/a.gif)")
        self.assertError(MODULO, "solo se admiten PNG, JPG o SVG")

    def test_imagen_incrustada(self):
        self.cambiar(MODULO, "(img/estructura.svg)", "(data:image/png;base64,AAAA)")
        self.assertError(MODULO, "imagen incrustada")

    def test_imagen_que_no_existe(self):
        self.cambiar(MODULO, "(img/estructura.svg)", "(img/otra.svg)")
        self.assertError(MODULO, "no existe la imagen img/otra.svg")


class Mermaid(Base):
    def test_negrita_en_una_etiqueta(self):
        self.cambiar(MODULO, 'B[Clave]', 'B["**Clave**"]')
        self.assertError(MODULO, "Mermaid con negrita o cursiva")

    def test_etiqueta_html_de_negrita(self):
        self.cambiar(MODULO, 'B[Clave]', 'B["<b>Clave</b>"]')
        self.assertError(MODULO, "Mermaid con negrita o cursiva")

    def test_entidad_no_admitida(self):
        self.cambiar(MODULO, "&quot;cliente&quot;", "&laquo;cliente&raquo;")
        self.assertError(MODULO, "la entidad &laquo;")

    def test_interaccion(self):
        self.cambiar(MODULO, "    B -->|tiene| C[Valor]", "    B -->|tiene| C[Valor]\n    click A \"https://ejemplo.org\"")
        self.assertError(MODULO, "interacciones")

    def test_directiva(self):
        self.cambiar(MODULO, "flowchart LR", "%%{init: {'theme': 'dark'}}%%\nflowchart LR")
        self.assertError(MODULO, "directivas")

    def test_flecha_de_composicion_no_es_cursiva(self):
        self.cambiar(MODULO, "flowchart LR\n    A[\"Objeto &quot;cliente&quot;\"] --> B[Clave]\n    B -->|tiene| C[Valor]",
                     "classDiagram\n    Order \"1\" *-- \"*\" OrderLine : contiene")
        self.assertSinErrores()


class Html(Base):
    def test_script(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.", "- Usa nombres de clave claros. <script>alert(1)</script>")
        self.assertError(MODULO, "<script> no se admite")

    def test_manejador_de_eventos(self):
        self.cambiar(MODULO, "<kbd>Ctrl</kbd>", '<kbd onclick="x()">Ctrl</kbd>')
        self.assertError(MODULO, "<kbd> con atributos que la academia no admite (onclick)")

    def test_details_open_no_lo_admite_la_academia(self):
        self.cambiar(MODULO, "<details>\n<summary>Pista 1</summary>", "<details open>\n<summary>Pista 1</summary>")
        self.assertError(MODULO, "<details> con atributos que la academia no admite (open)")

    def test_span_es_aviso(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.", "- Usa <span>nombres</span> de clave claros.")
        self.assertAviso(MODULO, "<span>: la academia quita esta etiqueta")

    def test_span_con_atributos_es_error(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.", '- Usa <span style="color:red">nombres</span>.')
        self.assertError(MODULO, "<span> con atributos (style)")

    def test_img_en_html(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.", '- <img src="img/estructura.svg" alt="x">')
        self.assertError(MODULO, "<img> no se admite")

    def test_html_admitido_no_avisa(self):
        self.comprobar()       # el curso bueno usa <kbd> y <code> dentro de <summary>
        self.assertFalse(self.hay(self.avisos, "<kbd>") or self.hay(self.avisos, "<code>"), self.avisos)

    def test_lo_que_va_entre_comillas_invertidas_no_es_html(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.", "- Escribe `git switch <rama>` para cambiar.")
        self.assertSinErrores()


class ListasDeTareas(Base):
    """La academia todavía no dibuja las listas de tareas de Markdown (- [ ] / - [x]): aviso fuera del código."""

    def test_lista_de_tareas_avisa(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.", "- [ ] Usa nombres de clave claros.\n- [x] Hecho.\n1. [X] Otro.")
        self.comprobar()
        avisos = [a for a in self.avisos if "lista de tareas" in a]
        self.assertEqual(len(avisos), 3, self.avisos)
        self.assertEqual(self.errores, [])

    def test_en_un_bloque_de_codigo_o_un_enlace_no_avisa(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.",
                     "- [x](https://example.com) es un enlace.\n\n```markdown\n- [ ] Comprar pan\n```\n\n- `- [ ]` en línea.")
        self.comprobar()
        self.assertFalse(self.hay(self.avisos, "lista de tareas"), self.avisos)


class Correos(Base):
    """La academia no admite enlaces mailto:, y <ana@example.com> fuera de código lo es: aviso."""

    def test_correo_entre_angulos_avisa(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.",
                     "- Escribe a Ana García <ana@example.com>.\n- O a <MAILTO:luis@example.com>.\n"
                     "- O [a Raúl](mailto:raul@example.com).")
        self.comprobar()
        avisos = [a for a in self.avisos if "mailto:" in a]
        self.assertEqual(len(avisos), 3, self.avisos)
        self.assertTrue(self.hay(avisos, "<ana@example.com> fuera de código"), avisos)
        self.assertEqual(self.errores, [])

    def test_en_codigo_escapado_o_sin_angulos_no_avisa(self):
        self.cambiar(MODULO, "- Usa nombres de clave claros.",
                     "- `Ana García <ana@example.com>` en línea.\n- Escapado: \\<ana@example.com>.\n"
                     "- Con espacio, no es correo: <ana @example.com>.\n\n"
                     "```text\nAuthor: Ana García <ana@example.com>\n```")
        self.comprobar()
        self.assertFalse(self.hay(self.avisos, "mailto:"), self.avisos)


class Glosario(Base):
    def test_cualquier_curso_puede_tener_su_glosario(self):
        self.escribir("glosario.md", "# Glosario\n\n## J\n\n### JSON\n\nUn formato de datos.\n")
        self.assertSinErrores()
        self.assertFalse(self.hay(self.avisos, "glosario.md"), self.avisos)

    def test_el_glosario_propio_tambien_se_comprueba(self):
        self.escribir("glosario.md", "# Glosario\n\n## J\n\n### JSON\n\n### JSON\n")
        self.assertError("glosario.md", "el término «JSON» está repetido")

    def test_al_curso_inicial_no_le_puede_faltar(self):
        d = self.json(); d["id"] = "inicial"
        (self.raiz / "curso.json").write_text(json.dumps(d).replace('"ejemplo.', '"inicial.'), encoding="utf-8")
        self.assertAviso("glosario.md", "el curso inicial tiene el glosario común")

    def test_glosario_desordenado(self):
        d = self.json(); d["id"] = "inicial"
        texto = json.dumps(d).replace('"ejemplo.', '"inicial.')
        (self.raiz / "curso.json").write_text(texto, encoding="utf-8")
        self.escribir("glosario.md", "# Glosario\n\n## A\n\n### Árbol\n\n### API\n")
        self.assertAviso("glosario.md", "«API» no está en orden alfabético")

    def glosario_inicial(self, texto):
        d = self.json(); d["id"] = "inicial"
        (self.raiz / "curso.json").write_text(json.dumps(d).replace('"ejemplo.', '"inicial.'), encoding="utf-8")
        self.escribir("glosario.md", texto)

    def test_glosario_con_letras_desordenadas(self):
        self.glosario_inicial("# Glosario\n\n## B\n\n### Bash\n\n## A\n\n### API\n")
        self.assertAviso("glosario.md", "la letra «A» no está en orden alfabético")

    def test_glosario_con_un_termino_repetido(self):
        self.glosario_inicial("# Glosario\n\n## A\n\n### API\n\n### Árbol\n\n### api\n")
        self.assertError("glosario.md", "el término «api» está repetido")

    def test_glosario_con_la_enie_entre_la_n_y_la_o(self):
        self.glosario_inicial("# Glosario\n\n## N\n\n### Nube\n\n## Ñ\n\n### Ñandú\n\n## O\n\n### Oso\n")
        self.comprobar()
        self.assertFalse(self.hay(self.avisos + self.errores, "glosario.md"), self.avisos)


class SaltosDeLinea(ConGit):
    SCRIPT = "fase-01-primeros-pasos/codigo/01-ficheros-json/ejemplos/2.2-contar-clientes/contar.sh"
    CRLF = "saltos de línea CRLF"
    SIN_LF = "no saldría con LF en un clon"

    def crlf(self, rel=None):
        ruta = self.raiz / (rel or self.SCRIPT)
        ruta.write_bytes(ruta.read_bytes().replace(b"\n", b"\r\n"))

    def avisos_de(self, trozo):
        self.comprobar()
        return [a for a in self.avisos if trozo in a]

    # -- sin Git: solo el disco ---------------------------------------------------------------------

    def test_sin_git_un_script_con_crlf_avisa_con_la_linea(self):
        self.crlf()
        avisos = self.avisos_de(self.CRLF)
        self.assertEqual(len(avisos), 1, avisos)
        self.assertTrue(avisos[0].startswith(f"{self.SCRIPT}:1: "), avisos)
        self.assertSinErrores()

    def test_sin_git_la_linea_es_la_primera_con_crlf(self):
        ruta = self.raiz / self.SCRIPT
        ruta.write_bytes(b"#!/bin/bash\necho uno\necho dos\r\n")
        self.assertTrue(self.avisos_de(self.CRLF)[0].startswith(f"{self.SCRIPT}:3: "))

    def test_sin_git_un_fichero_de_datos_con_crlf_tambien_avisa(self):
        self.crlf(self.SCRIPT.replace("contar.sh", "clientes.json"))
        self.assertEqual(len(self.avisos_de(self.CRLF)), 1)

    def test_un_binario_no_avisa(self):
        self.escribir(self.SCRIPT.replace("contar.sh", "logo.png"), "")
        (self.raiz / self.SCRIPT.replace("contar.sh", "logo.png")).write_bytes(b"\x89PNG\r\n\x1a\n\0\0\r\n")
        self.assertEqual(self.avisos_de(self.CRLF), [])

    def test_fuera_de_codigo_no_avisa(self):
        self.crlf("README.md")
        self.assertEqual(self.avisos_de(self.CRLF), [])

    def test_el_curso_bueno_no_avisa_de_saltos_de_linea(self):
        self.publicar()
        self.assertEqual(self.avisos_de(self.CRLF) + self.avisos_de(self.SIN_LF), [])

    # -- con Git: lo que guarda Git y lo que saldría en un clon -------------------------------------

    def test_sin_eol_lf_en_gitattributes_avisa_una_vez(self):
        (self.raiz / ".gitattributes").write_text("*.sh text eol=lf\n", encoding="utf-8")
        self.publicar()
        avisos = self.avisos_de(self.SIN_LF)
        self.assertEqual(len(avisos), 1, avisos)
        self.assertTrue(avisos[0].startswith(".gitattributes:0: "))
        self.assertIn("* text=auto eol=lf", avisos[0])
        self.assertNotIn("contar.sh", avisos[0])                 # el script sí sale con LF

    def test_sin_gitattributes_avisa(self):
        (self.raiz / ".gitattributes").unlink()
        self.publicar()
        self.assertEqual(len(self.avisos_de(self.SIN_LF)), 1)

    def test_un_script_guardado_con_crlf_avisa(self):
        (self.raiz / ".gitattributes").unlink()
        self.crlf()
        self.publicar()
        self.assertEqual(len(self.avisos_de(f"{self.SCRIPT}:1: {self.CRLF}")), 1)

    def test_crlf_solo_en_el_disco_no_avisa_si_git_guarda_lf(self):
        self.publicar()
        self.crlf()                                               # p. ej., un clon en Windows sin eol=lf
        self.assertEqual(self.avisos_de(self.CRLF), [])

    def test_un_fichero_nuevo_con_crlf_que_git_normalizara_no_avisa(self):
        self.publicar()
        self.escribir(self.SCRIPT.replace("contar.sh", "nuevo.sh"), "echo hola\r\n")
        self.assertEqual(self.avisos_de(self.CRLF), [])

    def test_un_fichero_nuevo_con_crlf_sin_gitattributes_avisa(self):
        (self.raiz / ".gitattributes").unlink()
        self.publicar()
        self.escribir(self.SCRIPT.replace("contar.sh", "nuevo.sh"), "echo hola\r\n")
        self.assertEqual(len(self.avisos_de(self.CRLF)), 1)

    def test_marcado_con_menos_text_no_avisa(self):
        with open(self.raiz / ".gitattributes", "a", encoding="utf-8") as f:
            f.write(f"{self.SCRIPT} -text\n")
        self.crlf()
        self.publicar()
        self.assertEqual(self.avisos_de(self.CRLF) + self.avisos_de(self.SIN_LF), [])


class ComoUnClon(ConGit):
    """Carpetas vacías y permisos de codigo/, que no viajan con Git."""
    CARPETA = "fase-01-primeros-pasos/codigo/01-ficheros-json/ejemplos/2.3-ver-un-fichero"
    VACIA = "no existirá en un clon"
    PUNTO = "necesita permiso de ejecución"

    def avisos_de(self, trozo):
        self.comprobar()
        return [a for a in self.avisos if trozo in a]

    def script_y_sesion(self, sesion, ejecutable=False):
        self.escribir(f"{self.CARPETA}/hola.sh", "#!/bin/bash\necho hola\n")
        (self.raiz / self.CARPETA / "hola.sh").chmod(0o755 if ejecutable else 0o644)
        self.escribir(f"{self.CARPETA}/sesion.txt", sesion)

    # -- carpetas vacías -----------------------------------------------------------------------------

    def test_carpeta_vacia_avisa_y_propone_mkdir_y_gitkeep(self):
        (self.raiz / self.CARPETA / "Descargas").mkdir()
        avisos = self.avisos_de(self.VACIA)
        self.assertEqual(len(avisos), 1, avisos)
        self.assertTrue(avisos[0].startswith(f"{self.CARPETA}/Descargas/:0: "))
        self.assertIn("mkdir", avisos[0])
        self.assertIn(".gitkeep", avisos[0])
        self.assertIn("rmdir", avisos[0])
        self.assertLess(avisos[0].index("mkdir"), avisos[0].index(".gitkeep"))   # primero, mkdir

    def test_solo_avisa_de_la_carpeta_de_mas_arriba(self):
        (self.raiz / self.CARPETA / "a" / "b" / "c").mkdir(parents=True)
        avisos = self.avisos_de(self.VACIA)
        self.assertEqual(len(avisos), 1, avisos)
        self.assertIn(f"{self.CARPETA}/a/:0:", avisos[0])

    def test_carpeta_con_un_fichero_no_avisa(self):
        self.escribir(f"{self.CARPETA}/Descargas/.gitkeep", "")
        self.assertEqual(self.avisos_de(self.VACIA), [])

    def test_carpeta_vacia_fuera_de_codigo_no_avisa(self):
        (self.raiz / "fase-01-primeros-pasos" / "img" / "vacia").mkdir(parents=True)
        self.assertEqual(self.avisos_de(self.VACIA), [])

    def test_carpeta_con_solo_ficheros_ignorados_avisa(self):
        self.escribir(f"{self.CARPETA}/Descargas/basura.tmp", "x")
        with open(self.raiz / ".gitignore", "a", encoding="utf-8") as f:
            f.write("*.tmp\n")
        self.publicar()
        self.assertEqual(len(self.avisos_de(self.VACIA)), 1)

    # -- scripts lanzados con ./ ---------------------------------------------------------------------

    def test_lanzado_con_punto_sin_permiso_en_git(self):
        self.script_y_sesion("ls\n./hola.sh\n")
        self.publicar()
        avisos = self.avisos_de(self.PUNTO)
        self.assertEqual(len(avisos), 1, avisos)
        self.assertTrue(avisos[0].startswith(f"{self.CARPETA}/sesion.txt:2: "))
        self.assertIn("git update-index --chmod=+x", avisos[0])

    def test_permiso_en_el_disco_pero_no_en_git_avisa(self):
        self.script_y_sesion("./hola.sh\n")
        self.publicar()
        (self.raiz / self.CARPETA / "hola.sh").chmod(0o755)          # sin commit del permiso
        self.assertEqual(len(self.avisos_de(self.PUNTO)), 1)

    def test_con_permiso_en_git_no_avisa(self):
        self.script_y_sesion("./hola.sh\n", ejecutable=True)
        self.publicar()
        self.comprobar()
        self.assertEqual([a for a in self.avisos if self.PUNTO in a or "hola.sh" in a], [])

    def test_detras_de_y_y_punto_y_coma(self):
        self.script_y_sesion("cd . && ./hola.sh\necho; ./hola.sh hola\n")
        self.publicar()
        self.assertEqual(len(self.avisos_de(self.PUNTO)), 2)

    def test_la_sesion_que_ensena_el_chmod_no_avisa(self):
        self.script_y_sesion("./hola.sh\nchmod +x hola.sh\n./hola.sh\n")      # primero, «Permiso denegado»
        self.publicar()
        self.assertEqual(self.avisos_de(self.PUNTO), [])

    def test_en_una_serie_vale_el_chmod_de_otra_sesion(self):
        self.script_y_sesion("ls\n")
        self.escribir(f"{self.CARPETA}/sesion-1.txt", "chmod +x hola.sh\n")
        self.escribir(f"{self.CARPETA}/sesion-2.txt", "./hola.sh\n")
        self.publicar()
        self.assertEqual(self.avisos_de(self.PUNTO), [])

    def test_el_chmod_de_una_serie_no_vale_para_una_sesion_suelta(self):
        self.script_y_sesion("./hola.sh\n")
        self.escribir(f"{self.CARPETA}/sesion-1.txt", "chmod +x hola.sh\n")
        self.publicar()
        avisos = self.avisos_de(self.PUNTO)
        self.assertEqual(len(avisos), 1, avisos)
        self.assertTrue(avisos[0].startswith(f"{self.CARPETA}/sesion.txt:1: "))

    def test_con_bash_no_hace_falta_el_permiso(self):
        self.script_y_sesion("bash hola.sh\nbash ./hola.sh\n")
        self.publicar()
        self.assertEqual(self.avisos_de(self.PUNTO), [])

    def test_un_script_que_crea_la_sesion_no_avisa(self):
        self.escribir(f"{self.CARPETA}/sesion.txt", "./otro.sh\n")
        self.publicar()
        self.assertEqual(self.avisos_de(self.PUNTO), [])

    def test_sin_git_mira_el_disco(self):
        self.script_y_sesion("./hola.sh\n")
        self.assertEqual(len(self.avisos_de(self.PUNTO)), 1)
        (self.raiz / self.CARPETA / "hola.sh").chmod(0o755)
        self.assertEqual(self.avisos_de(self.PUNTO), [])

    # -- permisos que no viajan ----------------------------------------------------------------------

    def test_solo_lectura_avisa(self):
        self.publicar()
        (self.raiz / self.CARPETA / "cliente.json").chmod(0o444)
        avisos = self.avisos_de("no tiene permiso de lectura o de escritura")
        self.assertEqual(len(avisos), 1, avisos)
        self.assertIn("cliente.json", avisos[0])

    def test_solo_lectura_sin_git_tambien_avisa(self):
        (self.raiz / self.CARPETA / "cliente.json").chmod(0o444)
        self.assertEqual(len(self.avisos_de("no tiene permiso de lectura o de escritura")), 1)

    def test_ejecutable_en_el_disco_y_no_en_git(self):
        self.publicar()
        (self.raiz / self.CARPETA / "cliente.json").chmod(0o755)
        avisos = self.avisos_de("es ejecutable en el disco y Git lo guarda sin permiso")
        self.assertEqual(len(avisos), 1, avisos)

    def test_permisos_del_grupo_no_avisan(self):
        self.publicar()
        (self.raiz / self.CARPETA / "cliente.json").chmod(0o600)
        self.comprobar()
        self.assertEqual([a for a in self.avisos if "cliente.json" in a], [])

    def test_con_core_filemode_false_no_mira_la_ejecucion(self):
        self.publicar()
        self.git("config", "core.fileMode", "false")
        (self.raiz / self.CARPETA / "cliente.json").chmod(0o755)
        self.assertEqual(self.avisos_de("Git lo guarda sin permiso"), [])

    def test_el_curso_bueno_no_avisa(self):
        self.publicar()
        self.assertEqual(self.avisos_de(self.VACIA) + self.avisos_de(self.PUNTO) + self.avisos_de("permiso"), [])


class LineaDeOrdenes(unittest.TestCase):
    def ejecutar(self, *args):
        return subprocess.run([sys.executable, str(HERRAMIENTAS / "formato_academia.py"), *args],
                              capture_output=True, text=True)

    def test_ayuda(self):
        r = self.ejecutar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("FORMATO.md", r.stdout)

    def test_opcion_desconocida(self):
        self.assertEqual(self.ejecutar("--rapido").returncode, 2)

    def test_carpeta_que_no_existe(self):
        r = self.ejecutar("/no/existe")
        self.assertEqual(r.returncode, 2)
        self.assertIn("No existe la carpeta", r.stderr)

    def test_curso_bueno_termina_con_0(self):
        r = self.ejecutar(str(BUENO))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("✅", r.stdout)

    def test_curso_malo_termina_con_1_y_dice_fichero_y_linea(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp) / "curso-ejemplo"
            shutil.copytree(BUENO, raiz)
            modulo = raiz / MODULO
            modulo.write_text(modulo.read_text(encoding="utf-8").replace("<summary>Ver respuesta</summary>", "<summary>x</summary>"),
                              encoding="utf-8")
            r = self.ejecutar(str(raiz))
            self.assertEqual(r.returncode, 1)
            self.assertIn(f"{MODULO}:", r.stdout)
            self.assertIn("ERROR: la pregunta 1 no tiene respuesta", r.stdout)
            self.assertIn("❌", r.stdout)


class Env(ConGit):
    """Los .env de codigo/: solo .env.example, y sin secretos con pinta de reales."""
    CARPETA = "fase-01-primeros-pasos/codigo/01-ficheros-json/ejemplos/2.3-ver-un-fichero"

    def test_un_env_real_es_error(self):
        for nombre in (".env", ".env.local", ".env.production", ".ENV"):
            with self.subTest(nombre=nombre):
                self.escribir(f"{self.CARPETA}/{nombre}", "CLAVE=x\n")
                self.assertError(f"{self.CARPETA}/{nombre}:0:", "la academia solo admite .env.example")
                (self.raiz / self.CARPETA / nombre).unlink()

    def test_env_example_con_valores_de_ejemplo_no_dice_nada(self):
        self.escribir(f"{self.CARPETA}/.env.example",
                      "# Copia este fichero a .env\nPUERTO=8080\nDEBUG=true\nAPI_KEY=\nSECRET_KEY=cambia-esto\n"
                      "DB_URL=postgres://app:tu-clave@localhost/app\nexport JWT_SECRET=\"<pon-aqui-tu-secreto>\"\n")
        self.comprobar()
        self.assertEqual([e for e in self.errores + self.avisos if ".env" in e], [])

    def test_env_example_con_secretos_avisa_sin_decir_el_valor(self):
        token = "ghp_" + "a1B2" * 9
        self.escribir(f"{self.CARPETA}/.env.example",
                      f"PUERTO=8080\nGITHUB_TOKEN={token}\nDB_URL=postgres://app:S3cr3tPass99@db/app\n"
                      "SECRET_KEY='9f8a7b6c5d4e3f2a1b0c9d8e'\nAWS_ACCESS_KEY_ID=AKIAQWERTYUIOPASDFGH\n"
                      "CORREO_CLAVE_API=7d2Kq9xLm4Pz8Rt1\n")
        self.comprobar()
        avisos = [a for a in self.avisos if ".env.example" in a]
        self.assertEqual(len(avisos), 5, avisos)
        self.assertTrue(self.hay(avisos, ".env.example:2:", "GITHUB_TOKEN", "un token de GitHub"))
        self.assertTrue(self.hay(avisos, ".env.example:3:", "DB_URL", "una URL con contraseña"))
        self.assertTrue(self.hay(avisos, ".env.example:4:", "SECRET_KEY", "clave larga y aleatoria"))
        self.assertTrue(self.hay(avisos, ".env.example:5:", "una clave de acceso de AWS"))
        self.assertTrue(self.hay(avisos, ".env.example:6:", "CORREO_CLAVE_API"))     # nombres en español
        self.assertFalse(any(token in a or "S3cr3tPass99" in a for a in avisos))
        self.assertFalse(self.hay(self.errores, ".env"))

    def test_env_example_con_mayusculas_es_error(self):
        self.escribir(f"{self.CARPETA}/.env.EXAMPLE", "A=1\n")
        self.assertError(f"{self.CARPETA}/.env.EXAMPLE:0:", "en minúsculas")

    def test_env_que_git_ignora_avisa(self):
        self.escribir(".gitignore", ".env\n")
        self.escribir(f"{self.CARPETA}/.env", "CLAVE=x\n")
        self.git("init", "-q", "-b", "main")
        self.comprobar()
        self.assertFalse(self.hay(self.errores, ".env"), self.errores)
        self.assertTrue(self.hay(self.avisos, f"{self.CARPETA}/.env:0:", "que Git ignora"), self.avisos)

    def test_fuera_de_codigo_no_se_mira(self):
        self.escribir(".env.example", "GITHUB_TOKEN=ghp_" + "a1B2" * 9 + "\n")
        self.comprobar()
        self.assertFalse(self.hay(self.errores + self.avisos, ".env"))


if __name__ == "__main__":
    unittest.main()
