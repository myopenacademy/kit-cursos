# Estado del kit de cursos

> Actualízalo al terminar cada tarea. Es la memoria entre sesiones: lo que no esté aquí o en `PLAN.md` no lo sabrá la sesión siguiente.

## Dónde estamos

**9 de noviembre de 2026.** El kit mínimo para el curso inicial está hecho: tareas 1 a 5 de `PLAN.md`, salvo el paso 4 de la tarea 4 (`curl`), que espera al curso. 265 pruebas (`python3 -m unittest discover -s herramientas/pruebas`). El curso inicial ha cerrado sus fases 1 a 3 con las herramientas del kit (la 3, la primera con scripts de bash y sesiones de terminal, a falta de la revisión del autor). La academia usa los cursos de ejemplo del kit (`94d93c8`).

| Herramienta | Qué hace |
|---|---|
| `formato_academia.py` | Que un curso cumple `FORMATO.md` y se puede instalar |
| `nucleo/verificar_codigo.py` | Que el código coincide con `codigo/` y funciona: bash (también con bash 3.2), sesiones de terminal y de Git, JSON, YAML, XML, CSV y Markdown; con Docker, en la terminal del kit |
| `nucleo/declarar_ejercicios.py` | Declara los ejercicios de un módulo en `curso.json` sin cambiar identificadores |
| `nucleo/generar_indice.py`, `nucleo/generar_chuleta_global.py` | `00-indice.md` y `99-chuleta-global.md`, desde `curso.json` |
| `nucleo/comprobar_mermaid.py` | Que los diagramas se dibujan, con Mermaid 12.2.0 (la de la academia) y 10.9.8 |
| `nucleo/reemplazar.py` | Sustituciones en varios ficheros, todas o ninguna |

Todo documentado en `herramientas/README.md`, con «Por dónde empezar».

## Siguiente paso

- **`curl` con un servidor local pequeño** (tarea 4, paso 4; la fase 6 del curso inicial), cuando el curso diga qué API necesitan sus ejercicios (rutas, respuestas, códigos de estado).
- **Comparar un CSV con su JSON** para el reto de la fase 4 del curso (en CSV todo es texto), cuando el curso lo escriba.
- Mientras, el kit no tiene nada que bloquee al curso ni a la academia. Lo que pidan al escribir (como en el 02.03), sobre la marcha.

## Lo hecho, tarea a tarea, y sus decisiones

**Tarea 1 (8 de noviembre de 2026).** `README.md` del kit (con el arranque de un curso paso a paso, probado en una carpeta temporal), `LICENSE` (MIT, «Santiago (santi-cast)», elegido por el autor) y `plantillas/` (`curso.json`, `modulo.md`, `retos.md`, `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`, `.gitignore`, y los opcionales `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md`). Los huecos se marcan con `[RELLENAR: …]`.

**Decisiones del apartado 4 de `PLAN.md` y ajustes de `FORMATO.md`** (todos dentro de la versión 1: las versiones cuentan desde la primera publicación). Fichero previsto de los módulos y los retos no disponibles; títulos en texto plano; una fase que solo tiene el proyecto final no necesita retos (los tres, pedidos por el curso inicial); ficheros de verificación y salidas en el texto, los del curso de Java tal cual (7.1); numeración de subapartados (5.1); «Conviene saber antes», solo enlaces (5.2); el HTML que admite la academia (10.5); cualquier curso puede tener su glosario (9); los cursos de ejemplo viven en el kit (14).

**Tarea 2: `formato_academia.py`.** Un solo fichero, solo la biblioteca de Python. Probado con el curso inicial y con una copia del curso de Java (199 módulos, con un `curso.json` provisional que genera `herramientas/pruebas/curso_json_de_java.py`; las copias, fuera del kit). Decisiones:
- Un enlace a un módulo o retos con `"disponible"`/`"retos_disponibles": false` es aviso (y avisa de que su ancla no se puede comprobar); a un fichero que no existe ni está previsto, error (pedido del autor).
- El HTML se comprueba como el saneador de la academia (`ContentSanitizer` de Code Academy, leído el 8 de noviembre de 2026): admite `code`, `kbd`, `br`, `sup`… y no admite `<details open>`.
- Las anclas, con la regla de `comprobar_enlaces.py` de Java, conservando el código en línea (`Page<T>` → `paget`, como GitHub) y numerando los repetidos.
- `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md` de un curso son ficheros de trabajo: no se revisan.
- El glosario (el común del curso inicial y el propio de cualquier curso): orden alfabético español, con la ñ entre la n y la o; un término repetido es un error.
- No hay `comprobar_enlaces.py` aparte (decisión del autor): `formato_academia.py` ya lo hace; `--fichero` y la comprobación de todos los cursos a la vez, para más adelante (`PLAN.md`).
- **Lo que dirá de Java al adaptarlo** (copia del 8 de noviembre de 2026): 199 «Requisitos previos», 88 títulos de ejercicio con formato, 28 «Conviene saber antes» con texto además de enlaces (se reescriben con anclas), 38 líneas de Mermaid con `<b>`, 1.622 ejercicios sin pistas, sin preguntas de repaso, `<i>` en algún `<summary>` y unas 300 imágenes en `codigo/` en vez de `img/` (aviso).

