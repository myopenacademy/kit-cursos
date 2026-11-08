# Estado del kit de cursos

> Actualízalo al terminar cada tarea. Es la memoria entre sesiones: lo que no esté aquí o en `PLAN.md` no lo sabrá la sesión siguiente.

## Dónde estamos

**8 de noviembre de 2026:** repositorio creado desde la sesión de la raíz, con `CLAUDE.md`, `PLAN.md`, `ESTADO.md`, `README.md`, `.gitignore` y `FORMATO.md` (versión 1, aprobada en el paso 0 y movida aquí desde la raíz). **Tarea 1 hecha:** `README.md` del kit (con el arranque de un curso paso a paso, probado en una carpeta temporal), `LICENSE` (MIT) y `plantillas/` (`curso.json`, `modulo.md`, `retos.md`, `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`, `.gitignore`, y los opcionales `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md`). Los huecos se marcan con `[RELLENAR: …]`.

**Tarea 2 hecha:** `herramientas/formato_academia.py` (un solo fichero, solo la biblioteca de Python), documentado en `herramientas/README.md`, con 106 pruebas en `herramientas/pruebas/` sobre un curso de ejemplo bueno (`cursos/bueno/`) que se estropea de una en una. Probado además con el curso inicial (sus cuatro módulos de la fase 1, en una copia, marcados como disponibles: sin falsos positivos) y con una copia del curso de Java (199 módulos, con un `curso.json` provisional que genera `herramientas/pruebas/curso_json_de_java.py`; las copias, fuera del kit). Decisiones tomadas al hacerlo:
- Un enlace a un módulo o retos con `"disponible"`/`"retos_disponibles": false` es aviso (y avisa de que su ancla no se puede comprobar); a un fichero que no existe ni está previsto, error (pedido del autor).
- El HTML se comprueba como el saneador de la academia (`ContentSanitizer` de Code Academy, leído el 8 de noviembre de 2026), que admite más de lo que decía `FORMATO.md` 10.5 (`code`, `kbd`, `br`, `sup`…) y no admite `<details open>`. El autor aprobó reescribir 10.5 con esa lista («primero Markdown; HTML solo cuando no llega»).
- «Conviene saber antes»: solo enlaces separados por «·» (decisión del autor); para precisar la sección, el enlace lleva su ancla (`FORMATO.md` 5.2). Los 28 casos de Java con texto añadido se reescriben al adaptarlo.
- Las anclas, con la regla de `comprobar_enlaces.py` de Java, pero conservando el código en línea (`Page<T>` → `paget`, como GitHub) y numerando los repetidos.
- `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md` de un curso son ficheros de trabajo: no se revisan.
- Regla de numeración de subapartados en `FORMATO.md` 5.1 (aprobada por el autor y comprobada en Java): se numeran los de Teoría, Ejemplos, Errores típicos y Buenas prácticas; no los de Qué aprenderás, Ejercicios, Chuleta y Preguntas de repaso.
- **Lo que dirá de Java al adaptarlo** (copia de 8 de noviembre de 2026): 199 «Requisitos previos», 88 títulos de ejercicio con formato, 28 «Conviene saber antes» con texto además de enlaces (por ejemplo «(sección 1.7…)»), 38 líneas de Mermaid con `<b>`, 1.622 ejercicios sin pistas, sin preguntas de repaso, `<i>` en algún `<summary>` y unas 300 imágenes en `codigo/` en vez de `img/` (aviso).

Resueltas con el autor las tres decisiones del apartado 4 de `PLAN.md`, y ajustado `FORMATO.md` dentro de la versión 1: fichero previsto de los módulos y los retos no disponibles (lo pidió el curso inicial) ficheros de verificación `debe-fallar.txt` y `separador.txt`, y títulos en texto plano (el curso de Java tendrá que quitar el formato de 88 títulos de ejercicio al adaptarlo).

**En paralelo:** una sesión en `../curso-inicial/` cierra su temario y escribe su fase 1 siguiendo `FORMATO.md`; cuando exista `formato_academia.py`, se comprueba con él.

## Siguiente paso

