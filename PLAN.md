# Plan del kit de cursos

> 8 de noviembre de 2026. Sale del plan general (`../../PLAN.md`, apartados 7 y 8.2) y del paso 0 (`FORMATO.md`).

## 1. Objetivo

Que se pueda **escribir un curso para MyOpenAcademy, verificarlo y saber que se puede instalar**. Primero, **lo justo para el curso inicial**; se amplía cuando lo pida el siguiente curso.

## 2. Estructura prevista

```
kit-cursos/
├── README.md                 ← qué es y cómo arrancar un curso nuevo, paso a paso
├── FORMATO.md                ← el contrato (versión 1)
├── plantillas/               ← lo que se copia al crear un curso, con huecos
│   ├── curso.json
│   ├── CLAUDE.md, PLAN-CURSO.md, ESTADO.md
│   ├── README.md, LICENSE, CONTRIBUTING.md, CHANGELOG.md, .gitignore
│   ├── modulo.md
│   └── retos.md
└── herramientas/
    ├── README.md
    ├── formato_academia.py   ← comprueba que un curso cumple FORMATO.md (la pieza central)
    ├── nucleo/               ← lo genérico: enlaces, Mermaid, índice y chuleta desde curso.json, argumentos…
    ├── servicios/            ← vacía hasta que la pida el curso de Java (bases de datos, contenedores, servidor Linux…)
    └── lenguajes/            ← un ejecutor por lenguaje o formato, con prefijo formato_ los de formatos (formato_json.py…)
```

## 3. Tareas para el curso inicial (versión mínima)

En este orden:

1. ~~**README del kit** y **plantillas**~~ (hecho el 8 de noviembre de 2026) (apartado 2), con `curso.json` de ejemplo y el módulo tipo de `FORMATO.md`.
2. ~~**`formato_academia.py`**~~ (hecho el 8 de noviembre de 2026; ver `ESTADO.md`): todo lo del apartado 13 de `FORMATO.md` (`curso.json`, módulos, retos, glosario, proyecto, enlaces del mismo curso y entre cursos, imágenes, Mermaid, HTML, ficheros obligatorios), con errores y avisos, y el campo `transicion`. Incluye que los títulos del curso, las fases, los módulos, los ejercicios y los retos sean texto plano (sin `` ` ``, `**`, `*`, `_`, enlaces ni HTML), en `curso.json` y en los encabezados. Con pruebas sobre cursos de ejemplo pequeños, buenos y malos.
3. **Del núcleo de las herramientas de Java**, lo que necesita el curso inicial:
   - ~~`comprobar_enlaces.py`~~: no se hace aparte (decisión del autor, 8 de noviembre de 2026). `formato_academia.py` ya comprueba los enlaces y las anclas, también entre cursos; lo que cubría se añadirá como opciones de `formato_academia.py` (ver «Después»).
   - `comprobar_mermaid.py` (necesita Node y Chrome; su ruta, en variables de entorno).
   - ~~`generar_indice.py`~~ (hecho el 8 de noviembre de 2026) y `generar_chuleta_global.py`, que pasan a leer `curso.json` en vez de una lista dentro del script.
   - ~~`argumentos.py`~~ (hecho el 8 de noviembre de 2026).
   - Van en `herramientas/nucleo/` y se ejecutan desde la raíz del curso (la raíz es la carpeta actual o la que se indique, no la carpeta del script).
4. **Comprobadores de los formatos del curso inicial** para sus ejemplos, ejercicios y retos, según su lista (`../curso-inicial/ESTADO.md`, «Lista para el kit», aprobada el 8 de noviembre de 2026):
   - JSON, YAML y XML (válidos, o que fallan con `debe-fallar.txt`; en las conversiones, que el JSON y el YAML cargan los mismos datos), CSV (con `separador.txt`, mismas columnas y número de filas esperado) y Markdown (enlaces, anclas, tablas bien formadas, bloques de código cerrados).
   - bash: el script en una carpeta temporal; se comparan su salida y los ficheros y carpetas que deja. Compatibilidad con **bash 3.2** (el de macOS): ejecutarlos con un bash 3.2 o, al menos, detectar lo que no existe en él (arrays asociativos, `mapfile`, `${var,,}`, `|&`, `&>>`…). Decisión del autor (8 de noviembre de 2026): **siempre** se detectan esas construcciones (no necesita nada instalado) y, **si hay Docker**, además se ejecutan los scripts en la imagen oficial `bash:3.2` de Docker Hub (comprobar antes que existe).
   - Git: comandos en un repositorio temporal; se comparan `git log`, `git status` y el contenido final. Autor, correo y fechas fijos (`GIT_AUTHOR_*`, `GIT_COMMITTER_*`) para que los hashes no cambien, y rama `main`.
   - `curl`: contra un **servidor HTTP local pequeño del kit**, nunca contra internet, con sus partes variables.
   - Condiciones comunes: **sin internet** y **salidas en español** (el kit fija `LC_ALL`, por ejemplo `es_ES.UTF-8`; la máquina necesita ese *locale* y las traducciones de Git).
5. **`herramientas/README.md`** con cada herramienta, sus requisitos y ejemplos.

**Después** (cuando lo pida el curso de Java): separar `verificar_codigo.py` (unas 1.500 líneas) en núcleo y ejecutores (Java, SQL, Node, páginas, Compose, Linux, plataformas…), `generar_modulo.py`, y la prueba de fiabilidad contra el curso de Java original. Y dos opciones de `formato_academia.py`, en vez de un `comprobar_enlaces.py` aparte (decisión del autor, 8 de noviembre de 2026):

- **`--fichero <ruta>`**: comprobar un solo fichero mientras se escribe, más rápido.
- **Todos los cursos a la vez** (por ejemplo, `--todos ../`, que recorre las carpetas hermanas con `curso.json`): detectar los enlaces que se rompen en otros cursos cuando uno renombra un fichero. Hace falta cuando haya más de un curso.

## 4. Decisiones del autor

Resueltas el 8 de noviembre de 2026:

1. **Qué se verifica de los ejercicios del curso inicial.** Solo los programas completos de `codigo/` (los fragmentos del texto no se verifican), y que el bloque del módulo sea idéntico a su fichero:
   - **JSON** (`json`), **XML** (`xml.etree`, bien formado) y **CSV** (`csv`: se lee con su separador y todas las filas tienen las mismas columnas), con la biblioteca de Python. El separador va en un `separador.txt` en la carpeta; si no hay, coma.
   - **YAML**, con PyYAML (decisión 2).
   - **Markdown**: enlaces, anclas y Mermaid, con las herramientas del núcleo.
   - **Lo que falla a propósito**: un `debe-fallar.txt` en su carpeta, y el kit comprueba que falla (misma idea que `termina-con-error.txt` y `no-validar.txt` del curso de Java). Ver `FORMATO.md`, apartado 7.
   - **Terminal y Git**: sesiones con órdenes y su salida esperada, en bash y en una carpeta temporal (sin Docker). Se hacen cuando el curso diga sus ejercicios. En Git cambian los hashes y las fechas: hará falta algo como `salida-variable.txt` del curso de Java o fijar autor y fecha con variables de entorno (`GIT_AUTHOR_DATE`, `GIT_COMMITTER_DATE`…).
2. **PyYAML, solo en el comprobador de YAML.** `formato_academia.py` y el resto de la parte mínima pública usan solo la biblioteca de Python. Si falta PyYAML, el comprobador lo dice y explica cómo instalarlo (`python3-yaml` o `pip install pyyaml`).
3. **Nombres y organización.** Se mantienen los nombres del curso de Java (para compararlas en la prueba de fiabilidad y porque ya se conocen). `formato_academia.py` en `herramientas/`; el resto en `nucleo/`, `servicios/` (vacía de momento) y `lenguajes/`. Los comprobadores de formatos llevan el prefijo `formato_` para no chocar con los módulos de Python (`json`, `csv`…). Los cursos las ejecutan desde su raíz: `python3 ../kit-cursos/herramientas/nucleo/comprobar_enlaces.py`.

Además: **los ajustes de `FORMATO.md` se hacen dentro de la versión 1** mientras no haya nada publicado (las versiones cuentan desde la primera publicación).