**Tarea 3: las herramientas del núcleo de Java.** `nucleo/generar_indice.py`, `generar_chuleta_global.py`, `comprobar_mermaid.py` y `argumentos.py`; las rutas, desde la raíz del curso (la carpeta actual), no desde la del script. Decisiones:
- El índice saca el nivel y el tiempo de la cabecera de cada módulo: los pendientes salen con «—» y el índice se completa solo (el autor prefiere no añadir horas previstas a `curso.json`: es temporal).
- La chuleta global, con la copia de Java, sale idéntica a la original salvo una línea de ejemplo dentro de un bloque ` ```` ` que el original reescribía mal.
- **Mermaid** (decisión del autor): la biblioteca **12.2.0**, la de la academia (manda la academia), y la **10.9.8**, por GitHub; fijadas las dos, porque mermaid-cli solo pide un rango (ya existe la 12.3.0). Se suben junto con la de la academia.

**Tarea 4: `verificar_codigo.py` y los comprobadores**, en el orden en que escribe el curso:
- **Paso 1, bash y sesiones de terminal.** El núcleo del de Java, sin Java, con sus convenciones. **Docker para la verificación completa** (sin red con `--network none` y las mismas versiones en cualquier máquina); **sin Docker, parcial y avisando** (`unshare --net` no funciona sin permisos en Ubuntu; no se toca la seguridad del sistema).
- **La terminal del kit** (`servicios/terminal/Dockerfile`): Ubuntu 26.04.1 por su huella; **Git 2.56.0** compilado del código oficial (SHA-256) con sus traducciones, **como el paquete de Ubuntu** (`prefix=/usr`, `gitexecdir=/usr/lib/git-core`) y con `NO_RUST=1` (desde Git 3.0 habrá que instalar Rust); **bash 3.2.57** compilado en la misma imagen (firma de Chet Ramey verificada; no la imagen oficial `bash:3.2.57`, que es de Alpine con BusyBox y daría diferencias falsas); `language-pack-es-base` (bash, coreutils, grep, sed y tar en español); **coreutils de GNU 9.7**, no las uutils (Rust) de Ubuntu 26.04, con mensajes en inglés o a medias, fechas en inglés y otro orden en `ls` (decisión del autor, 9 de noviembre de 2026, por lo que vio el curso en su fase 3); hora de Madrid. La persona `alumno` con `USER`, `LOGNAME` y `SHELL`; bash 3.2, en un contenedor limpio; la pantalla convierte los tabuladores en espacios, como una terminal (el `ls` de GNU alinea con ellos). Los demás paquetes (`file`, `tree`, `curl`…), sin fijar hasta que den un problema (decisión del autor), pero la imagen guarda la lista de lo instalado (`verificar_codigo.py --versiones`).
- **No se comprueba** que `sed`, `date` o `ls` se comporten igual en macOS (BSD frente a GNU): lo cubren los avisos de cada módulo.
- **Paso 2, JSON, YAML (PyYAML), XML, CSV y Markdown**: cada fichero de datos de una carpeta enlazada, válido (o que falle, con `debe-fallar.txt`), y un `.json` y un `.yaml` con el mismo nombre, con los mismos datos.
- **Paso 3, Git**: sesiones de terminal con el **reloj de Git** (decisión del autor: fechas fijas que avanzan un minuto por commit desde el 15 de enero de 2026 a las 10:00). Está en `/usr/bin/git`, donde lo tiene Ubuntu, con el Git de verdad fuera del `PATH` (`command -v git` da `/usr/bin/git`, como pidió el curso). Sin paginador. Git no traduce las fechas ni el resumen «1 file changed…» (igual en el Git de Ubuntu).

