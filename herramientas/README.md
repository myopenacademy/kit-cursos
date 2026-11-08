# Herramientas del kit

Las herramientas para comprobar los cursos de MyOpenAcademy. Se ejecutan **desde la raíz del curso**, con el kit en la carpeta hermana `../kit-cursos/`, sin copiarlas al curso.

## Requisitos

| Herramienta | Necesita |
|---|---|
| `formato_academia.py` | Python 3.11 o posterior, sin librerías adicionales. Git, solo para comparar con la última versión publicada (si no está, no compara). |

## Resumen

| Herramienta | Qué hace | Cuándo se usa |
|---|---|---|
| [`formato_academia.py`](#formato_academiapy) | Comprueba que el curso cumple `FORMATO.md` y se puede instalar en la academia | Al terminar cada módulo, al cerrar cada fase y antes de publicar una versión |
| [`pruebas/`](#las-pruebas) | Pruebas de las herramientas, con un curso de ejemplo bueno | Al cambiar una herramienta |

Las demás (enlaces, Mermaid, índice, chuleta global y los comprobadores del código de cada formato) están en preparación: `PLAN.md` del kit, tareas 3 y 4.

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

## Las pruebas

En `pruebas/`:

- `cursos/bueno/`: un curso de ejemplo pequeño que cumple `FORMATO.md` (una fase con un módulo escrito y otro pendiente, retos, imagen, Mermaid y proyecto por etapas). Pasa sin errores.
- `test_formato_academia.py`: cada prueba copia ese curso a una carpeta temporal, lo estropea de una forma concreta y comprueba que sale justo ese error o aviso. Así, si un cambio en el comprobador deja de detectar algo, una prueba falla.
- `curso_json_de_java.py`: genera un `curso.json` provisional para una **copia** del curso de Java original (que no lo tiene), para probar `formato_academia.py` con 199 módulos reales y como punto de partida de `curso-java/`. Su ayuda (`--help`) explica cómo sacar la copia solo con Git de lectura.

```bash
python3 -m unittest discover -s herramientas/pruebas -v     # desde la raíz del kit
```