Tarea 4 de `PLAN.md`, paso 4: `curl` con un servidor local pequeño (la fase 6 del curso inicial), cuando el curso diga qué API necesitan sus ejercicios. **Mientras**, el kit no tiene nada pendiente que bloquee al curso; según el autor (8 de noviembre de 2026), el curso ha reorganizado su fase 2: los ejercicios de bash empiezan en la fase 3 (en la 2 solo hay razonamiento y comprobar lo instalado); lo confirmará su sesión.

**Tarea 4, paso 3 hecho (Git):** las sesiones de Git se verifican con la terminal del kit. **Reloj de Git** (decisión del autor: fechas fijas que avanzan, no todas iguales): `servicios/terminal/git-reloj`, delante del `git` de verdad, da a cada orden que crea commits la fecha del reloj (desde el 15 de enero de 2026, 10:00) y lo adelanta un minuto si sale bien; respeta las fechas que ponga la sesión. Sin paginador (`GIT_PAGER=cat`) para que una salida larga no se quede esperando. Git no traduce las fechas ni el resumen «1 file changed…» (también así en el Git de Ubuntu). 181 pruebas.

**Tarea 4, paso 2 hecho:** `lenguajes/formato_json.py`, `formato_yaml.py` (PyYAML), `formato_xml.py`, `formato_csv.py` y `formato_markdown.py`, conectados a `verificar_codigo.py`: cada fichero de datos de una carpeta enlazada, válido (o que falle, con `debe-fallar.txt`), y un `.json` y un `.yaml` con el mismo nombre, con los mismos datos. 178 pruebas. Pendiente para el reto de la fase 4 (CSV de pedidos a JSON y YAML): comparar también un CSV con su JSON (los tipos difieren: en CSV todo es texto); se hará cuando el curso escriba ese reto.

**Tarea 4, paso 1 hecho:** `nucleo/verificar_codigo.py` (el núcleo de Java, sin Java), `lenguajes/bash.py` (scripts y lo que no existe en bash 3.2) y `servicios/terminal.py` con la imagen `servicios/terminal/Dockerfile`. 165 pruebas. Decisiones (del autor salvo donde se dice):
- **Docker para la verificación completa** (sin red con `--network none` y las mismas versiones en cualquier máquina); **sin Docker, parcial y avisando** (`unshare --net` no funciona sin permisos: Ubuntu limita los espacios de nombres de usuario; no se toca la seguridad del sistema).
- Imagen: Ubuntu 26.04.1 por su huella; **Git 2.56.0** compilado del código oficial (SHA-256) con sus traducciones, `sysconfdir=/etc` y `NO_RUST=1` (desde Git 3.0 habrá que instalar Rust); español y hora de Madrid. Comprobado: `git status` responde en español con la rama `main`.
- **bash 3.2.57 compilado en la misma imagen** (firma de Chet Ramey verificada), no la imagen oficial `bash:3.2.57`, porque esa es de Alpine con BusyBox y daría diferencias falsas en `ls`, `sort`, `grep` (decisión de esta sesión, anotada en `herramientas/README.md`). Así una diferencia es solo del bash: un `printf '%(%Y)T'` falla en la 3.2 y la búsqueda de texto no lo ve.
- **No se comprueba** que `sed`, `date`, `ls` se comporten igual en macOS (BSD frente a GNU): lo cubren los avisos de cada módulo (documentado). La tarea 5 (`herramientas/README.md`) se va haciendo con cada herramienta.

**Tarea 3 hecha:** además, `nucleo/generar_chuleta_global.py` (con la copia de Java, idéntica a la original salvo una línea de ejemplo dentro de un bloque ` ```` ` que el original reescribía mal, y la frase de la cabecera) y `nucleo/comprobar_mermaid.py` (probado con los 23 diagramas del curso inicial y los 31 de la fase 03 de Java). 130 pruebas. **Versiones de Mermaid** (decisión del autor, 8 de noviembre de 2026): la biblioteca **12.2.0**, la de la academia (manda la academia), y la **10.9.8**, por GitHub; fijadas las dos (mermaid-cli solo pide un rango y ya existe la 12.3.0). Se suben junto con la de la academia (`herramientas/README.md`).