**Tarea 5: `herramientas/README.md`**, revisado entero para quien llega nuevo (9 de noviembre de 2026).

**Además, a petición del curso inicial**: `nucleo/reemplazar.py` (de su `.verificacion/`, mejorado: `--comprobar`, `--raiz`, saltos de línea de Windows y vuelta atrás si una escritura falla) y `nucleo/declarar_ejercicios.py` (de su `publicar.py`: reconoce los ejercicios solo por su título y, si uno cambia, para y pregunta; decisiones del autor).

**Datos de esta máquina** (8 de noviembre de 2026): Docker 29.9.2, Node 24.22.1 y Chrome, el *locale* `es_ES.UTF-8` y Git 2.53.0 del sistema.

## Dependencias con el curso inicial

Se trabaja a la vez que `../curso-inicial/`. **Lee su `ESTADO.md` (solo leer) al empezar cada sesión y antes de cerrar cada tarea**, y actualiza esta tabla.

| El kit espera del curso inicial | Para | Estado |
|---|---|---|
| Qué ejercicios y retos de herramientas lleva (terminal, Git, Markdown, JSON, YAML, XML, CSV) y qué hay que comprobar de cada uno | Tarea 4 (comprobadores de formatos) y decisión 1 del apartado 4 de `PLAN.md` | **Hecho** (commit 7ee70c2 del curso, 8 de noviembre de 2026): su `ESTADO.md`, «Lista para el kit»; resumida en la tarea 4 de `PLAN.md` |
| Uso real de las herramientas del kit | Saber que funcionan con un curso de verdad | **9 de noviembre de 2026:** fase 3 cerrada (sus commits 31d3455 a 808380e), verificada entera con la imagen `8a8282d`: 25 scripts (también con bash 3.2) y 53 sesiones, 0 errores y 0 avisos; ejercicios declarados con `declarar_ejercicios.py`. Antes, fase 2 cerrada (sus commits 925d8f5 a 5ae82f5): las 3 sesiones del 02.03 pasan `verificar_codigo.py` con Docker y la terminal nueva; `formato_academia.py`, 0 errores. Su fase 3 es la primera con scripts de bash y sesiones de verdad |
| Su `curso.json` y la fase 1 escritos | Probar `formato_academia.py` con un curso real | `curso.json` **hecho** (commit 068fd7c del curso, 8 de noviembre de 2026): 8 fases y 31 módulos con su fichero previsto, todos con `"disponible": false`, y los retos con `"retos_disponibles": false`. Revisado a mano: encaja con `FORMATO.md`. Fase 1: pendiente |

