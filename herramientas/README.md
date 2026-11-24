# Herramientas del kit

Las herramientas para comprobar y mantener los cursos de MyOpenAcademy. Viven en el kit y **se ejecutan desde la raíz del curso**, con el kit en la carpeta hermana `../kit-cursos/`, sin copiarlas al curso:

```text
Cursos/
├── kit-cursos/        ← el kit (estas herramientas)
└── curso-micurso/     ← tu curso: ejecuta las herramientas desde aquí
```

Para crear un curso solo hace falta [`formato_academia.py`](#formato_academiapy), con Python y nada más. Las demás son opcionales y cada una dice qué necesita.

## Por dónde empezar

**Al terminar cada módulo**, desde la raíz del curso:

```bash
python3 ../kit-cursos/herramientas/nucleo/generar_ruta_minima.py      # 0. la ruta mínima, si curso.json tiene «ruta_minima»
python3 ../kit-cursos/herramientas/nucleo/generar_indice.py           # 1. el índice, desde curso.json
python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py   # 2. la chuleta global
python3 ../kit-cursos/herramientas/formato_academia.py                # 3. ¿cumple el formato?
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-NN-…/NN-….md   # 4. su código, si tiene
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-NN-…/NN-….md  # 5. sus diagramas, si tiene
```

La ruta mínima va **antes que el índice**, porque el índice marca con 🧭 los módulos de la ruta y enlaza a `RUTA-MINIMA.md`. **En un curso de Java**, antes de la primera verificación (y cada vez que cambie una dependencia de un proyecto de Maven o Gradle), prepara su caché, la única vez que hay red ([`--preparar-java`](#preparar-la-caché---preparar-java)):

```bash
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --preparar-java
```

**Al terminar de escribir un módulo**, antes de todo lo anterior, sus ejercicios en `curso.json` (y el módulo, disponible):

```bash
python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py fase-NN-…/NN-….md
```

**Al cerrar cada fase**, lo mismo con la fase entera, después del último commit: `comprobar_mermaid.py fase-NN-…` y el código **como lo recibirá el alumno**, desde el commit y con Docker ([la verificación completa](#la-terminal-del-kit)):

```bash
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --commit fase-NN-…
```

En el disco de quien escribe puede funcionar lo que en un clon falla: carpetas vacías, permisos o saltos de línea que no están en Git ([`--commit`](#verificar-el-commit---commit)).

**Antes de publicar una versión**, `formato_academia.py` sin errores, con la versión etiquetada en Git (`v1.0.0`): así compara los identificadores con los de la versión anterior. Y `verificar_codigo.py --commit v1.0.0`: el código de la etiqueta que instalará la academia.

## Qué hay

| Herramienta | Qué hace | Necesita |
|---|---|---|
| [`formato_academia.py`](#formato_academiapy) | Comprueba que el curso cumple `FORMATO.md` y se puede instalar en la academia | Python 3.11 o posterior, sin librerías adicionales. Git, solo para comparar con la última versión publicada y mirar los saltos de línea que guarda (si no está, no compara y mira el disco) |
| [`nucleo/verificar_codigo.py`](#nucleoverificar_codigopy) | Comprueba que el código de los módulos coincide con `codigo/` y funciona: scripts de bash, sesiones de terminal (también de Git, y de `curl` con un servidor HTTP local), ficheros JSON, YAML, XML, CSV, TSV, TOML, INI, SVG y Markdown, y que un CSV y su JSON dicen lo mismo; y, desde el kit 1.1.0, **Java** ([el ejecutor de Java](#el-ejecutor-de-java): programas sueltos, Maven, Gradle, JUnit, Spring Boot, JavaFX y Swing) | Python 3.11 o posterior; **PyYAML** para los YAML (en Ubuntu, `python3-yaml`; con pip, `pyyaml`: la única librería de fuera de Python que usa el kit, y solo para eso); **Docker** para la verificación completa (sin él, verifica de forma parcial y avisa). Para Java, la imagen de Java del kit (con Docker) o el JDK, Maven y Gradle del equipo (sin él), e internet solo para `--preparar-java` |
| [`nucleo/generar_ruta_minima.py`](#nucleogenerar_ruta_minimapy) | Genera `RUTA-MINIMA.md` desde `ruta_minima` de `curso.json` | Python 3.11 o posterior |
| [`nucleo/declarar_ejercicios.py`](#nucleodeclarar_ejerciciospy) | Declara en `curso.json` los ejercicios de un módulo o una fase, conservando sus identificadores, y los pone disponibles | Python 3.11 o posterior |
| [`nucleo/generar_indice.py`](#nucleogenerar_indicepy) | Genera `00-indice.md` desde `curso.json` | Python 3.11 o posterior |
| [`nucleo/generar_chuleta_global.py`](#nucleogenerar_chuleta_globalpy) | Genera `99-chuleta-global.md` con la chuleta de cada módulo | Python 3.11 o posterior |
| [`nucleo/reemplazar.py`](#nucleoreemplazarpy) | Aplica sustituciones de texto en varios ficheros a la vez: todas o ninguna | Python 3.11 o posterior |
| [`nucleo/comprobar_mermaid.py`](#nucleocomprobar_mermaidpy) | Comprueba que los diagramas Mermaid se dibujan, con la versión de la academia y con la antigua | **Node.js** (con `npx`) y **Google Chrome o Chromium** (si no está en un sitio habitual, su ruta en la variable `CHROME_PATH`). Comprobado el 8 de noviembre de 2026 con Node 24.22.1 y Chrome en Linux |

Las carpetas:

| Carpeta | Qué guarda |
|---|---|
| `herramientas/` | `formato_academia.py`, la parte pública: un solo fichero, sin dependencias |
| `nucleo/` | Las herramientas comunes a todos los cursos, sacadas del curso de Java original, y `argumentos.py` (la revisión común de sus argumentos) |
| `lenguajes/` | Un comprobador por lenguaje o formato, que usa `verificar_codigo.py`: los ejecutores `bash.py` y `java.py` (desde el kit 1.1.0), y `formato_json.py`, `formato_yaml.py`, `formato_xml.py`, `formato_csv.py` (también TSV y la comparación con su JSON), `formato_markdown.py`, `formato_toml.py`, `formato_ini.py` y `formato_svg.py` |
| `servicios/` | Lo que necesitan los comprobadores para ejecutar: `terminal.py`, la imagen de [la terminal del kit](#la-terminal-del-kit) (`terminal/`), [el servidor HTTP local](#el-servidor-http-local-curl) (`servidor_http.py`) y [la imagen de Java](#la-imagen-de-java) (`java/`, con los programas que usa dentro: `teclear.py`, `aplicacion.py`, `CapturaVentana.java`, `CapturaSwing.java` y `classpath.init.gradle.kts`) |
| `pruebas/` | [Las pruebas](#las-pruebas) de las herramientas, los cursos de ejemplo y [la prueba de fiabilidad con el curso de Java](#la-prueba-de-fiabilidad-con-el-curso-de-java) |

No hay un `comprobar_enlaces.py` aparte: los enlaces y las anclas los comprueba `formato_academia.py`.

## Lo común a todas

- **`--help`** (o `-h`) muestra la ayuda de la herramienta, el mismo texto que hay al principio de su fichero.
- Sin argumentos, trabajan con **el curso de la carpeta actual**. Las que lo admiten reciben una carpeta o un fichero (una fase, un módulo, otro curso).
- **Códigos de salida**: **0** si todo está bien (aunque haya avisos); **1** si hay algún error (o, con `--comprobar`, si un fichero generado no está al día); **2** si los argumentos están mal (una opción desconocida o una ruta que no existe), sin hacer nada. Así una ruta mal escrita no da un «✅» falso por haber revisado 0 ficheros (`nucleo/argumentos.py`, sacado del curso de Java; las rutas se buscan desde la carpeta actual, no desde la del script).
- **Cada mensaje dice el fichero, la línea y qué pasa**, como `fichero.md:120: ERROR: …`. Un **ERROR** es lo que `FORMATO.md` dice con «debe» (el curso no se instala o el código no funciona); un **AVISO**, lo que dice con «conviene» o lo que no se ha podido comprobar.

## `formato_academia.py`

Comprueba, sin ejecutar nada del curso, todo lo del apartado 13 de [`FORMATO.md`](../FORMATO.md):

- **`curso.json`**: campos, identificadores (forma, que no se repitan y que no desaparezca ninguno publicado sin su equivalencia), partes, proyecto y equivalencias; que cada fichero declarado existe y cada módulo de las carpetas de fase está declarado. Los módulos con `"disponible": false` y los retos con `"retos_disponibles": false` no tienen por qué existir. Desde el kit 1.1.0 (revisión 1.1 de `FORMATO.md`, apartado 3.2), además:
  - **Partes**: cada parte tiene al menos una fase (`"fases": []` es un error), cada fase está en una sola parte, y cada parte es un tramo de fases **seguidas y en el orden del curso**, con las partes una tras otra. A: [f1, f2] y B: [f3] vale; A: [f3, f1] («sus fases no van en el orden del curso») o A: [f1, f3] con B: [f2] («sus fases no van seguidas»), no. La academia copia estas reglas en su importador, para que ningún curso pase el kit y falle al instalarse.
  - **`ruta_minima`** (opcional): un objeto con `modulos` (obligatorio: al menos uno, sin repetir y que existan), `etapas` (opcional: etapas del proyecto que existan) y `plantilla` (opcional: un `.md` de la raíz del curso que exista). En la plantilla, solo los huecos `{{resumen}}`, `{{modulos}}` (obligatorio), `{{proyecto}}` y `{{consultas}}`: cualquier otro es un error, con su línea. Si hay `ruta_minima` y falta `RUTA-MINIMA.md`, aviso ([`generar_ruta_minima.py`](#nucleogenerar_ruta_minimapy) lo genera).
  - **`academia_minima`** (opcional): la versión mínima de la academia que necesita el curso, con la forma `MAYOR.MENOR.PARCHE` (`"1.1.0"`); otra forma es un error. Lo usa, por ejemplo, un curso de Java cuyos ZIP de proyecto solo da bien la academia 1.1.0.
- **Títulos en texto plano** del curso, las fases, los módulos, los ejercicios y los retos.
- **Cada módulo disponible**: título igual al de `curso.json`, cabecera (`Conviene saber antes`, `Tiempo estimado` y `Nivel`), las ocho secciones en orden, subapartados numerados donde toca, los ejercicios con los títulos y el orden de `curso.json`, sus pistas antes de la solución, la solución, las preguntas de repaso con su respuesta y la navegación del final.
- **Retos** de cada fase, **etapas** del proyecto, **glosario** (el común del curso inicial, que no le puede faltar, y el propio de cualquier curso: letras y términos en orden alfabético español, con la ñ entre la n y la o, cada término en su letra, y ningún término repetido, que es un error porque cada término se define una vez), **`00-indice.md`** (sus fases, las de `curso.json`) y **ficheros obligatorios**.
- En todos los Markdown del curso (salvo `codigo/`, `herramientas/` y los ficheros de trabajo `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md`): **enlaces** y sus **anclas** (también a otros cursos), **imágenes**, **diagramas Mermaid**, **HTML**, bloques de código sin cerrar y huecos `[RELLENAR: …]` de las plantillas.
- **Lo de `codigo/` que no viaja con Git** (lo único que mira de esas carpetas), todo avisos: el fallo real lo da [`verificar_codigo.py --commit`](#verificar-el-commit---commit). **Carpetas vacías** (o con solo ficheros ignorados), solo la de más arriba: el aviso propone crearla en la sesión con `mkdir` y, si no, un `.gitkeep` (que `ls -a`, `find` y `du` muestran y que hace fallar un `rmdir`). **Scripts lanzados con `./`** en un `sesion*.txt` (también detrás de `&&`, `||`, `;`, `|` o `(`) que Git no guarda como ejecutables, en la línea de la sesión; no avisa si la sesión hace un `chmod` de ese script (antes o después: es lo que enseña, como un «Permiso denegado» a propósito), si se lanza con `bash` ni si el script lo crea la sesión. **Permisos del disco que un clon no tendría**: un fichero sin lectura o escritura para su propietario, o ejecutable en el disco y no en Git (o al revés; no con `core.fileMode=false`); solo los del propietario, porque los del grupo dependen del equipo. En Windows no se miran los permisos. **Saltos de línea**: aviso por cada fichero de texto con CRLF, con la primera línea que lo tiene, y un aviso en `.gitattributes` si algún fichero no saldría con LF en un clon en Windows (con `core.autocrlf=true`, lo normal en Git for Windows), porque falta `* text=auto eol=lf`. Con Git mira **lo que guarda Git** (`git ls-files --eol`: el índice y, en los ficheros nuevos, lo que guardaría al añadirlos), no el disco, porque la academia instala desde un commit; sin Git, el disco. Los marcados con `-text` en `.gitattributes` (CRLF a propósito) y los binarios no avisan.

```bash
python3 ../kit-cursos/herramientas/formato_academia.py            # el curso de la carpeta actual
python3 ../kit-cursos/herramientas/formato_academia.py ../curso-x # otro curso
```

Al final, un resumen:

```text
fase-01-que-es-programar/01-que-es-programar.md:1275: ERROR: no existe ../00-indice.md
curso.json:16: AVISO: fase «inicial.fase.herramientas»: los retos todavía no están escritos

Curso «inicial» 0.1.0: 8 fases, 31 módulos (4 disponibles), 36 ejercicios; sin versiones etiquetadas todavía.
❌ El curso no cumple FORMATO.md (versión 1): 1 error y 1 aviso. No se puede instalar.
```

**Detalles:**

- **Enlaces a lo que aún no está escrito.** Un enlace a un módulo con `"disponible": false` (o a unos retos con `"retos_disponibles": false`) es un **aviso**, para revisarlo cuando se escriba; si lleva ancla, avisa de que no se podrá comprobar hasta entonces. Un enlace a un fichero que no existe y que no está previsto en `curso.json` es un **error**.
- **Enlaces a otros cursos** (`https://github.com/myopenacademy/<curso>/blob/main/…`): se traducen a la carpeta hermana `../<curso>/` y se comprueban el fichero y el ancla; un módulo pendiente de ese curso (según su `curso.json`) es un aviso. Si la carpeta hermana no está, avisa de que no lo ha podido revisar. Deben apuntar a la rama `main`.
- **El texto de cada «📁 Código» y su destino**, la misma carpeta (desde el kit 1.1.0, `FORMATO.md` 7): si no, **aviso** («el texto dice «…» y el enlace lleva a «…»»). Importa en los proyectos de Maven y Gradle, en los que la academia da el ZIP del proyecto entero, pero el enlace y su texto dicen la carpeta del fichero, para leerlo en GitHub (en el curso de Java salen 20, en sus módulos 01.05 y 01.06).
- **Código en línea como en CommonMark** (desde el kit 1.1.0): un tramo de comillas invertidas se abre y se cierra con otro igual de largo, y nunca empieza a mitad de otro tramo. Así, unas comillas invertidas sin cerrar son texto y lo que viene detrás se lee como lo lee la academia (en el 13.02 del curso de Java, un `<template>` daba un error de HTML que la academia no daba).
- **Anclas**: las que genera GitHub a partir del encabezado, con la misma regla que `comprobar_enlaces.py` del curso de Java (minúsculas, sin signos, espacios convertidos en guiones; los repetidos, con `-1`, `-2`…), conservando el texto del código en línea (`` `Page<T>` `` da `paget`).
- **HTML**: el que admite la academia, como su saneador (visto en Code Academy el 8 de noviembre de 2026):
  - Se admiten tal cual `details`, `summary`, `code`, `kbd`, `br`, `sup`, `sub`, `em`, `strong`, `del`, tablas, listas, párrafos y encabezados, sin atributos (salvo `align` en las celdas, `start` en `ol` y `class="language-…"` en `code`).
  - El formato sin efecto (`span`, `div`, `u`, `b`, `i`…) y los `<a>` los quita al instalar y deja su texto: **aviso**.
  - Cualquier otra etiqueta (`script`, `iframe`, `img`, `style`…) y cualquier otro atributo (`onclick`, `style`, `open`…) hacen fallar la instalación: **error**.
- **Mermaid**: sin negrita ni cursiva en las etiquetas (tampoco `<b>` o `<i>`), solo las entidades `&quot;`, `&lt;`, `&gt;` y `&amp;`, y sin directivas, *frontmatter*, `click`, `url()` ni `@import`. Que el diagrama se dibuje lo comprueba [`comprobar_mermaid.py`](#nucleocomprobar_mermaidpy).
- **Listas de tareas** (`- [ ]`, `- [x]`) fuera de los bloques de código: **aviso**, porque la academia todavía no las dibuja (`FORMATO.md` 10.6; desde el 9 de noviembre de 2026, hasta que la academia avise de que ya las dibuja).
- **Correos fuera del código** (`FORMATO.md` 10.7): **aviso** por `<ana@example.com>` o `<mailto:…>` fuera de los bloques y fragmentos de código (CommonMark y GitHub los convierten en un enlace `mailto:`, que la academia no admite), por un correo suelto (`ana@example.com`, que GitHub enlaza y la academia deja como texto; no cuenta seguido de `:`, como `git@github.com:usuario/repo.git`, ni dentro de una URL) y por cada enlace `[texto](mailto:…)`. Escrito en código (`` `Ana García <ana@example.com>` ``) o escapado (`\<ana@example.com>`), no avisa (desde el 16 de noviembre de 2026, pedido por la academia).
- **Repositorios de Git dentro de `codigo/`** (`FORMATO.md` 7): una carpeta `.git` en el disco o un submódulo que Git guarda (modo 160000) es un **error**: Git no guarda su contenido, así que no llega a un clon ni a la academia. Los repositorios se crean dentro de la sesión (`git init`). Las demás carpetas ocultas, como `.github/`, son normales.
- **Ficheros `.env` de `codigo/`** (`FORMATO.md` 7): solo se admite `.env.example`, en minúsculas. Cualquier otro (`.env`, `.env.local`, `.env.production`…) que Git guarda (o guardaría) es un **error**: la academia lo excluye y puede llevar secretos; si el ejemplo lo necesita, se crea en la sesión (`cp .env.example .env`). Uno que Git ignora, **aviso** (no llega a un clon, pero está en el disco). En `.env.example`, **aviso** por cada valor con pinta de secreto real, con la línea y la variable, nunca el valor: formatos conocidos (claves privadas, AWS `AKIA…`, GitHub `ghp_…`/`github_pat_…`, GitLab, Slack, Stripe, Google `AIza…`, claves de API de IA `sk-…`, JWT; a 16 de noviembre de 2026), una contraseña dentro de una URL (`postgres://app:clave@…`) o una clave de 16 caracteres o más, con letras y cifras mezcladas, en una variable de secretos (`SECRET`, `TOKEN`, `PASSWORD`, `KEY`, `CONTRASENA`, `CLAVE`…). Los valores que se ven falsos no avisan: vacíos, o con `cambia`, `aquí`/`aqui`, `tu-`, `ejemplo`, `example`, `changeme`, `xxx`, `…`, `<…>` o `${…}`.
- **Versiones publicadas**: si el curso tiene etiquetas `vX.Y.Z` en Git, compara los identificadores de la última con los de ahora; cada uno que haya desaparecido necesita su equivalencia (`FORMATO.md`, apartado 11.2).

## `nucleo/verificar_codigo.py`

El núcleo de `verificar_codigo.py` del curso de Java, con las mismas convenciones ([`FORMATO.md`, apartado 7.1](../FORMATO.md#71-ficheros-de-verificación-y-salidas-en-el-texto)). Cada lenguaje o formato tiene su comprobador en `lenguajes/`; los que ejecutan código (los **ejecutores**: bash y, desde el kit 1.1.0, [Java](#el-ejecutor-de-java)) están en una lista del núcleo, y para cada fichero manda el primero que diga que es suyo.

```bash
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py                       # todo el curso
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-03-herramientas  # una fase (o un módulo)
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --commit              # el último commit, como un clon
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --sin-docker          # en la bash del equipo
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --preparar-java       # la caché de Java (con red)
```

- **Cada bloque seguido de «📁 Código»** tiene que ser idéntico a un fichero de su carpeta (sin contar los espacios del final de las líneas ni las líneas en blanco del principio y del final). Si no, dice cuál es el más parecido y la primera línea distinta. Desde el kit 1.1.0, el bloque **puede enseñar un fichero de verificación** (las peticiones de un `peticiones.txt`, lo que se teclea en un `entrada.txt`…; `FORMATO.md` 7.1): se compara con él como con cualquier otro, cuenta como mostrado y no se ejecuta. Va en el ZIP del alumno, así que lo que ve en el bloque también lo puede descargar. El fichero se busca solo en la carpeta enlazada y sus subcarpetas, nunca en el resto del proyecto.
- **Un script de bash** (`.sh`) se ejecuta con `bash fichero.sh` en una copia de su carpeta, con `args.txt` y `entrada.txt`, y tiene que terminar con 0; su salida, la de «**Salida:**». Con `termina-con-error.txt`, tiene que terminar con otro código, y su salida de error, la de «**Salida de error:**».
- **Una sesión** («**En tu terminal** (`sesion.txt`):», su bloque ` ```text ` y su «📁 Código»): se teclea cada orden de `sesion.txt` en una bash con terminal de 100 columnas, con el indicador `$ `, en una carpeta personal con los demás ficheros de la carpeta; la pantalla final tiene que ser la del bloque. Como en Java, `@ctrl-c 3` tras una orden que no termina sola pulsa Ctrl+C a los 3 segundos. Las sesiones de **Git** son sesiones como las demás, con [el reloj de Git](#el-reloj-de-git). Los `sesion*.txt` de la carpeta no se copian a la terminal (un `ls` no los enseña).
- **Sesiones encadenadas** (`sesion-1.txt`, `sesion-2.txt`…, `FORMATO.md` 7.1): las de un ejemplo que el alumno hace una detrás de otra. Se teclean todas, en orden, en la misma terminal (el mismo contenedor): cada una encuentra los ficheros y el reloj de Git como los dejó la anterior, pero **arranca en una bash nueva** en la carpeta del ejemplo, sin el `cd` ni las variables de la anterior (el alumno puede cerrar la terminal entre una y otra, y así una sesión que depende sin decirlo de un `cd` anterior falla). Cada bloque se compara con la pantalla de la suya. Si una falla, el error lo dice en su bloque, y las de detrás dicen «no se ha podido teclear: va encadenada detrás de `sesion-2.txt`, que falla». Error si la numeración tiene saltos o ceros delante; aviso por cada sesión encadenada que ningún bloque muestra (se teclea igual). Las sueltas (`sesion.txt`, `sesion-<nombre>.txt`) siguen empezando desde cero. En `formato_academia.py`, el `chmod` de un script en cualquier sesión de la serie vale para las demás.
- **`curl`**: si la carpeta tiene un `servidor.json`, la sesión o el script tienen [un servidor HTTP en `localhost`](#el-servidor-http-local-curl) que responde lo que dice.
- **`salida-variable.txt`**: lo que encaja con cada expresión regular se sustituye por `…` en las dos salidas antes de compararlas. En Java, si la carpeta no tiene uno, vale el que está junto al `pom.xml` de su módulo, también para la «**Salida de las pruebas:**» ([el ejecutor de Java](#el-ejecutor-de-java)).
- **Java** (`.java`): [el ejecutor de Java](#el-ejecutor-de-java), más abajo.
- **Los ficheros de datos** de cada carpeta enlazada se comprueban con Python (no necesitan Docker), cada error con su línea:
  - **JSON** (`formato_json.py`): que se lee.
  - **YAML** (`formato_yaml.py`, con PyYAML): que se leen todos sus documentos. Si falta PyYAML, avisa de que no los ha podido comprobar.
  - **XML** (`formato_xml.py`): que está bien formado (no lo valida contra un esquema).
  - **CSV y TSV** (`formato_csv.py`): que se lee con el separador de `separador.txt` (`;`, `|` o `tabulador`; si no hay, la coma; un `.tsv`, siempre con tabulador), sin comillas sin cerrar, y con las mismas columnas en cada fila que en la cabecera. En **UTF-8 sin BOM** (un BOM es un error), salvo que la carpeta tenga un **`codificacion.txt`** con el nombre de `iconv` (`WINDOWS-1252`, `ISO-8859-15`…): entonces se convierte desde ella y se comprueba igual. Si con `codificacion.txt` el fichero resulta estar en UTF-8 (y no solo en ASCII), es un error: lo más probable es que ya se convirtiera y sobre el `codificacion.txt`.
  - **TOML** (`formato_toml.py`, con `tomllib`): que se lee (TOML 1.0).
  - **INI** (`formato_ini.py`, con `configparser`): INI no tiene norma, así que se comprueba lo que aceptan casi todos los programas: cada clave dentro de una sección `[nombre]`, con `=` o `:`, sin secciones ni claves repetidas, y comentarios con `;` o `#`.
  - **SVG** (`formato_svg.py`): XML bien formado con la raíz `<svg xmlns="http://www.w3.org/2000/svg">` (sin el `xmlns`, el navegador no lo dibuja como imagen). Las imágenes se comprueban siempre: `debe-fallar.txt` no les afecta.
  - **Markdown** (`formato_markdown.py`, los `.md` de `codigo/`, como el README de un proyecto): enlaces relativos y anclas que existen, tablas con su fila separadora y las mismas columnas en cada fila, y bloques de código cerrados. Los enlaces a internet no se comprueban (sin red). Si el `.md` empieza por una **cabecera YAML entre `---`** (una plantilla de *issue* de GitHub en `.github/ISSUE_TEMPLATE/`), la cabecera debe cerrarse con otra `---` y ser YAML válido con claves y valores (con PyYAML), con la línea de cada error; el resto se comprueba como Markdown. Las carpetas ocultas como `.github/` se comprueban y se copian a la terminal como las demás (y las que empiezan por `_`, como el `_data/` de Jekyll). Las etiquetas de **Liquid** de Jekyll (`{{ … }}`, `{% … %}`) son texto, porque el kit no ejecuta Jekyll: los `|` de sus filtros (`{{ x | upcase }}`) no cuentan como columnas de una tabla (se cuenta como lo deja Jekyll: `{{ }}`, un valor; `{% %}`, nada) y un enlace cuyo destino lleva Liquid (`[Ver]({{ ruta.url }})`) no se comprueba.
  - **`debe-fallar.txt`**: si la carpeta lo tiene, **todos** sus ficheros de datos tienen que fallar (están mal a propósito); uno válido es un error. Cada ejemplo roto, en su propia carpeta.
  - **Conversiones**: un `.json` y un `.yaml` con el mismo nombre en la misma carpeta tienen que cargar los mismos datos. Un `.csv` (o `.tsv`) y un `.json` con el mismo nombre, también, con las reglas de `FORMATO.md` 7.1 (pedidas por el curso inicial para su reto 3 de la fase 4): el JSON, una lista con un objeto por fila de datos y en el mismo orden; cada objeto, con exactamente las claves de la cabecera; y cada campo según el tipo de su valor en el JSON (un texto, igual letra a letra; un número, escrito como `-?(0|[1-9][0-9]*)(\.[0-9]+)?` y con el mismo valor; un booleano, `sí`/`true` o `no`/`false` en minúscula; `null`, el campo vacío, que solo vale como `null`; una lista o un objeto, error). Cada error dice la línea del CSV, la fila y la clave. El resumen cuenta cuántos CSV se han comparado.
- **bash 3.2, la de macOS**: cada `.sh` no puede usar lo que no existe en ella (arrays asociativos, `mapfile`, `${var,,}`, `|&`, `&>>`, `[[ -v ]]`, `{1..10..2}`…); esa búsqueda funciona siempre. Con Docker, además, cada script se **ejecuta con bash 3.2.57** y su salida y su código de salida tienen que ser los de bash 5: así salen también las diferencias que la búsqueda no ve (un `printf '%(%Y)T'`, de bash 4.2, falla en la 3.2). Cada pasada, en un contenedor limpio: un script que deja algo creado se comporta igual en las dos.
- **Lo que no comprueba de macOS**: que `sed`, `date`, `ls`, `grep`… se comporten igual. En macOS son las versiones de **BSD** y en la terminal del kit, las de **GNU** (Linux), con opciones y salidas distintas (`sed -i ''`, `date -v`…). Eso lo cubren los avisos del texto de cada módulo, no el kit.
- **También**: error por cada fichero enlazado que Git ignora (no llegaría a un clon del curso), y aviso por cada carpeta de `codigo/` que ningún módulo enlaza y por cada script que ningún bloque muestra.

### Verificar el commit (`--commit`)

Sin `--commit` se verifican los ficheros del disco, tal como están: lo normal mientras se escribe un módulo. Con `--commit [referencia]` (`HEAD` si no se dice otra; un commit, una rama o una etiqueta: `--commit v1.0.0` o `--commit=v1.0.0`) se verifica **el curso como lo recibe el alumno**:

- Se saca esa versión con `git archive` a una carpeta temporal y se verifica esa copia. `git archive` solo lee: no toca el repositorio del curso (`git worktree` escribiría en su `.git`).
- La copia es como un clon: saltos de línea según `.gitattributes`, solo los permisos que guarda Git (ejecutable o no), sin carpetas vacías, sin lo que Git ignora y sin lo que no tiene commit. `docker cp` conserva los permisos al pasarla a la terminal del kit, así que lo que fallaría en un clon falla aquí.
- Si hay cambios sin commit, lo dice al principio: no entran. Una ruta que no está en ese commit termina con 2.
- Los mensajes dicen las rutas del curso, como siempre. El curso puede ser una subcarpeta de su repositorio (como los cursos de ejemplo del kit).
- Nada de `codigo/` puede llevar `export-ignore` en `.gitattributes`: `git archive` lo dejaría fuera (`FORMATO.md`, apartado 7).

### La terminal del kit

Donde se ejecutan los scripts y las sesiones (`servicios/terminal.py`).

**Con Docker, la verificación completa.** Un contenedor de la imagen `servicios/terminal/Dockerfile` (se llama `kit-terminal:<huella del Dockerfile>` y se construye la primera vez, en unos minutos y con internet), **sin red** (`--network none`), con el nombre de máquina `ordenador`, la persona `alumno` (con `USER`, `LOGNAME` y `SHELL`, como tras un inicio de sesión) y la configuración de Git de todo el sistema (nombre «Ana García», `ana@example.com` y la rama `main`; una sesión que enseña `git config --global` la cambia, como en cualquier equipo). Los ficheros de la carpeta se copian con una fecha fija (15 de enero de 2026, 10:00) y con **permisos fijos**, como los da Git al clonar con la umask más común (022): ficheros `644` (`755` si son ejecutables) y carpetas `755`; así `ls -l` no cambia, ni con la umask de cada máquina (con 002, Git deja `rw-rw-r--`) ni con `--commit` (`git archive` pone `664` y `775`). Un permiso distinto que necesite un ejemplo (un fichero de solo lectura) se pone con `chmod` en la sesión. Fija todo lo que cambia la salida de una orden, así que es **la misma en cualquier máquina** (versiones comprobadas el 16 de noviembre de 2026; las más recientes, debajo de la tabla):

| Pieza | Versión | De dónde y por qué |
|---|---|---|
| Ubuntu | 26.04.1 LTS | `ubuntu:26.04` fijada por su huella (`sha256:6a06111c…`) |
| Git | **2.56.0** | La que enseña el curso inicial (Ubuntu 26.04 trae la 2.53.0). Compilada del código oficial de kernel.org, comprobando su SHA-256 publicado, **con sus traducciones** (gettext): sin ellas, Git responde en inglés. Instalada **como el paquete de Ubuntu** (`prefix=/usr`, `gitexecdir=/usr/lib/git-core`): la configuración del sistema en `/etc/gitconfig`, `git --exec-path` en `/usr/lib/git-core` y nada en `/usr/local`. Con **`NO_RUST=1`**: en Git 2.56 la parte en Rust es opcional (lo dice su `Makefile`) y no cambia los mensajes. **Desde Git 3.0, Rust será obligatorio y la imagen tendrá que instalarlo** (`cargo`) para compilarlo. |
| bash | 5.3.9 | La de Ubuntu 26.04 |
| bash 3.2 | **3.2.57** | La de macOS, como `bash-3.2`. Compilada del código oficial de GNU: su firma (`.sig`) se verificó el 8 de noviembre de 2026 con la clave de Chet Ramey, que mantiene bash (`7C01 35FB 088A AF6C 66C6 50B9 BB58 69F0 64EA 74AB`), y el Dockerfile comprueba su SHA-256. |
| Idioma y hora | `es_ES.UTF-8`, Europe/Madrid | Las salidas del curso están en español |
| coreutils | **GNU 9.7** (`gnu-coreutils` 9.7-3ubuntu2.1, con `coreutils-from-gnu`) | `ls`, `cp`, `mkdir`, `date`…: las de Git Bash y casi todos los Linux, con sus mensajes y sus fechas en español y el orden de `ls` de un sistema en español. Ubuntu 26.04 trae por defecto las **uutils** (Rust, 0.10.0), con mensajes en inglés o a medias, fechas en inglés y las mayúsculas primero en `ls`: se cambian por las de GNU (decisión del autor, 9 de noviembre de 2026, a partir de lo que vio el curso inicial al escribir su fase 3) |
| Traducciones del sistema | `language-pack-es-base` 1:26.04+20260818 | Las de bash, coreutils, grep, sed, tar…: sin ellas, «bash: gti: orden no encontrada» o los errores de `ls` salen en inglés, como no salen en un Ubuntu en español (pedido por el curso inicial, 9 de noviembre de 2026) |
| Reloj de Git | Desde el 15 de enero de 2026, 10:00 | `servicios/terminal/git-reloj`, en `/usr/bin/git` (también sin Docker, delante del `PATH`) |

**Las más recientes** (16 de noviembre de 2026). Git: la 2.56.1, un parche (la terminal da las salidas de la 2.56.0; según la regla común, se sube con la versión menor, la 2.57, no con cada parche). coreutils: la 9.12 de GNU, pero la terminal lleva la del paquete de Ubuntu 26.04 (9.7), que es la que tiene quien usa Ubuntu. curl: la 8.23.0, pero la terminal lleva la de Ubuntu 26.04 (8.18.0). Ubuntu 26.04.1 es la más reciente de la 26.04. bash 3.2.57 es a propósito la de macOS (la más reciente de bash es la 5.3).

**La lista de lo instalado.** Lo que no está en la tabla (`file`, `tree`, `curl`, `jq`, `python3` y sus dependencias) viene de Ubuntu el día en que se construye la imagen, sin fijar (decisión del autor, 9 de noviembre de 2026: se fijará si un día da un problema real). Por eso la imagen guarda, al construirse, la lista de todo lo instalado con sus versiones y la fecha (`/usr/share/kit-terminal/versiones.txt`). Si un día cambia una salida, se compara la de las dos máquinas:

```bash
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --versiones > versiones-aqui.txt
```

`--versiones` enseña la lista de la terminal y, desde el kit 1.1.0, también la de [la imagen de Java](#la-imagen-de-java) (`/usr/share/kit-java/versiones.txt`: el JDK, Maven, Gradle, las letras y Pango). La primera vez construye las dos imágenes, si no están.

Si cambia una versión (por ejemplo, el curso pasa a enseñar otra de Git), se cambia en el `Dockerfile` (con su SHA-256) y en esta tabla: la huella del `Dockerfile` cambia y la imagen se reconstruye sola.

**Por qué bash 3.2 se compila en la imagen y no se usa la imagen oficial `bash:3.2.57`** (que existe en Docker Hub): la oficial es de Alpine, con las herramientas de BusyBox en lugar de las de GNU, así que `ls`, `sort` o `grep` darían salidas distintas y cada script daría diferencias falsas. Con las dos bash en la misma imagen y las mismas herramientas, una diferencia es solo del bash.

#### El reloj de Git

Para que los identificadores de los commits salgan siempre iguales y `git log` parezca un historial real (decisión del autor, 8 de noviembre de 2026), los commits de cada sesión o script tienen **fechas fijas que avanzan**: el primero, el 15 de enero de 2026 a las 10:00 (la fecha de los ficheros copiados); cada uno, un minuto después del anterior. Lo hace `git-reloj`, un script pequeño que hace de `git`: a las órdenes que pueden crear commits (`commit`, `merge`, `rebase`, `cherry-pick`, `revert`, `stash`, `tag`…) les da la fecha del reloj y, si terminan bien, lo adelantan un minuto (un `git commit` que no tiene nada que confirmar no lo adelanta). Si la sesión pone sus propias fechas (`GIT_AUTHOR_DATE`…), se respetan. En la imagen está en **`/usr/bin/git`**, donde está el `git` de un Ubuntu, así que `command -v git`, `type git` y `which git` dicen lo mismo que en el equipo del alumno; el `git` de verdad está fuera del `PATH`, en `/usr/lib/kit/git`. (Se descartó fijar las fechas con variables de entorno o con la configuración: tendrían que cambiar tras cada commit, con *hooks* de Git que una sesión que los enseñe dejaría a la vista.) Sin Docker, el reloj va en una carpeta temporal delante del `PATH`, y `command -v git` la dice.

**Sin paginador.** En la terminal, `GIT_PAGER` y `PAGER` son `cat`: con una salida que no cabe en pantalla, `git log` o `man` se quedarían esperando una tecla (en el equipo del alumno, `less` la pide). Con una que cabe, se ve igual.

**Lo que coreutils no traduce.** La traducción al español de las coreutils de GNU que trae Ubuntu (`language-pack-es-base`) es de coreutils 8.23 (2014: «Project-Id-Version: GNU coreutils 8.23-pre1»), así que los mensajes que han cambiado desde entonces salen en inglés, en parte: `mkdir: cannot create directory ‘docs’: El archivo ya existe` (el final, «El archivo ya existe», viene del sistema). Es igual en cualquier sistema con las GNU en español; el curso lo muestra tal cual, con una nota general.

**Lo que Git no traduce**, aunque el sistema esté en español (es así en cualquier Git, también en el de Ubuntu): las fechas (`Date:   Thu Jan 15 10:00:00 2026 +0100`) y el resumen de cambios (`1 file changed, 1 insertion(+)`). El curso las muestra tal cual.

#### El servidor HTTP local (`curl`)

`servicios/servidor_http.py`, solo con la biblioteca de Python. Si la carpeta de una sesión o un script tiene un **`servidor.json`** (su formato, en [`FORMATO.md` 7.1](../FORMATO.md#71-ficheros-de-verificación-y-salidas-en-el-texto)), la terminal lo arranca **antes** de la sesión o el script y lo para **después** (para unas sesiones encadenadas, uno para toda la serie, como una API que sigue ahí). Es genérico: cada ejemplo describe sus rutas (método, ruta, código de estado, cabeceras y cuerpo) y el servidor responde eso, siempre igual.

- **Con Docker**, dentro del contenedor, sin red: solo `localhost`, en `127.0.0.1` y `::1` a la vez (así `curl localhost` conecta a la primera, sin un intento fallido que se vería con `-v`). Corre como `nobody`, desde `/opt/kit-servidor/`, fuera de la carpeta personal. `servidor.json` no se copia a la carpeta personal.
- **Sin Docker**, en el equipo, en el puerto que diga el `servidor.json` (8080 si no dice otro): si está ocupado, la sesión falla con «el puerto 8080 ya está en uso». `localhost` queda fuera de los proxies muertos. (Las [pruebas](#las-pruebas) del kit, desde la 1.1.0, usan un puerto libre que elige el sistema: ya no fallan si el 8080 del equipo está ocupado, por ejemplo con la academia en local.)
- **Respuestas deterministas**: `HTTP/1.1`, las cabeceras de la ruta, `Content-Type` y `Content-Length`; ni `Date` ni `Server`. 404 y 405 propios, `HEAD` como `GET`, y lo que envía la petición se ignora.
- **`curl` no está fijado** en la imagen (es el de Ubuntu: 8.18.0, a 16 de noviembre de 2026). Su salida con `-i` o `-s` no depende de la versión; con `-v`, sí: no se verifica (`FORMATO.md` 7.1).
- Cada `servidor.json` de una carpeta enlazada se comprueba aunque ninguna sesión lo use; cada error, con su línea.

Para probar un `servidor.json` a mano:

```bash
python3 ../kit-cursos/herramientas/servicios/servidor_http.py servidor.json --comprobar   # solo comprueba
python3 ../kit-cursos/herramientas/servicios/servidor_http.py servidor.json               # escucha hasta Ctrl+C
```

#### Sin Docker, la verificación parcial

Sin Docker (o con `--sin-docker`), en la bash del equipo, en una carpeta temporal que hace de carpeta personal, con el español, la hora de Madrid, la misma configuración de Git y el reloj de Git. Pero:

- **La red no se puede cortar** sin permisos de administrador (`unshare --net` necesita espacios de nombres de usuario, que Ubuntu limita): solo se apuntan los proxies a una dirección muerta, que para `curl`, `git` y los gestores de paquetes, pero no a un programa que abra la conexión por su cuenta.
- Las versiones son las del equipo, así que una salida puede cambiar.
- No hay bash 3.2: solo la búsqueda de lo que no existe en ella.

Lo dice al final de cada verificación. **Para cerrar una fase, verifica con Docker.**

### El ejecutor de Java

`lenguajes/java.py`, desde el kit 1.1.0, para los cursos de Java. Sale de `verificar_codigo.py` del curso de Java original, con sus mismas reglas y comparaciones, para que el kit dé el mismo resultado ([la prueba de fiabilidad](#la-prueba-de-fiabilidad-con-el-curso-de-java) lo comprueba). Sus ficheros de verificación y lo que se escribe en el texto están en [`FORMATO.md` 7.1, «Los de Java»](../FORMATO.md#71-ficheros-de-verificación-y-salidas-en-el-texto). El docstring de `java.py` lo explica entero.

**Antes de verificar un curso de Java por primera vez**, prepara su caché con [`--preparar-java`](#preparar-la-caché---preparar-java): la verificación no tiene red.

**Qué se ejecuta.** Cada `.java` con `main` que muestra un bloque seguido de «📁 Código». Los que no tienen `main` (una clase auxiliar, `package-info`, `module-info`) solo se comparan con su bloque.

- **Un programa suelto**: `java Fichero.java` (el lanzador de código fuente) desde una copia de su carpeta, con las opciones de `opciones-java.txt` delante del fichero, los argumentos de `args.txt` detrás y `entrada.txt` como entrada estándar. Si tiene `package` y está en las carpetas de su paquete (`src/es/tienda/app/Main.java` con `package es.tienda.app;`), se copia desde la raíz de las fuentes (`src/`, sin salir de `codigo/`) y se ejecuta desde la carpeta del programa, como en su sitio: el lanzador (JDK 22 o posterior) encuentra las demás clases desde esa raíz.
- **Un programa de un proyecto de Maven** (hay un `pom.xml` en su carpeta o más arriba, sin salir de `codigo/`): el proyecto se construye **una vez por verificación** (`mvn package`, pruebas incluidas) y la clase se ejecuta con su classpath (`java -cp … paquete.Clase`) desde la carpeta de su módulo, la del `pom.xml` más cercano, como en IntelliJ. La raíz es el `pom.xml` más alto (un multimódulo).
- **Un programa de un proyecto de Gradle**, igual: `build.gradle.kts` o `build.gradle`, con la raíz en la carpeta más exterior con `settings.gradle.kts` o `settings.gradle` (el de Groovy también), sin salir de `codigo/`; **sin `settings.gradle*`**, Gradle (9.8.2) construye la carpeta del `build.gradle*` como un proyecto de un solo módulo, y esa es la raíz. Se construye con `gradle build` y el classpath lo da la tarea de `servicios/java/classpath.init.gradle.kts`. Gradle va siempre **sin demonio** (`--no-daemon`), para que no se quede nada vivo en el contenedor del proyecto.
- **Maven y Gradle mezclados** (uno dentro del otro): el programa se construye con la herramienta de su módulo (su `pom.xml` o `build.gradle*` más cercano; en la misma carpeta, Maven) desde su raíz, y a la terminal se copia el proyecto de [`FORMATO.md` 7](../FORMATO.md#7-el-código), el que entrega la academia en el ZIP: el más exterior de todos dentro de `codigo/`.
- `entrada.txt`, `args.txt` y `opciones-java.txt` pueden ir junto al fichero o en la raíz de su módulo; `salida-variable.txt`, también junto al `pom.xml`.
- Sin pantalla, con la salida en UTF-8 y en español, y con un tiempo máximo. El curso nunca se toca: `target/`, `build/` y `.gradle/` quedan en la copia.

**Qué se compara.** Lo que viene tras el enlace «📁 Código» (o más abajo, tras otros ficheros del mismo proyecto, solo para el programa de la carpeta), antes del siguiente título o programa:

| En el texto | Qué tiene que coincidir |
|---|---|
| «**Salida:**» | Su salida estándar (`System.err` no se compara). Termina con 0; con `termina-con-error.txt`, con otro código, y entonces su «**Salida de error:**» es la de `System.err`. |
| «**Sesión en la terminal:**» | Un programa que lee del teclado: se ejecuta en una terminal y cada línea de `entrada.txt` se teclea cuando el programa la espera (`servicios/java/teclear.py`); coincide la pantalla entera, con lo tecleado y `System.err`. |
| «**Salida de las pruebas:**» | Tras una clase de pruebas (JUnit) de un proyecto de Maven: se ejecutan solo esas pruebas (`mvn test -Dtest=paquete.Clase`) y se compara el resumen de Surefire, desde «Running» hasta «Results:» más el «Tests run:» del total, sin tiempos, trazas ni líneas vacías. Su `salida-variable.txt`, el de la carpeta de la clase o, si no hay, **el del `pom.xml` de su módulo** (así un curso quita, por ejemplo, la ruta de la caché de Maven de quien escribe). |
| «**Con la aplicación arrancada:**» | Una aplicación de Spring Boot con `peticiones.txt` (abajo). |
| «**La ventana:**» | Una imagen `![…](….png)` de la ventana de JavaFX o Swing, idéntica **byte a byte** (abajo). |

**`solo-compilar.txt`**, con el motivo dentro. Junto a un programa: solo se compila con `javac` (una ventana que no se puede abrir sin pantalla, como un `JOptionPane`). Junto al `pom.xml` (o al `build.gradle.kts`/`build.gradle`): el proyecto se construye, pruebas incluidas, y sus programas no se ejecutan (una aplicación de Spring Boot que se queda escuchando). **Si su texto empieza por «Sin pruebas:»** (por ejemplo, «Sin pruebas: su prueba usa Testcontainers, que necesita Docker»), el proyecto se construye **sin ejecutar sus pruebas**, aunque sí se compilan: `mvn package -DskipTests`, `gradle build testClasses -x test`, y lo mismo con `--preparar-java`. Tiene que estar en UTF-8: si no, el error dice el fichero y la línea, y ese proyecto no se construye.

**Spring Boot con `curl`.** Con un `peticiones.txt` junto al `pom.xml` (las órdenes `curl` a `http://localhost:8080`, una por línea; las que empiezan por `#`, comentarios), la clase con `main` no se ejecuta como un programa. Si tras ella viene «**Con la aplicación arrancada:**» y un bloque ` ```text `, el kit la arranca en **un puerto libre** (`--server.port`), espera a que acepte conexiones, lanza las órdenes con ese puerto en lugar del 8080 (`curl`, `VAR=$(curl … | jq -r .campo)`, `curl … | jq -r .campo`, `sleep` y `cp`) y la para (`servicios/java/aplicacion.py`; con Docker, sin red, solo `localhost`). Compara la sesión sin la cabecera `Date`, con los métodos de `Allow` ordenados, el puerto visto como 8080 y sin las fechas y horas ISO (ni lo de `salida-variable.txt`). Sin ese bloque, el proyecto solo se construye.

- **`servidor.txt`** junto al `pom.xml`: los programas que se arrancan antes, en orden, y se paran después. Una **API simulada** (`../api-externa/ApiDelTiempo.java`, un programa suelto que escribe en su primera línea «Escuchando en http://localhost:PUERTO/») u otro proyecto de Spring Boot con sus opciones (`../catalogo --server.port=8082`, que se construye sin pruebas y se arranca con `java -jar`). Por eso la copia de la terminal es la carpeta que los contiene a todos. El puerto de un proyecto de Spring Boot (`--server.port=` en sus opciones, o `server.port=` en su `application*.properties`) es un número o `${VARIABLE:número}` (en la terminal no hay esa variable: vale el número); si no, el error dice el fichero y la línea.
- Junto a un programa suelto que lo nombra (el servidor de una página que usa `fetch`), ese programa solo se compila.
- Un `compose.yaml` en `servidor.txt` todavía no se admite: necesita Docker dentro de la terminal.

**Ventanas, sin pantalla.**

- **JavaFX**: una clase que extiende `Application`, en un proyecto con JavaFX, se ejecuta sin pantalla (`-Dglass.platform=headless -Dprism.order=sw`) con el lanzador `servicios/java/CapturaVentana.java`, que hace lo que diga **`acciones.txt`** (junto al programa o en la raíz de su módulo; una acción por línea: `escribir #id texto`, `pulsar #id`, `elegir #id n`, `responder Texto`, `esperar ms`, siempre en la ventana de delante, también en un diálogo), guarda la imagen de la ventana de delante y la cierra.
- **Swing**: un programa con `public static JPanel content()` no ejecuta su `main`; el lanzador `servicios/java/CapturaSwing.java` pinta ese panel con `-Djava.awt.headless=true`.
- Tras el enlace (y su «**Salida:**», si la hay), «**La ventana:**» y una imagen `![…](….png)`: la de ahora debe ser **idéntica byte a byte**. Si no lo es, o si la imagen todavía no existe, la de ahora se guarda en **`.verificacion/ventanas/`** (con la misma ruta que la del texto, desde la carpeta en la que verificas) y el error lo dice. Si el cambio es correcto, cópiala encima de la del curso. Nunca se escribe fuera de `.verificacion/ventanas/`: si la imagen del texto está fuera de la carpeta que verificas, la de ahora no se guarda y el error lo dice.
- **Las imágenes se hacen con Docker**, con las letras de la imagen de Java: **DejaVu** (decisión del autor, 24 de noviembre de 2026). Sin Docker salen con las letras del equipo (en un Ubuntu de escritorio, Noto Sans) y no coinciden: en Swing cambia hasta el tamaño de la ventana.

#### La imagen de Java

`servicios/java/Dockerfile`, construida **encima de la terminal del kit** (`kit-terminal`), así que todo lo demás es idéntico: Ubuntu, español, hora de Madrid, coreutils de GNU, Git con su reloj y la persona `alumno`. Se llama `kit-java:<huella>`, con una huella que sale de los ficheros de `servicios/java/` y del nombre de la imagen de la terminal: si cambia cualquiera de los dos, es otra imagen, y se construye sola la primera vez que hace falta (unos minutos, con internet). Al verificar, **sin red**.

**Ocupa 1,39 GB, unos 826 MB más que la terminal del kit** (`docker image ls`, 24 de noviembre de 2026: `kit-java:b7e24586c836`, 1.386.470.393 bytes, sobre `kit-terminal:b92f4401d9d9`, 560.526.200 bytes). El autor aceptó ese tamaño el 23 de noviembre de 2026. Solo se construye cuando hace falta: al verificar código de Java con Docker, con `--preparar-java` o con `--versiones`.

Versiones comprobadas el 23 de noviembre de 2026, cada descarga con la huella oficial de su fuente:

| Pieza | Versión | De dónde y por qué |
|---|---|---|
| JDK | **Temurin 25.0.4.1+1** | La que usa el autor con SDKMAN (`25.0.4.1+1-tem`; decisión del 23 de noviembre de 2026), de Eclipse Adoptium, con su SHA-256. Para x64 y aarch64 |
| Maven | **3.10.0** | De Apache (`archive.apache.org`), con su SHA-512 |
| Gradle | **9.8.2** | De `gradle.org`, con su SHA-256 |
| Letras | `fonts-dejavu-core` 2.37-8build1 y `fontconfig` 2.17.1-3ubuntu1 | Fijadas: las ventanas que se dibujan sin pantalla usan esas letras, y con otras la imagen cambiaría |
| Pango | `libpangoft2-1.0-0` 1.57.0-1 | JavaFX coloca el texto con él en Linux: sin él, ninguna ventana con texto arranca |

**Las más recientes** (23 de noviembre de 2026): Temurin 25.0.5.1+2 en la 25 (LTS) y 27.0.1.1+4 en la última versión de Java; Maven 3.10.2 (la 4.0.0 sigue en candidata, 4.0.0-rc-7); Gradle 9.9.2. **Temurin y Maven son parches y se quedan.** **Gradle 9.8.2 → 9.9.x se actualiza a la vez que el curso de Java revise sus versiones antes de publicar**, para que la imagen y el curso lleven las mismas (decisión del autor, 23 de noviembre de 2026). Si cambia una versión, se cambia en el `Dockerfile` (con su huella) y en esta tabla, y la imagen se reconstruye sola.

La caché de Maven y Gradle está en `/opt/kit-java/cache/` de la imagen (`m2/repository` y `gradle`), fuera de la carpeta personal: un `ls -a` en una sesión ve lo mismo que el alumno. En ella se monta el volumen de `--preparar-java`.

**Al verificar, la caché es de solo lectura** (desde el kit 1.1.0): el volumen se monta con `:ro`, así que ni un programa del curso ni una construcción pueden cambiar lo que usan los demás; solo `--preparar-java` escribe en él. Lo que Maven y Gradle necesitan escribir va a una caché de cada contenedor, que se tira con él:

- **Maven**, con su repositorio local encadenado (Maven 3.9 o posterior): un repositorio local nuevo (`-Dmaven.repo.local=/tmp/kit-java-m2`) y el del volumen detrás (`-Dmaven.repo.local.tail=/opt/kit-java/cache/m2/repository`), que solo se lee.
- **Gradle**, con un `GRADLE_USER_HOME` nuevo (`/tmp/kit-java-gradle`) y la caché de dependencias del volumen como caché de solo lectura (`GRADLE_RO_DEP_CACHE=/opt/kit-java/cache/gradle/caches`, la carpeta que contiene `modules-2`, como dice la documentación de Gradle). Gradle compila los `build.gradle.kts` en cada contenedor (antes lo guardaba en la caché compartida): unos segundos más por proyecto.

Sin Docker, las cachés del equipo no son de solo lectura.

#### Preparar la caché (`--preparar-java`)

**La única vez que hay red.** Construye, con internet, cada proyecto de Maven o Gradle de las carpetas que enlazan los módulos (de todo el curso, o de la carpeta o el módulo que digas) para descargar sus dependencias y plugins a la caché. No verifica nada: termina con 0 si todos los proyectos se han preparado.

```bash
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --preparar-java                     # todo el curso
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --preparar-java fase-11-spring-boot # una fase
```

- **Con Docker**, la caché es el volumen **`kit-java-cache`** (u otro, con la variable de entorno `KIT_JAVA_CACHE`), que la verificación monta en la imagen de Java, de solo lectura.
- **Sin Docker**, las cachés del equipo: la de Maven, `~/.m2/repository` (u otra, con `KIT_JAVA_M2`); la de Gradle, `~/.gradle` (u otra, con `GRADLE_USER_HOME`).
- Se prepara sin el *repackage* de Spring Boot (un proyecto sin clase con `main`, como una autoconfiguración, fallaba sin necesidad), y las pruebas que fallan a propósito no paran la construcción. Un proyecto con «Sin pruebas:» en su `solo-compilar.txt` compila sus pruebas, pero no las ejecuta.
- Después, la verificación trabaja **sin conexión** (Maven con `-o`, Gradle con `--offline`). Si falta una dependencia, el error dice que hay que volver a preparar. Vuelve a prepararla cada vez que cambie una dependencia.

#### Java sin Docker

Sin Docker (o con `--sin-docker`), el `java`, `javac`, `mvn` y `gradle` del `PATH` del equipo, también sin conexión y con sus cachés, en una copia temporal. Es la verificación parcial: otras versiones pueden dar otra salida, y **las ventanas no coinciden** (otras letras). Lo dice al final.

## `nucleo/declarar_ejercicios.py`

Declara en `curso.json` los ejercicios de uno o varios módulos (o de todos los de una fase), a partir de sus encabezados «#### Ejercicio N · Título». Sale de la parte común del `publicar.py` del curso inicial.

```bash
python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py fase-03-herramientas/01-terminal-lo-basico.md
python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py fase-03-herramientas --retos   # la fase, y sus retos
python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py fase-03-herramientas --comprobar
```

- Pone los ejercicios en «ejercicios» de su módulo, en el orden del módulo, y quita su `"disponible": false`; con `--retos`, también el `"retos_disponibles": false` de la fase (si su `retos.md` existe). Al declarar una fase entera, los módulos aún sin escribir siguen pendientes.
- **Un ejercicio se reconoce solo por su título, nunca por su posición**: si ya estaba en `curso.json` con el mismo título, conserva su identificador aunque se haya movido. A los nuevos les propone uno con la regla de `FORMATO.md` (apartado 3.3): el id del módulo, un punto y el título en minúsculas, sin tildes y con guiones.
- **Si un título cambia, no decide**: cuando en un módulo desaparecería algún ejercicio de `curso.json`, se para sin escribir nada y pregunta. Si es el mismo ejercicio con otro título, se cambia su `titulo` en `curso.json` (conservando su `id`) y se vuelve a ejecutar; si es otro ejercicio, se vuelve a ejecutar con `--aceptar-cambios`. Un identificador no cambia nunca: el progreso de los alumnos va unido a él. Hoy ningún curso tiene todavía una versión publicada (los identificadores de Code Academy, como `java-03.06`, eran otros), así que aún no afecta a nadie; desde la primera, un identificador que desaparece necesita su equivalencia, y `formato_academia.py` lo comprueba.
- Comprueba que ningún identificador se repite en el curso y que los títulos son texto plano.
- Solo escribe `curso.json` si algo cambia, con sangría de 2 espacios: un `curso.json` formateado a mano se reformatea.

## `nucleo/generar_indice.py`

Genera `00-indice.md` a partir de `curso.json`. Sale de `generar_indice.py` del curso de Java, que tenía la lista de fases y módulos dentro del script; aquí la lista es `curso.json`.

```bash
python3 ../kit-cursos/herramientas/nucleo/generar_indice.py              # escribe 00-indice.md
python3 ../kit-cursos/herramientas/nucleo/generar_indice.py --comprobar  # solo dice si está al día
```

- Un encabezado `## Fase NN — Título` por fase, con los títulos de `curso.json`, y una tabla con sus módulos y sus retos.
- El **nivel** y el **tiempo** de cada módulo salen de su cabecera (`FORMATO.md`, apartado 5.2), así que solo los tienen los módulos disponibles. Los que tienen `"disponible": false` salen como «Pendiente», sin enlace y con «—»; lo mismo los retos pendientes y las etapas que no existen. El índice se completa solo a medida que se escriben los módulos.
- Si hay `partes`, el contenido se agrupa por partes. El proyecto por etapas tiene su propia sección; el de tipo `"modulo"` se marca con 🎯 en su fase.
- La carpeta de una fase solo se enlaza si ya existe.
- **Ruta mínima** (desde el kit 1.1.0): si `curso.json` tiene `ruta_minima`, los módulos y las etapas de la ruta llevan 🧭, cada fase dice cuántas horas suyas entran en la ruta («🧭 ~6 h») y, tras la explicación del principio, una línea resume la ruta y enlaza a `RUTA-MINIMA.md`, si existe. Sin `ruta_minima`, el índice no cambia. Genera antes `RUTA-MINIMA.md` con [`generar_ruta_minima.py`](#nucleogenerar_ruta_minimapy).
- Diferencias con el de Java: no genera los textos propios de aquel curso (bloques, hitos, versiones); se añadirán cuando los pida el curso de Java. `RUTA-MINIMA.md` lo genera `generar_ruta_minima.py`.

## `nucleo/generar_ruta_minima.py`

Genera `RUTA-MINIMA.md` a partir de `ruta_minima` de `curso.json` (desde el kit 1.1.0; `FORMATO.md`, apartados 3.2 y 4). Sale de `generar_indice.py` del curso de Java, que tenía la ruta en una lista dentro del script y su texto escrito en el código; aquí la lista es `curso.json` y el texto propio del curso va en una plantilla.

```bash
python3 ../kit-cursos/herramientas/nucleo/generar_ruta_minima.py              # escribe RUTA-MINIMA.md
python3 ../kit-cursos/herramientas/nucleo/generar_ruta_minima.py --comprobar  # solo dice si está al día
```

```json
"ruta_minima": {
  "modulos": ["java.que-es-programar", "java.polimorfismo"],
  "etapas": ["java.etapa.consola"],
  "plantilla": "RUTA-MINIMA.plantilla.md"
}
```

- `modulos`, obligatorio, en orden; `etapas` (del proyecto) y `plantilla`, opcionales.
- **La plantilla** es un `.md` de la raíz del curso con su texto propio y estos huecos:

  | Hueco | Qué pone |
  |---|---|
  | `{{resumen}}` | Módulos y horas de la ruta, frente a los del curso entero, y sus etapas del proyecto |
  | `{{modulos}}` | **Obligatorio.** Por fase, la tabla de sus módulos de la ruta con su tiempo, y los que se quedan fuera (o «Fuera de la ruta», si no entra ninguno) |
  | `{{proyecto}}` | La tabla de las etapas del proyecto de la ruta |
  | `{{consultas}}` | Las consultas puntuales: los módulos que no están en la ruta, pero que algún módulo de la ruta enlaza en «Conviene saber antes», y quién los pide |

  Cualquier otro hueco es un error (también en `formato_academia.py`). Sin plantilla, se usa un texto genérico con las cuatro partes. La academia no instala la plantilla.
- Los módulos con `"disponible": false` salen sin enlace y con «—» de tiempo. Las horas son las de la cabecera de cada módulo, como en el índice.
- `RUTA-MINIMA.md` no se edita a mano: después de cambiar la ruta, se vuelve a generar, y después el índice.
- Termina con 1 si `curso.json` no tiene `ruta_minima` o tiene un error (o, con `--comprobar`, si `RUTA-MINIMA.md` falta o no está al día).
- Con el curso de Java (su commit `cfb14f3e`), los 104 módulos, sus enlaces, las tablas por fase y las 26 consultas salen iguales que su `RUTA-MINIMA.md`; cambian 12 líneas, por datos del propio curso ([la prueba de fiabilidad](#la-prueba-de-fiabilidad-con-el-curso-de-java)).

## `nucleo/generar_chuleta_global.py`

Genera `99-chuleta-global.md` reuniendo la sección «## 6. Chuleta» de cada módulo disponible, en el orden de `curso.json`. Sale de `generar_chuleta_global.py` del curso de Java.

```bash
python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py              # escribe 99-chuleta-global.md
python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py --comprobar  # solo dice si está al día
```

- Baja un nivel los encabezados de cada chuleta y corrige sus enlaces, anclas e imágenes relativos para que funcionen desde la raíz del curso. Lo que está dentro de un bloque de código no se toca.
- La chuleta de cada módulo termina en la sección siguiente («## 7. Preguntas de repaso») o en la línea `---` de la navegación.
- Diferencias con el de Java: los títulos de las fases salen de `curso.json` (no de `00-indice.md`), y los bloques de código de cuatro comillas (` ```` `) se reconocen bien (el de Java reescribía un enlace de ejemplo dentro de uno). Con la copia del curso de Java, el resultado es idéntico salvo en esa línea y en la frase de la cabecera.

## `nucleo/comprobar_mermaid.py`

Comprueba que cada bloque ` ```mermaid ` se dibuja sin errores. Un diagrama mal escrito no avisa al escribirlo: simplemente no se ve. Sale de `comprobar_mermaid.py` del curso de Java, con lo mismo que comprueba. También comprueba los bloques Mermaid que están dentro de otro bloque (por ejemplo, en las chuletas), para que quien los copie pueda usarlos tal cual. Las reglas de `FORMATO.md` sobre Mermaid (sin negrita, entidades…) las mira `formato_academia.py`; esta, solo que se dibujen.

```bash
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py                          # todo el curso
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-01-que-es-programar # una carpeta o un fichero
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-01-…/04-….md --imagenes /tmp/diagramas
```

Con `--imagenes`, guarda además cada diagrama como PNG para revisarlo a ojo. Cada fallo dice el fichero, la línea donde empieza el bloque, la versión y el error de Mermaid. Revisa también los `.md` de `codigo/` (como el README de un ejemplo, que el alumno abre en GitHub o en su editor). Se salta lo que está mal a propósito: los `.md` de una carpeta de `codigo/` con `debe-fallar.txt` (en ella o en una de sus carpetas de arriba, dentro de `codigo/`) y los diagramas del bloque de un módulo cuyo «📁 Código» lleva a una de esas carpetas, también los anidados (el README roto de un reto, mostrado en un bloque ` ````markdown `). Ignora `.verificacion/`, `herramientas/` y `node_modules/` dentro de lo que revisa. Si falta Node o Chrome, termina con 1 y lo dice.

Dibuja cada diagrama con **dos versiones de la biblioteca Mermaid**, fijadas las dos (a 16 de noviembre de 2026):

| Biblioteca Mermaid | Con mermaid-cli | Por qué |
|---|---|---|
| **12.3.0** | 12.2.0 (la última a 16 de noviembre de 2026; admite `^12.2.0`) | Es la que usa **la academia** para dibujar los diagramas (`frontend/package.json` de Code Academy, desde su commit `4b688f0`). |
| **10.9.8** | 10.9.1 | La antigua, la del curso de Java: por **GitHub** y los visores de Markdown, donde también se leen los cursos. |

- **Las dos se fijan**: mermaid-cli no fija la versión de la biblioteca que lleva dentro, solo un rango (`^12.2.0`), así que sin fijarla `npx` instalaría la última que encaje y se comprobaría con una versión distinta de la de la academia sin que nadie se diera cuenta. Por eso la herramienta pide a `npx` los dos paquetes con su versión exacta. La primera vez, `npx` los descarga en su caché, sin tocar el repositorio.
- **La versión del kit tiene que coincidir con la de la academia.** Cuando la academia suba su `mermaid` en `frontend/package.json`, se sube a la vez la de `VERSIONES` en `comprobar_mermaid.py` (con el mermaid-cli que la admita, comprobado con `npm view @mermaid-js/mermaid-cli@<versión> dependencies.mermaid`) y esta tabla.

## `nucleo/reemplazar.py`

Aplica sustituciones de texto en varios ficheros a la vez: **todas o ninguna**. Viene del curso inicial, donde resolvió un problema real: un script de sustituciones escribió unos ficheros, falló en otro, y el commit se hizo igual, con el cambio a medias. Sirve a cualquier proyecto que actualice varios documentos a la vez (el kit, la academia, los cursos).

Los cambios van en un fichero JSON, en orden:

```json
[
  {"fichero": "ESTADO.md", "antes": "texto exacto", "despues": "texto nuevo"},
  {"fichero": "PLAN.md", "antes": "otro texto", "despues": "su sustituto"}
]
```

```bash
python3 ../kit-cursos/herramientas/nucleo/reemplazar.py cambios.json && git commit -am "…"   # el commit, solo si todo va bien
python3 ../kit-cursos/herramientas/nucleo/reemplazar.py cambios.json --comprobar              # solo comprueba; no escribe nada
python3 ../kit-cursos/herramientas/nucleo/reemplazar.py cambios.json --raiz ../curso-x        # rutas relativas a otra carpeta
```

- Cada «antes» tiene que aparecer **exactamente una vez** en su fichero, contando los cambios anteriores de la lista sobre ese mismo fichero (así un cambio puede tocar lo que dejó otro).
- Si alguno falla (el fichero no existe, el texto no aparece o aparece más de una vez), **no escribe ningún fichero**: dice cuál ha fallado y cuántas veces aparecía su texto, y termina con 1.
- Si todos van bien, escribe los ficheros y los vuelve a leer para comprobar que cada «despues» está en su sitio. Si una escritura falla a medias (disco lleno, permisos), deja como estaban los ya escritos.
- Respeta los saltos de línea de cada fichero, también los de Windows (`\r\n`).

## Las pruebas

Cada herramienta tiene sus pruebas en `pruebas/`. Casi todas siguen el mismo método: **copian un curso de ejemplo correcto a una carpeta temporal, lo estropean de una forma concreta y comprueban que sale justo ese error o ese aviso**. Así, si un cambio en una herramienta deja de detectar algo, una prueba falla.

```bash
python3 -m unittest discover -s herramientas/pruebas -v     # desde la raíz del kit
```

- `cursos/bueno/`: el curso de ejemplo. Pequeño y correcto: una fase con un módulo escrito (con un script de bash, una sesión de terminal, ficheros JSON, una imagen, un diagrama y enlaces a otro curso, a un módulo con ancla y a un término de su glosario) y otro pendiente, retos (a los que lleva el «Siguiente» de su último módulo), proyecto por etapas, y su índice y su chuleta generados.
- `cursos/ejemplo-destino/`: el curso al que enlaza `bueno`, en su carpeta hermana (por eso la carpeta se llama como su repositorio). Un módulo que es su proyecto final (de tipo `"modulo"`, así que su fase no necesita retos) y su propio glosario.
- Los dos pasan todas las herramientas sin errores. **La academia los usa como cursos de ejemplo** para sus pruebas y su demo: guarda una copia sacada de un commit fijo del kit (`FORMATO.md`, apartado 14). Si se cambian, hay que avisar a la academia del commit para que renueve su copia.
- `cursos/java/` (desde el kit 1.1.0): un curso pequeño de Java para las pruebas del ejecutor de Java, con una fase de cinco módulos: programas sueltos (con `entrada.txt`, `args.txt`, `opciones-java.txt`, `termina-con-error.txt`, `salida-variable.txt`, `solo-compilar.txt` y paquetes bajo `src/`), Maven con JUnit, Gradle, ventanas (JavaFX con `acciones.txt` y Swing, con sus imágenes) y Spring Boot con `peticiones.txt` y una API simulada (`servidor.txt`). No lo usa la academia.
- `test_formato_academia.py`, `test_verificar_codigo.py`, `test_java.py`, `test_declarar_ejercicios.py`, `test_generar_indice.py`, `test_generar_ruta_minima.py`, `test_generar_chuleta_global.py`, `test_comprobar_mermaid.py` y `test_reemplazar.py`: las de cada herramienta. Las de `verificar_codigo.py` prueban también los comprobadores de `lenguajes/` y, con Docker, la terminal del kit (sus versiones, Git en español con la rama `main`, el reloj de Git y que no hay red). Las del servidor HTTP local escuchan en **un puerto libre que elige el sistema**, no en el 8080: no fallan si otro programa lo ocupa. Las de `test_java.py`, con Docker en la imagen de Java y sin Docker con el JDK, Maven y Gradle del equipo; preparan la caché una vez por ejecución (con red), con Docker en un volumen solo para ellas (`kit-java-cache-pruebas`).
- **Se saltan solas** las que necesitan algo que la máquina no tiene: las de la terminal del kit, sin Docker; las de Mermaid, sin Node o Chrome; las de Java, sin Docker o sin `java`, `javac`, `mvn` y `gradle` en el `PATH` (cada modo, lo suyo).

### La prueba de fiabilidad con el curso de Java

`fiabilidad_java.py` (con su `--help`) no es una prueba de `unittest`: es lenta y necesita el curso de Java en la carpeta hermana. Saca un **commit fijo** del curso con `git archive` (solo lee) a dos copias temporales y verifica las fases que le digas con las dos herramientas: el `verificar_codigo.py` original de ese commit (con el Java del equipo) y el del kit (con Docker, después de `--preparar-java`). Después compara **bloque a bloque**, solo los bloques ` ```java ` con su «📁 Código»: coinciden si las dos los dan por buenos o las dos por malos. Deja los resultados en la carpeta de `--salida` (por defecto `odd/fiabilidad/`, una carpeta de trabajo local que no está en Git): un `.json` por objetivo y la salida completa de cada herramienta; un objetivo que ya tiene su `.json` no se repite, así que una prueba larga se puede cortar y seguir. Con `--ruta-minima`, compara `RUTA-MINIMA.md` en lugar del código.

```bash
python3 herramientas/pruebas/fiabilidad_java.py ../curso-java cfb14f3e fase-02-fundamentos   # desde la raíz del kit
python3 herramientas/pruebas/fiabilidad_java.py ../curso-java cfb14f3e --resumen
```

La del kit 1.1.0 (23 y 24 de noviembre de 2026, commit `cfb14f3e` del curso; el resumen, en `ESTADO.md`): **2172 de 2244 bloques coinciden (96,8 %)**, en las fases 01, 02, 07, 08 y 11 y tres módulos de la 12. Lo que era del kit (programas con paquete bajo `src/`, el bloqueo de la caché de Gradle y el *repackage* de `--preparar-java`) está arreglado; lo demás es del curso (sobre todo, 62 ventanas hechas con otras letras) y está en `ESTADO.md`.
- `curso_json_de_java.py`: genera un `curso.json` provisional para una **copia** del curso de Java original (que no lo tiene), para probar `formato_academia.py` con 199 módulos reales y como punto de partida de `curso-java/`. Su ayuda (`--help`) explica cómo sacar la copia solo con Git de lectura.
