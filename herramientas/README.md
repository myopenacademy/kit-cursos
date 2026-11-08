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
python3 ../kit-cursos/herramientas/nucleo/generar_indice.py           # 1. el índice, desde curso.json
python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py   # 2. la chuleta global
python3 ../kit-cursos/herramientas/formato_academia.py                # 3. ¿cumple el formato?
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-NN-…/NN-….md   # 4. su código, si tiene
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-NN-…/NN-….md  # 5. sus diagramas, si tiene
```

**Al cerrar cada fase**, lo mismo con la fase entera (`verificar_codigo.py fase-NN-…`, `comprobar_mermaid.py fase-NN-…`), y `verificar_codigo.py` **con Docker** ([la verificación completa](#la-terminal-del-kit)).

**Antes de publicar una versión**, `formato_academia.py` sin errores, con la versión etiquetada en Git (`v1.0.0`): así compara los identificadores con los de la versión anterior.

## Qué hay

| Herramienta | Qué hace | Necesita |
|---|---|---|
| [`formato_academia.py`](#formato_academiapy) | Comprueba que el curso cumple `FORMATO.md` y se puede instalar en la academia | Python 3.11 o posterior, sin librerías adicionales. Git, solo para comparar con la última versión publicada (si no está, no compara) |
| [`nucleo/verificar_codigo.py`](#nucleoverificar_codigopy) | Comprueba que el código de los módulos coincide con `codigo/` y funciona: scripts de bash, sesiones de terminal (también de Git) y ficheros JSON, YAML, XML, CSV y Markdown | Python 3.11 o posterior; **PyYAML** para los YAML (en Ubuntu, `python3-yaml`; con pip, `pyyaml`: la única librería de fuera de Python que usa el kit, y solo para eso); **Docker** para la verificación completa (sin él, verifica de forma parcial y avisa) |
| [`nucleo/generar_indice.py`](#nucleogenerar_indicepy) | Genera `00-indice.md` desde `curso.json` | Python 3.11 o posterior |
| [`nucleo/generar_chuleta_global.py`](#nucleogenerar_chuleta_globalpy) | Genera `99-chuleta-global.md` con la chuleta de cada módulo | Python 3.11 o posterior |
| [`nucleo/comprobar_mermaid.py`](#nucleocomprobar_mermaidpy) | Comprueba que los diagramas Mermaid se dibujan, con la versión de la academia y con la antigua | **Node.js** (con `npx`) y **Google Chrome o Chromium** (si no está en un sitio habitual, su ruta en la variable `CHROME_PATH`). Comprobado el 8 de noviembre de 2026 con Node 24.22.1 y Chrome en Linux |

Las carpetas:

| Carpeta | Qué guarda |
|---|---|
| `herramientas/` | `formato_academia.py`, la parte pública: un solo fichero, sin dependencias |
| `nucleo/` | Las herramientas comunes a todos los cursos, sacadas del curso de Java original, y `argumentos.py` (la revisión común de sus argumentos) |
| `lenguajes/` | Un comprobador por lenguaje o formato, que usa `verificar_codigo.py`: `bash.py` y `formato_json.py`, `formato_yaml.py`, `formato_xml.py`, `formato_csv.py` y `formato_markdown.py` |
| `servicios/` | Lo que necesitan los comprobadores para ejecutar: `terminal.py` y la imagen de [la terminal del kit](#la-terminal-del-kit) (`terminal/`) |
| `pruebas/` | [Las pruebas](#las-pruebas) de las herramientas y un curso de ejemplo pequeño |

Aún falta `curl` con un servidor local (`PLAN.md` del kit, tarea 4), que se hará cuando el curso inicial diga qué necesitan sus ejercicios. No hay un `comprobar_enlaces.py` aparte: los enlaces y las anclas los comprueba `formato_academia.py`.

## Lo común a todas

- **`--help`** (o `-h`) muestra la ayuda de la herramienta, el mismo texto que hay al principio de su fichero.
- Sin argumentos, trabajan con **el curso de la carpeta actual**. Las que lo admiten reciben una carpeta o un fichero (una fase, un módulo, otro curso).
- **Códigos de salida**: **0** si todo está bien (aunque haya avisos); **1** si hay algún error (o, con `--comprobar`, si un fichero generado no está al día); **2** si los argumentos están mal (una opción desconocida o una ruta que no existe), sin hacer nada. Así una ruta mal escrita no da un «✅» falso por haber revisado 0 ficheros (`nucleo/argumentos.py`, sacado del curso de Java; las rutas se buscan desde la carpeta actual, no desde la del script).
- **Cada mensaje dice el fichero, la línea y qué pasa**, como `fichero.md:120: ERROR: …`. Un **ERROR** es lo que `FORMATO.md` dice con «debe» (el curso no se instala o el código no funciona); un **AVISO**, lo que dice con «conviene» o lo que no se ha podido comprobar.

## `formato_academia.py`

Comprueba, sin ejecutar nada del curso, todo lo del apartado 13 de [`FORMATO.md`](../FORMATO.md):

- **`curso.json`**: campos, identificadores (forma, que no se repitan y que no desaparezca ninguno publicado sin su equivalencia), partes, proyecto y equivalencias; que cada fichero declarado existe y cada módulo de las carpetas de fase está declarado. Los módulos con `"disponible": false` y los retos con `"retos_disponibles": false` no tienen por qué existir.
- **Títulos en texto plano** del curso, las fases, los módulos, los ejercicios y los retos.
- **Cada módulo disponible**: título igual al de `curso.json`, cabecera (`Conviene saber antes`, `Tiempo estimado` y `Nivel`), las ocho secciones en orden, subapartados numerados donde toca, los ejercicios con los títulos y el orden de `curso.json`, sus pistas antes de la solución, la solución, las preguntas de repaso con su respuesta y la navegación del final.
- **Retos** de cada fase, **etapas** del proyecto, **glosario** (en el curso inicial), **`00-indice.md`** (sus fases, las de `curso.json`) y **ficheros obligatorios**.
- En todos los Markdown del curso (salvo `codigo/`, `herramientas/` y los ficheros de trabajo `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md`): **enlaces** y sus **anclas** (también a otros cursos), **imágenes**, **diagramas Mermaid**, **HTML**, bloques de código sin cerrar y huecos `[RELLENAR: …]` de las plantillas.

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
- **Anclas**: las que genera GitHub a partir del encabezado, con la misma regla que `comprobar_enlaces.py` del curso de Java (minúsculas, sin signos, espacios convertidos en guiones; los repetidos, con `-1`, `-2`…), conservando el texto del código en línea (`` `Page<T>` `` da `paget`).
- **HTML**: el que admite la academia, como su saneador (visto en Code Academy el 8 de noviembre de 2026):
  - Se admiten tal cual `details`, `summary`, `code`, `kbd`, `br`, `sup`, `sub`, `em`, `strong`, `del`, tablas, listas, párrafos y encabezados, sin atributos (salvo `align` en las celdas, `start` en `ol` y `class="language-…"` en `code`).
  - El formato sin efecto (`span`, `div`, `u`, `b`, `i`…) y los `<a>` los quita al instalar y deja su texto: **aviso**.
  - Cualquier otra etiqueta (`script`, `iframe`, `img`, `style`…) y cualquier otro atributo (`onclick`, `style`, `open`…) hacen fallar la instalación: **error**.
- **Mermaid**: sin negrita ni cursiva en las etiquetas (tampoco `<b>` o `<i>`), solo las entidades `&quot;`, `&lt;`, `&gt;` y `&amp;`, y sin directivas, *frontmatter*, `click`, `url()` ni `@import`. Que el diagrama se dibuje lo comprueba [`comprobar_mermaid.py`](#nucleocomprobar_mermaidpy).
- **Versiones publicadas**: si el curso tiene etiquetas `vX.Y.Z` en Git, compara los identificadores de la última con los de ahora; cada uno que haya desaparecido necesita su equivalencia (`FORMATO.md`, apartado 11.2).

## `nucleo/verificar_codigo.py`

El núcleo de `verificar_codigo.py` del curso de Java, sin nada de Java y con las mismas convenciones ([`FORMATO.md`, apartado 7.1](../FORMATO.md#71-ficheros-de-verificación-y-salidas-en-el-texto)). Cada lenguaje o formato tiene su comprobador en `lenguajes/`.

```bash
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py                       # todo el curso
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-03-herramientas  # una fase (o un módulo)
python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --sin-docker          # en la bash del equipo
```

- **Cada bloque seguido de «📁 Código»** tiene que ser idéntico a un fichero de su carpeta (sin contar los espacios del final de las líneas ni las líneas en blanco del principio y del final). Si no, dice cuál es el más parecido y la primera línea distinta.
- **Un script de bash** (`.sh`) se ejecuta con `bash fichero.sh` en una copia de su carpeta, con `args.txt` y `entrada.txt`, y tiene que terminar con 0; su salida, la de «**Salida:**». Con `termina-con-error.txt`, tiene que terminar con otro código, y su salida de error, la de «**Salida de error:**».
- **Una sesión** («**En tu terminal** (`sesion.txt`):», su bloque ` ```text ` y su «📁 Código»): se teclea cada orden de `sesion.txt` en una bash con terminal de 100 columnas, con el indicador `$ `, en una carpeta personal con los demás ficheros de la carpeta; la pantalla final tiene que ser la del bloque. Como en Java, `@ctrl-c 3` tras una orden que no termina sola pulsa Ctrl+C a los 3 segundos. Las sesiones de **Git** son sesiones como las demás, con [el reloj de Git](#el-reloj-de-git).
- **`salida-variable.txt`**: lo que encaja con cada expresión regular se sustituye por `…` en las dos salidas antes de compararlas.
- **Los ficheros de datos** de cada carpeta enlazada se comprueban con Python (no necesitan Docker), cada error con su línea:
  - **JSON** (`formato_json.py`): que se lee.
  - **YAML** (`formato_yaml.py`, con PyYAML): que se leen todos sus documentos. Si falta PyYAML, avisa de que no los ha podido comprobar.
  - **XML** (`formato_xml.py`): que está bien formado (no lo valida contra un esquema).
  - **CSV** (`formato_csv.py`): que se lee con el separador de `separador.txt` (`;`, `|` o `tabulador`; si no hay, la coma), sin comillas sin cerrar, y con las mismas columnas en cada fila que en la cabecera.
  - **Markdown** (`formato_markdown.py`, los `.md` de `codigo/`, como el README de un proyecto): enlaces relativos y anclas que existen, tablas con su fila separadora y las mismas columnas en cada fila, y bloques de código cerrados. Los enlaces a internet no se comprueban (sin red).
  - **`debe-fallar.txt`**: si la carpeta lo tiene, **todos** sus ficheros de datos tienen que fallar (están mal a propósito); uno válido es un error. Cada ejemplo roto, en su propia carpeta.
  - **Conversiones**: un `.json` y un `.yaml` con el mismo nombre en la misma carpeta tienen que cargar los mismos datos.
- **bash 3.2, la de macOS**: cada `.sh` no puede usar lo que no existe en ella (arrays asociativos, `mapfile`, `${var,,}`, `|&`, `&>>`, `[[ -v ]]`, `{1..10..2}`…); esa búsqueda funciona siempre. Con Docker, además, cada script se **ejecuta con bash 3.2.57** y su salida y su código de salida tienen que ser los de bash 5: así salen también las diferencias que la búsqueda no ve (un `printf '%(%Y)T'`, de bash 4.2, falla en la 3.2).
- **Lo que no comprueba de macOS**: que `sed`, `date`, `ls`, `grep`… se comporten igual. En macOS son las versiones de **BSD** y en la terminal del kit, las de **GNU** (Linux), con opciones y salidas distintas (`sed -i ''`, `date -v`…). Eso lo cubren los avisos del texto de cada módulo, no el kit.
- **También**: error por cada fichero enlazado que Git ignora (no llegaría a un clon del curso), y aviso por cada carpeta de `codigo/` que ningún módulo enlaza y por cada script que ningún bloque muestra.

### La terminal del kit

Donde se ejecutan los scripts y las sesiones (`servicios/terminal.py`).

**Con Docker, la verificación completa.** Un contenedor de la imagen `servicios/terminal/Dockerfile` (se llama `kit-terminal:<huella del Dockerfile>` y se construye la primera vez, en unos minutos y con internet), **sin red** (`--network none`), con el nombre de máquina `ordenador`, la persona `alumno` y la configuración de Git de todo el sistema (nombre «Ana García», `ana@example.com` y la rama `main`; una sesión que enseña `git config --global` la cambia, como en cualquier equipo). Los ficheros de la carpeta se copian con una fecha fija (15 de enero de 2026, 10:00), para que `ls -l` no cambie. Fija todo lo que cambia la salida de una orden, así que es **la misma en cualquier máquina** (a 8 de noviembre de 2026):

| Pieza | Versión | De dónde y por qué |
|---|---|---|
| Ubuntu | 26.04.1 LTS | `ubuntu:26.04` fijada por su huella (`sha256:6a06111c…`) |
| Git | **2.56.0** | La que enseña el curso inicial (Ubuntu 26.04 trae la 2.53.0). Compilada del código oficial de kernel.org, comprobando su SHA-256 publicado, **con sus traducciones** (gettext): sin ellas, Git responde en inglés. Con `sysconfdir=/etc`, como el Git de Ubuntu (si no, no lee `/etc/gitconfig`). Con **`NO_RUST=1`**: en Git 2.56 la parte en Rust es opcional (lo dice su `Makefile`) y no cambia los mensajes. **Desde Git 3.0, Rust será obligatorio y la imagen tendrá que instalarlo** (`cargo`) para compilarlo. |
| bash | 5.3.9 | La de Ubuntu 26.04 |
| bash 3.2 | **3.2.57** | La de macOS, como `bash-3.2`. Compilada del código oficial de GNU: su firma (`.sig`) se verificó el 8 de noviembre de 2026 con la clave de Chet Ramey, que mantiene bash (`7C01 35FB 088A AF6C 66C6 50B9 BB58 69F0 64EA 74AB`), y el Dockerfile comprueba su SHA-256. |
| Idioma y hora | `es_ES.UTF-8`, Europe/Madrid | Las salidas del curso están en español |
| Reloj de Git | Desde el 15 de enero de 2026, 10:00 | `servicios/terminal/git-reloj`, delante del `git` de verdad (también sin Docker) |

Si cambia una versión (por ejemplo, el curso pasa a enseñar otra de Git), se cambia en el `Dockerfile` (con su SHA-256) y en esta tabla: la huella del `Dockerfile` cambia y la imagen se reconstruye sola.

**Por qué bash 3.2 se compila en la imagen y no se usa la imagen oficial `bash:3.2.57`** (que existe en Docker Hub): la oficial es de Alpine, con las herramientas de BusyBox en lugar de las de GNU, así que `ls`, `sort` o `grep` darían salidas distintas y cada script daría diferencias falsas. Con las dos bash en la misma imagen y las mismas herramientas, una diferencia es solo del bash.

#### El reloj de Git

Para que los identificadores de los commits salgan siempre iguales y `git log` parezca un historial real (decisión del autor, 8 de noviembre de 2026), los commits de cada sesión o script tienen **fechas fijas que avanzan**: el primero, el 15 de enero de 2026 a las 10:00 (la fecha de los ficheros copiados); cada uno, un minuto después del anterior. Lo hace `git-reloj`, un script pequeño que la terminal pone delante del `git` de verdad: a las órdenes que pueden crear commits (`commit`, `merge`, `rebase`, `cherry-pick`, `revert`, `stash`, `tag`…) les da la fecha del reloj y, si terminan bien, lo adelantan un minuto (un `git commit` que no tiene nada que confirmar no lo adelanta). Si la sesión pone sus propias fechas (`GIT_AUTHOR_DATE`…), se respetan. Lo único que lo delata es `which git`, que dice `/usr/local/sbin/git`.

**Sin paginador.** En la terminal, `GIT_PAGER` y `PAGER` son `cat`: con una salida que no cabe en pantalla, `git log` o `man` se quedarían esperando una tecla (en el equipo del alumno, `less` la pide). Con una que cabe, se ve igual.

**Lo que Git no traduce**, aunque el sistema esté en español (es así en cualquier Git, también en el de Ubuntu): las fechas (`Date:   Thu Jan 15 10:00:00 2026 +0100`) y el resumen de cambios (`1 file changed, 1 insertion(+)`). El curso las muestra tal cual.

#### Sin Docker, la verificación parcial

Sin Docker (o con `--sin-docker`), en la bash del equipo, en una carpeta temporal que hace de carpeta personal, con el español, la hora de Madrid, la misma configuración de Git y el reloj de Git. Pero:

- **La red no se puede cortar** sin permisos de administrador (`unshare --net` necesita espacios de nombres de usuario, que Ubuntu limita): solo se apuntan los proxies a una dirección muerta, que para `curl`, `git` y los gestores de paquetes, pero no a un programa que abra la conexión por su cuenta.
- Las versiones son las del equipo, así que una salida puede cambiar.
- No hay bash 3.2: solo la búsqueda de lo que no existe en ella.

Lo dice al final de cada verificación. **Para cerrar una fase, verifica con Docker.**

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
- Diferencias con el de Java: no genera `RUTA-MINIMA.md` ni los textos propios de aquel curso (bloques, hitos, versiones); se añadirán cuando los pida el curso de Java.

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

Con `--imagenes`, guarda además cada diagrama como PNG para revisarlo a ojo. Cada fallo dice el fichero, la línea donde empieza el bloque, la versión y el error de Mermaid. Ignora `codigo/`, `.verificacion/`, `herramientas/` y `node_modules/` dentro de lo que revisa. Si falta Node o Chrome, termina con 1 y lo dice.

Dibuja cada diagrama con **dos versiones de la biblioteca Mermaid**, fijadas las dos (a 8 de noviembre de 2026):

| Biblioteca Mermaid | Con mermaid-cli | Por qué |
|---|---|---|
| **12.2.0** | 12.2.0 | Es la que usa **la academia** para dibujar los diagramas (`frontend/package.json` de Code Academy). |
| **10.9.8** | 10.9.1 | La antigua, la del curso de Java: por **GitHub** y los visores de Markdown, donde también se leen los cursos. |

- **Las dos se fijan**: mermaid-cli no fija la versión de la biblioteca que lleva dentro, solo un rango (`^12.2.0`), así que sin fijarla `npx` instalaría la última que encaje (el 8 de noviembre de 2026 ya existía la 12.3.0) y se comprobaría con una versión distinta de la de la academia sin que nadie se diera cuenta. Por eso la herramienta pide a `npx` los dos paquetes con su versión exacta. La primera vez, `npx` los descarga en su caché, sin tocar el repositorio.
- **La versión del kit tiene que coincidir con la de la academia.** Cuando la academia suba su `mermaid` en `frontend/package.json`, se sube a la vez la de `VERSIONES` en `comprobar_mermaid.py` (con el mermaid-cli que la admita, comprobado con `npm view @mermaid-js/mermaid-cli@<versión> dependencies.mermaid`) y esta tabla.

## Las pruebas

Cada herramienta tiene sus pruebas en `pruebas/`. Casi todas siguen el mismo método: **copian un curso de ejemplo correcto a una carpeta temporal, lo estropean de una forma concreta y comprueban que sale justo ese error o ese aviso**. Así, si un cambio en una herramienta deja de detectar algo, una prueba falla.

```bash
python3 -m unittest discover -s herramientas/pruebas -v     # desde la raíz del kit
```

- `cursos/bueno/`: el curso de ejemplo. Pequeño y correcto: una fase con un módulo escrito (con un script de bash, una sesión de terminal, ficheros JSON, una imagen y un diagrama) y otro pendiente, retos, proyecto por etapas, y su índice y su chuleta generados. Pasa todas las herramientas sin errores.
- `test_formato_academia.py`, `test_verificar_codigo.py`, `test_generar_indice.py`, `test_generar_chuleta_global.py` y `test_comprobar_mermaid.py`: las de cada herramienta. Las de `verificar_codigo.py` prueban también los comprobadores de `lenguajes/` y, con Docker, la terminal del kit (sus versiones, Git en español con la rama `main`, el reloj de Git y que no hay red).
- **Se saltan solas** las que necesitan algo que la máquina no tiene: las de la terminal del kit, sin Docker; las de Mermaid, sin Node o Chrome.
- `curso_json_de_java.py`: genera un `curso.json` provisional para una **copia** del curso de Java original (que no lo tiene), para probar `formato_academia.py` con 199 módulos reales y como punto de partida de `curso-java/`. Su ayuda (`--help`) explica cómo sacar la copia solo con Git de lectura.