**Tarea 3, primera parte:** `herramientas/nucleo/generar_indice.py` y `herramientas/nucleo/argumentos.py`, con sus pruebas (117 en total). Decisión: el nivel y el tiempo salen de la cabecera de cada módulo, así que los pendientes salen con «—» y el índice se completa solo al escribirlos (el autor prefiere no añadir horas previstas a `curso.json`: es temporal). Probado con una copia del curso inicial: su índice generado cumple `FORMATO.md`, y el curso pasa con 0 errores.

**Datos de esta máquina para la tarea 4** (8 de noviembre de 2026): existe el *locale* `es_ES.UTF-8` y Git (2.53.0) responde en español con `LC_ALL=es_ES.UTF-8`; el bash es el 5.3.9, sin un bash 3.2 instalado (para eso, la imagen `bash:3.2` de Docker: tarea 4 de `PLAN.md`).

## Dependencias con el curso inicial

Se trabaja a la vez que `../curso-inicial/`. **Lee su `ESTADO.md` (solo leer) al empezar cada sesión y antes de cerrar cada tarea**, y actualiza esta tabla.

| El kit espera del curso inicial | Para | Estado |
|---|---|---|
| Qué ejercicios y retos de herramientas lleva (terminal, Git, Markdown, JSON, YAML, XML, CSV) y qué hay que comprobar de cada uno | Tarea 4 (comprobadores de formatos) y decisión 1 del apartado 4 de `PLAN.md` | **Hecho** (commit 7ee70c2 del curso, 8 de noviembre de 2026): su `ESTADO.md`, «Lista para el kit»; resumida en la tarea 4 de `PLAN.md` |
| Uso real de las herramientas del kit | Saber que funcionan con un curso de verdad | **9 de noviembre de 2026:** fase 2 del curso cerrada (sus commits 925d8f5 a 5ae82f5): las 3 sesiones del 02.03 pasan `verificar_codigo.py` con Docker y la terminal nueva; `formato_academia.py`, 0 errores. Su fase 3 es la primera con scripts de bash y sesiones de verdad |
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
| La terminal del kit, con bash y las herramientas en español y `command -v git` en `/usr/bin/git` | Las sesiones de su módulo 02.03 | **Hecho** (9 de noviembre de 2026): `language-pack-es-base` en la imagen y el reloj de Git en `/usr/bin/git` |
| `generar_chuleta_global.py` y `comprobar_mermaid.py` | Generar `99-chuleta-global.md` y comprobar sus diagramas | **Hecho** (8 de noviembre de 2026): `herramientas/nucleo/` |
| Verificar con salidas en español (`LC_ALL`), rama `main`, Git con autor y fechas fijos, servidor HTTP local y compatibilidad con bash 3.2 | Sus ejercicios y retos de las fases 2 a 8 | Anotado en la tarea 4 de `PLAN.md`; pendiente |
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
| 2026-11-09 | `nucleo/declarar_ejercicios.py` (de la parte común del `publicar.py` del curso inicial): reconoce los ejercicios solo por su título y, si uno cambia, para y pregunta (decisiones del autor). `formato_academia.py`: el glosario en orden alfabético español (letras y términos, con la ñ) y sin términos repetidos. Probado con el curso inicial: su `curso.json` sale idéntico. |
| 2026-11-09 | Terminal del kit: `language-pack-es-base` 1:26.04+20260818 (bash, coreutils, grep, sed y tar en español) y el reloj de Git en `/usr/bin/git`, con el de verdad fuera del `PATH` (pedidos por el curso inicial al escribir su 02.03). Git compilado como el paquete de Ubuntu (`prefix=/usr`, `gitexecdir=/usr/lib/git-core`; nada en `/usr/local`), a propuesta del autor. La imagen guarda la lista de lo instalado con sus versiones (`verificar_codigo.py --versiones`); los paquetes de Ubuntu que no se fijan (`file`, `tree`, `curl`…), sin fijar hasta que den un problema real (decisión del autor). |
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