| El curso inicial espera del kit | Para | Estado |
|---|---|---|
| `formato_academia.py` | Comprobar y cerrar su fase 1 | **Hecho** (8 de noviembre de 2026): `herramientas/formato_academia.py` |
| `generar_indice.py` | Generar `00-indice.md` (sus módulos ya lo enlazan) | **Hecho** (8 de noviembre de 2026): `herramientas/nucleo/generar_indice.py` |
| `verificar_codigo.py` con bash y las sesiones de terminal | Verificar los ejemplos y ejercicios de bash de sus fases 2 y 3 | **Hecho** (8 de noviembre de 2026): `herramientas/nucleo/verificar_codigo.py` |
| Sesiones de Git reproducibles (reloj de Git) | Su fase 5 | **Hecho** (8 de noviembre de 2026) |
| Comprobadores de JSON, YAML, XML, CSV y Markdown | Su fase 4 | **Hecho** (8 de noviembre de 2026): `verificar_codigo.py` |
| `reemplazar.py` en las herramientas comunes (para que el curso borre su copia de `.verificacion/`) | Sustituciones en varios ficheros, todas o ninguna | **Hecho** (9 de noviembre de 2026): `herramientas/nucleo/reemplazar.py`. El curso ya la usa y borró su copia (su commit 1fa43e2) |
| `declarar_ejercicios.py` (de su `publicar.py`) y la comprobación del glosario en `formato_academia.py` | Declarar ejercicios sin cambiar identificadores; editar el glosario a mano desde su fase 3 | **Hecho** (9 de noviembre de 2026): `herramientas/nucleo/declarar_ejercicios.py`; el glosario, con orden alfabético español y términos repetidos como error |
| Coreutils de GNU (no uutils) en la terminal del kit; `$USER` en las sesiones; bash 3.2 en un contenedor limpio | Las salidas de su fase 3 | **Hecho** (9 de noviembre de 2026; las coreutils, decisión del autor). Su fase 3 tiene que volver a verificarse: 16 salidas cambian (fechas, orden de `ls`, «el directorio» y tabuladores) |
| La terminal del kit, con bash y las herramientas en español y `command -v git` en `/usr/bin/git` | Las sesiones de su módulo 02.03 | **Hecho** (9 de noviembre de 2026): `language-pack-es-base` en la imagen y el reloj de Git en `/usr/bin/git` |
| `generar_chuleta_global.py` y `comprobar_mermaid.py` | Generar `99-chuleta-global.md` y comprobar sus diagramas | **Hecho** (8 de noviembre de 2026): `herramientas/nucleo/` |
| Verificar con salidas en español (`LC_ALL`), rama `main`, Git con autor y fechas fijos, servidor HTTP local y compatibilidad con bash 3.2 | Sus ejercicios y retos de las fases 2 a 8 | **Hecho** todo menos el servidor HTTP local (`curl`, tarea 4, paso 4), que espera a que el curso diga qué API necesita su fase 6 |
| Permisos fijos en la terminal del kit: `ls -l` dependía de la umask de quien clona (pedido por el curso inicial y la raíz al verificar su fase 3 en un clon, 9 de noviembre de 2026) | Que la verificación dé lo mismo en cualquier máquina | **Hecho** (9 de noviembre de 2026): al copiar a la terminal (con y sin Docker, desde el disco o con `--commit`), ficheros 644 (755 si son ejecutables) y carpetas 755. Sus salidas ya están escritas así: no cambia nada |
| Verificar como en un clon (la fase 3 falló en un clon limpio y en el disco del autor no: carpetas vacías, permisos y CRLF no viajan con Git; propuesto por la raíz, 9 de noviembre de 2026) | Cerrar cada fase con lo que recibe el alumno | **Hecho** (9 de noviembre de 2026): `verificar_codigo.py --commit [ref]` y avisos de carpetas vacías, scripts lanzados con `./` sin permiso en Git y permisos que no viajan en `formato_academia.py`. Probado con su fase 3 desde su commit `feec868`: 25 scripts y 54 sesiones, 0 errores y 0 avisos; `formato_academia.py`, ningún aviso nuevo. La regla común de `Cursos/CLAUDE.md` la cambia la raíz |
| Saltos de línea LF: `.gitattributes` en la plantilla y aviso de CRLF (pedido al revisar su fase 3, 9 de noviembre de 2026) | Que los scripts y sus datos no se rompan en Windows | **Hecho** (9 de noviembre de 2026): `plantillas/.gitattributes` con `* text=auto eol=lf` y dos avisos en `formato_academia.py`. **Le toca al curso:** cambiar su `.gitattributes` (hoy solo `*.sh text eol=lf`) por el de la plantilla; hoy le da un aviso. Para el ejemplo del 03.04 no hace falta ningún fichero nuevo: si algún fichero tiene CRLF a propósito, se marca con `-text` |
| Las convenciones de verificación del curso de Java en `FORMATO.md` (7.1) | Saber cómo se escriben las salidas y sesiones verificables | **Hecho** (8 de noviembre de 2026, dentro de la versión 1) |
| No avisar de la falta de retos en una fase que solo contiene el proyecto final (su aviso 3) | Su fase 8 | **Hecho** en `FORMATO.md`, apartado 6 (8 de noviembre de 2026, dentro de la versión 1) |
| Plantillas (`curso.json`, módulo, retos) | Puede empezar sin ellas, siguiendo `FORMATO.md` | **Hecho** (8 de noviembre de 2026): `plantillas/` |
| Ajustes de `FORMATO.md` (sus avisos 1 y 2): fichero previsto de los módulos con `"disponible": false` y de los retos con `"retos_disponibles": false`; títulos en texto plano | Escribir su `curso.json` con los nombres cerrados | **Hecho** (8 de noviembre de 2026, dentro de la versión 1). El curso ya los aplicó (su commit 068fd7c) |

Si algo bloquea, dilo al autor: él pasa la información de una sesión a otra.

## Hecho

