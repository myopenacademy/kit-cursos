# Herramientas del kit

Las herramientas para comprobar los cursos de MyOpenAcademy. Se ejecutan **desde la raíz del curso**, con el kit en la carpeta hermana `../kit-cursos/`, sin copiarlas al curso.

## Requisitos

| Herramienta | Necesita |
|---|---|
| `formato_academia.py` | Python 3.11 o posterior, sin librerías adicionales. Git, solo para comparar con la última versión publicada (si no está, no compara). |
| `nucleo/generar_indice.py`, `nucleo/generar_chuleta_global.py` | Python 3.11 o posterior, sin librerías adicionales. |
| `nucleo/comprobar_mermaid.py` | **Node.js** (con `npx`) y **Google Chrome o Chromium** (si no está en un sitio habitual, su ruta en la variable `CHROME_PATH`). La primera vez, `npx` descarga mermaid-cli y la biblioteca Mermaid de las dos versiones en su caché, sin tocar el repositorio. Comprobado el 8 de noviembre de 2026 con Node 24.22.1 y Chrome en Linux. |

## Resumen

| Herramienta | Qué hace | Cuándo se usa |
|---|---|---|
| [`formato_academia.py`](#formato_academiapy) | Comprueba que el curso cumple `FORMATO.md` y se puede instalar en la academia | Al terminar cada módulo, al cerrar cada fase y antes de publicar una versión |
| [`nucleo/generar_indice.py`](#nucleogenerar_indicepy) | Genera `00-indice.md` desde `curso.json` | Al terminar cada módulo y al cambiar el temario |
| [`nucleo/generar_chuleta_global.py`](#nucleogenerar_chuleta_globalpy) | Genera `99-chuleta-global.md` con la chuleta de cada módulo | Al terminar cada módulo |
| [`nucleo/comprobar_mermaid.py`](#nucleocomprobar_mermaidpy) | Comprueba que los diagramas Mermaid se dibujan con dos versiones de Mermaid | Al terminar cada módulo con diagramas y al cerrar cada fase |
| [`nucleo/argumentos.py`](#nucleoargumentospy) | Revisión común de los argumentos de las herramientas del núcleo | La usan las herramientas; no se ejecuta a mano |
| [`pruebas/`](#las-pruebas) | Pruebas de las herramientas, con un curso de ejemplo bueno | Al cambiar una herramienta |

Los comprobadores del código de cada formato (JSON, YAML, XML, CSV, bash, Git…) están en preparación: `PLAN.md` del kit, tarea 4. No hay un `comprobar_enlaces.py` aparte: los enlaces y las anclas los comprueba `formato_academia.py`.

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
python3 ../kit-cursos/herramientas/formato_academia.py --help
```

Cada línea dice el fichero, la línea (si la hay) y qué pasa, y al final un resumen:

```text
fase-01-que-es-programar/01-que-es-programar.md:1275: ERROR: no existe ../00-indice.md
curso.json:16: AVISO: fase «inicial.fase.que-es-programar»: los retos todavía no están escritos

Curso «inicial» 0.1.0: 8 fases, 31 módulos (2 disponibles), 24 ejercicios; sin versiones etiquetadas todavía.
❌ El curso no cumple FORMATO.md (versión 1): 1 error y 1 aviso. No se puede instalar.
```

- **ERROR**: lo que `FORMATO.md` dice con «debe». El curso no se puede instalar.
- **AVISO**: lo que dice con «conviene», y lo que no se ha podido comprobar. Se instala, pero conviene revisarlo.

Termina con **0** si no hay errores (aunque haya avisos), con **1** si hay alguno, y con **2** si los argumentos están mal (una opción desconocida o una carpeta que no existe), sin revisar nada.

### Detalles

- **Enlaces a lo que aún no está escrito.** Un enlace a un módulo con `"disponible": false` (o a unos retos con `"retos_disponibles": false`) es un **aviso**, para revisarlo cuando se escriba; si lleva ancla, avisa de que no se podrá comprobar hasta entonces. Un enlace a un fichero que no existe y que no está previsto en `curso.json` es un **error**.
- **Enlaces a otros cursos** (`https://github.com/myopenacademy/<curso>/blob/main/…`): se traducen a la carpeta hermana `../<curso>/` y se comprueban el fichero y el ancla; un módulo pendiente de ese curso (según su `curso.json`) es un aviso. Si la carpeta hermana no está, avisa de que no lo ha podido revisar. Deben apuntar a la rama `main`.
- **Anclas**: las que genera GitHub a partir del encabezado, con la misma regla que `comprobar_enlaces.py` del curso de Java (minúsculas, sin signos, espacios convertidos en guiones; los repetidos, con `-1`, `-2`…).
- **HTML**: el que admite la academia, como su saneador (visto en Code Academy el 8 de noviembre de 2026):
  - Se admiten tal cual `details`, `summary`, `code`, `kbd`, `br`, `sup`, `sub`, `em`, `strong`, `del`, tablas, listas, párrafos y encabezados, sin atributos (salvo `align` en las celdas, `start` en `ol` y `class="language-…"` en `code`).
  - El formato sin efecto (`span`, `div`, `u`, `b`, `i`…) y los `<a>` los quita al instalar y deja su texto: **aviso**.
  - Cualquier otra etiqueta (`script`, `iframe`, `img`, `style`…) y cualquier otro atributo (`onclick`, `style`, `open`…) hacen fallar la instalación: **error**.
- **Mermaid**: sin negrita ni cursiva en las etiquetas (tampoco `<b>` o `<i>`), solo las entidades `&quot;`, `&lt;`, `&gt;` y `&amp;`, y sin directivas, *frontmatter*, `click`, `url()` ni `@import`. Que el diagrama se dibuje lo comprobará `comprobar_mermaid.py`.
- **Versiones publicadas**: si el curso tiene etiquetas `vX.Y.Z` en Git, compara los identificadores de la última con los de ahora; cada uno que haya desaparecido necesita su equivalencia (`FORMATO.md`, apartado 11.2).

## `nucleo/generar_indice.py`

Genera `00-indice.md` a partir de `curso.json`. Sale de `generar_indice.py` del curso de Java, que tenía la lista de fases y módulos dentro del script; aquí la lista es `curso.json`.

```bash
python3 ../kit-cursos/herramientas/nucleo/generar_indice.py              # escribe 00-indice.md
python3 ../kit-cursos/herramientas/nucleo/generar_indice.py --comprobar  # solo dice si está al día (1 si no)
python3 ../kit-cursos/herramientas/nucleo/generar_indice.py ../curso-x   # otro curso
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
python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py --comprobar  # solo dice si está al día (1 si no)
```

- Baja un nivel los encabezados de cada chuleta y corrige sus enlaces, anclas e imágenes relativos para que funcionen desde la raíz del curso. Lo que está dentro de un bloque de código no se toca.
- La chuleta de cada módulo termina en la sección siguiente («## 7. Preguntas de repaso») o en la línea `---` de la navegación.
- Diferencias con el de Java: los títulos de las fases salen de `curso.json` (no de `00-indice.md`), y los bloques de código de cuatro comillas (` ```` `) se reconocen bien (el de Java reescribía un enlace de ejemplo dentro de uno). Con la copia del curso de Java, el resultado es idéntico salvo en esa línea y en la frase de la cabecera.

## `nucleo/comprobar_mermaid.py`

Comprueba que cada bloque ` ```mermaid ` se dibuja sin errores con **dos versiones de la biblioteca Mermaid**, fijadas las dos (a 8 de noviembre de 2026):

| Biblioteca Mermaid | Con mermaid-cli | Por qué |
|---|---|---|
| **12.2.0** | 12.2.0 | Es la que usa **la academia** para dibujar los diagramas (`frontend/package.json` de Code Academy). |
| **10.9.8** | 10.9.1 | La antigua, la del curso de Java: por **GitHub** y los visores de Markdown, donde también se leen los cursos. |

- **Las dos se fijan**: mermaid-cli no fija la versión de la biblioteca que lleva dentro, solo un rango (`^12.2.0`), así que sin fijarla `npx` instalaría la última que encaje (el 8 de noviembre de 2026 ya existía la 12.3.0) y se comprobaría con una versión distinta de la de la academia sin que nadie se diera cuenta. Por eso la herramienta pide a `npx` los dos paquetes con su versión exacta.
- **La versión del kit tiene que coincidir con la de la academia.** Cuando la academia suba su `mermaid` en `frontend/package.json`, se sube a la vez la de `VERSIONES` en `comprobar_mermaid.py` (con el mermaid-cli que la admita, comprobado con `npm view @mermaid-js/mermaid-cli@<versión> dependencies.mermaid`) y esta tabla. También comprueba los bloques Mermaid que están dentro de otro bloque (por ejemplo, en las chuletas). Sale de `comprobar_mermaid.py` del curso de Java, con lo mismo que comprueba. Las reglas de `FORMATO.md` sobre Mermaid (sin negrita, entidades…) las mira `formato_academia.py`; esta, solo que se dibujen.

```bash
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py                         # todo el curso
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-01-que-es-programar # una carpeta o un fichero
python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-01-…/04-….md --imagenes /tmp/diagramas
```

Con `--imagenes`, guarda además cada diagrama como PNG para revisarlo a ojo. Termina con 0 si todos se dibujan, con 1 y la lista de los que fallan (fichero, línea donde empieza el bloque, versión y el error de Mermaid) o si falta Node o Chrome, y con 2 si los argumentos están mal. Ignora `codigo/`, `.verificacion/`, `herramientas/` y `node_modules/` dentro de lo que revisa.

## `nucleo/argumentos.py`

La revisión común de los argumentos, sacada de `argumentos.py` del curso de Java: `--help` muestra la ayuda de la herramienta, y una opción desconocida o una ruta que no existe terminan con código 2 sin hacer nada (así una ruta mal escrita no da un «✅» falso). Como las herramientas viven en el kit, las rutas se buscan desde la carpeta actual (la raíz del curso), no desde la carpeta del script.

## Las pruebas

En `pruebas/`:

- `cursos/bueno/`: un curso de ejemplo pequeño que cumple `FORMATO.md` (una fase con un módulo escrito y otro pendiente, retos, imagen, Mermaid y proyecto por etapas). Pasa sin errores.
- `test_generar_chuleta_global.py` y `test_comprobar_mermaid.py`: las de esas herramientas (las de Mermaid se saltan si no hay Node o Chrome).
- `test_generar_indice.py`: las de `generar_indice.py` (el índice del curso de ejemplo está al día, nivel y tiempo de la cabecera, pendientes sin enlace, `--comprobar`, y que el índice generado cumple `FORMATO.md`).
- `test_formato_academia.py`: cada prueba copia ese curso a una carpeta temporal, lo estropea de una forma concreta y comprueba que sale justo ese error o aviso. Así, si un cambio en el comprobador deja de detectar algo, una prueba falla.
- `curso_json_de_java.py`: genera un `curso.json` provisional para una **copia** del curso de Java original (que no lo tiene), para probar `formato_academia.py` con 199 módulos reales y como punto de partida de `curso-java/`. Su ayuda (`--help`) explica cómo sacar la copia solo con Git de lectura.

```bash
python3 -m unittest discover -s herramientas/pruebas -v     # desde la raíz del kit
```