| Fecha | Qué |
|---|---|
| 2026-11-08 | Repositorio creado; `FORMATO.md` versión 1 movido desde la raíz. |
| 2026-11-08 | Decisiones 1 a 3 del apartado 4 de `PLAN.md`. Ajustes de `FORMATO.md` dentro de la versión 1 (apartados 3.2, 7, 13 y 15). |
| 2026-11-08 | Aviso 3 del curso inicial en `FORMATO.md` (fase del proyecto final sin retos) y su lista de comprobaciones en la tarea 4 de `PLAN.md`. |
| 2026-11-08 | `FORMATO.md`: regla de numeración de subapartados (5.1), «Conviene saber antes» con ancla (5.2) y el HTML que admite la academia (10.5). |
| 2026-11-08 | Tarea 1: README del kit, `LICENSE` (MIT, «Santiago (santi-cast)», elegido por el autor) y plantillas. |
| 2026-11-08 | Tarea 2: `formato_academia.py`, sus pruebas y su documentación; `curso_json_de_java.py`. |
| 2026-11-08 | Tarea 3, primera parte: `nucleo/generar_indice.py` y `nucleo/argumentos.py`. |
| 2026-11-08 | Tarea 3 terminada: `nucleo/generar_chuleta_global.py` y `nucleo/comprobar_mermaid.py`. |
| 2026-11-08 | `FORMATO.md` 7.1: ficheros de verificación y salidas en el texto (las convenciones del curso de Java). |
| 2026-11-08 | Tarea 4, paso 1: `verificar_codigo.py` con bash y las sesiones de terminal, y la imagen de la terminal del kit. |
| 2026-11-08 | Tarea 4, paso 2: JSON, YAML, XML, CSV y Markdown. |
| 2026-11-08 | Tarea 4, paso 3: Git, con el reloj de Git. |
| 2026-11-09 | Terminal del kit: coreutils de GNU 9.7 en lugar de uutils (decisión del autor), `USER`/`LOGNAME`/`SHELL` en sesiones y scripts, bash 3.2 en un contenedor limpio y los tabuladores de la pantalla en espacios (pedidos por el curso inicial al escribir su 03.02). |
| 2026-11-09 | Cursos de ejemplo para la academia (`bueno` y `ejemplo-destino`), `FORMATO.md` 9 y 14, y documentación al día: `ESTADO.md` ordenado por tareas, `PLAN.md` (estructura real y tarea 5), README del kit y plantilla `CLAUDE.md` (las herramientas al terminar cada módulo y «fichero», no «archivo»). |
| 2026-11-09 | `nucleo/declarar_ejercicios.py` (de la parte común del `publicar.py` del curso inicial): reconoce los ejercicios solo por su título y, si uno cambia, para y pregunta (decisiones del autor). `formato_academia.py`: el glosario en orden alfabético español (letras y términos, con la ñ) y sin términos repetidos. Probado con el curso inicial: su `curso.json` sale idéntico. |
| 2026-11-09 | Terminal del kit: `language-pack-es-base` 1:26.04+20260818 (bash, coreutils, grep, sed y tar en español) y el reloj de Git en `/usr/bin/git`, con el de verdad fuera del `PATH` (pedidos por el curso inicial al escribir su 02.03). Git compilado como el paquete de Ubuntu (`prefix=/usr`, `gitexecdir=/usr/lib/git-core`; nada en `/usr/local`), a propuesta del autor. La imagen guarda la lista de lo instalado con sus versiones (`verificar_codigo.py --versiones`); los paquetes de Ubuntu que no se fijan (`file`, `tree`, `curl`…), sin fijar hasta que den un problema real (decisión del autor). |
| 2026-11-09 | Verificar como en un clon (propuesto por la raíz, aprobado por el autor con tres ajustes de la raíz): `verificar_codigo.py --commit [ref]` (HEAD por defecto, también una etiqueta) con `git archive`, que solo lee (no `git worktree`, que escribe en el `.git` del curso) y da una copia como un clon (`docker cp` conserva los permisos: comprobado); avisa de los cambios sin commit. `formato_academia.py` avisa de carpetas vacías en `codigo/` (primero `mkdir` en la sesión; `.gitkeep`, segunda opción, con sus problemas), de scripts lanzados con `./` en una sesión sin permiso de ejecución en Git (salvo si la sesión hace su `chmod`: el «Permiso denegado» a propósito del 03.02 del curso daba un aviso de más, corregido) y de permisos del propietario que un clon no tendría. `FORMATO.md` 7, 13 y 15 (sin `export-ignore` en `codigo/`), plantilla `CLAUDE.md` y `herramientas/README.md`. Y permisos fijos en la terminal del kit (pedido por el curso y la raíz): ficheros 644 o 755 y carpetas 755 al copiarlos, con y sin Docker, para que `ls -l` no dependa de la umask ni de `git archive`. 29 pruebas nuevas. |
| 2026-11-09 | Saltos de línea (pedido por el curso inicial al revisar su fase 3; aprobado por el autor con los ajustes de la sesión de la raíz): `plantillas/.gitattributes` con `* text=auto eol=lf` (no una lista de tipos: también se rompen los datos que leen los scripts, como los registros, CSV y JSON), también en los cursos de ejemplo; `formato_academia.py` avisa (no da error: el fallo real ya lo da `verificar_codigo.py`) de los ficheros de texto de `codigo/` con CRLF en lo que guarda Git (`git ls-files --eol`; sin Git, el disco) y de los que no saldrían con LF en un clon; respeta `-text`. `FORMATO.md` 2, 7, 13 y 15, dentro de la versión 1. Nota para la academia (de la raíz, para H7): los ZIP de código, con los ficheros del commit, no los de una copia en disco. |
| 2026-11-09 | Tarea 5: `herramientas/README.md` revisado entero (por dónde empezar, qué hay en cada carpeta, lo común a todas, sin repeticiones ni datos desfasados). `nucleo/reemplazar.py`, incorporado desde el curso inicial (con `--raiz`, `--comprobar`, saltos de línea de Windows y vuelta atrás si una escritura falla), con sus pruebas. |

## Cursos de ejemplo para la academia

**9 de noviembre de 2026:** la academia usa los cursos de ejemplo del kit (`herramientas/pruebas/cursos/bueno/` y `ejemplo-destino/`) como sus únicos cursos de ejemplo, con una copia sacada de un commit fijo del kit. **Si se cambian, hay que avisar a la academia del commit.** Hecho a petición suya: `FORMATO.md` 14 (los cursos de ejemplo viven en el kit), `ejemplo-destino` (id y repositorio propios, para no chocar con el curso inicial real: decisión del autor; un módulo que es su proyecto de tipo `"modulo"` y su glosario), y en `bueno` un enlace a un módulo de `ejemplo-destino` con ancla, otro a un término de su glosario y el «Siguiente» del último módulo a `retos.md`. Además, `FORMATO.md` 9 (aprobado por el autor): cualquier curso puede tener su propio glosario; el común sigue siendo el del curso inicial.

## Prueba de importación en la academia

**9 de noviembre de 2026:** la academia ha importado la fase 1 del curso inicial (commit c2bfba8 de su repositorio). **`FORMATO.md` no cambia**: todo lo que no encajó es de la academia y lo arreglará su importador nuevo. Los identificadores con punto (`inicial.que-es-programar`) se aceptan tal cual, así que el apartado 3.3 se queda como está. Los cursos se instalan con una ruta relativa (`../Cursos/curso-inicial`), como dice el plan común.

## Para más adelante

- **Prueba de fiabilidad con el curso de Java:** cuando se adapte ese curso, después del pack base 1.0 (decisión del autor).

## Avisos de los cursos

Lo que las sesiones de los cursos encuentren que no encaja con `FORMATO.md` o con el kit (el autor lo trae aquí):

- **Curso inicial, 8 de noviembre de 2026:** que un módulo con `"disponible": false` pueda llevar su fichero previsto en `curso.json`, y lo mismo el `retos` de una fase sin retos escritos. **Resuelto** el mismo día en `FORMATO.md`, apartado 3.2 (los retos, con `"retos_disponibles": false`).
- **Curso inicial, 8 de noviembre de 2026:** títulos del curso, las fases, los módulos, los ejercicios y los retos en texto plano, en `curso.json` y en los encabezados, y que lo compruebe `formato_academia.py`. **Resuelto** el mismo día en `FORMATO.md`, apartados 3.2 y 13; la comprobación entra en la tarea 2.
- **Curso inicial, 8 de noviembre de 2026:** que no se avise de la falta de retos en una fase que solo contiene el proyecto final (su aviso 3). **Resuelto** el mismo día en `FORMATO.md`, apartado 6.
