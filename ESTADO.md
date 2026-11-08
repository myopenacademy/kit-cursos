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

Tarea 4 de `PLAN.md`: los comprobadores de los formatos del curso inicial (JSON, YAML, XML, CSV, Markdown, bash y Git, con sus condiciones comunes), según su «Lista para el kit». La tarea 5 (`herramientas/README.md`) se va haciendo con cada herramienta.

**Tarea 3 hecha:** además, `nucleo/generar_chuleta_global.py` (con la copia de Java, idéntica a la original salvo una línea de ejemplo dentro de un bloque ` ```` ` que el original reescribía mal, y la frase de la cabecera) y `nucleo/comprobar_mermaid.py` (mismas versiones que Java, mermaid-cli 12.0.0 y 10.9.1; probado con los 23 diagramas del curso inicial y los 31 de la fase 03 de Java). 130 pruebas. **Pendiente del autor:** la última mermaid-cli es la 12.2.0 (npm, 8 de noviembre de 2026); ¿se sube la reciente o se mantiene la 12.0.0 del curso de Java?

**Tarea 3, primera parte:** `herramientas/nucleo/generar_indice.py` y `herramientas/nucleo/argumentos.py`, con sus pruebas (117 en total). Decisión: el nivel y el tiempo salen de la cabecera de cada módulo, así que los pendientes salen con «—» y el índice se completa solo al escribirlos (el autor prefiere no añadir horas previstas a `curso.json`: es temporal). Probado con una copia del curso inicial: su índice generado cumple `FORMATO.md`, y el curso pasa con 0 errores.

**Datos de esta máquina para la tarea 4** (8 de noviembre de 2026): existe el *locale* `es_ES.UTF-8` y Git (2.53.0) responde en español con `LC_ALL=es_ES.UTF-8`; el bash es el 5.3.9, sin un bash 3.2 instalado (para eso, la imagen `bash:3.2` de Docker: tarea 4 de `PLAN.md`).

## Dependencias con el curso inicial

Se trabaja a la vez que `../curso-inicial/`. **Lee su `ESTADO.md` (solo leer) al empezar cada sesión y antes de cerrar cada tarea**, y actualiza esta tabla.

| El kit espera del curso inicial | Para | Estado |
|---|---|---|
| Qué ejercicios y retos de herramientas lleva (terminal, Git, Markdown, JSON, YAML, XML, CSV) y qué hay que comprobar de cada uno | Tarea 4 (comprobadores de formatos) y decisión 1 del apartado 4 de `PLAN.md` | **Hecho** (commit 7ee70c2 del curso, 8 de noviembre de 2026): su `ESTADO.md`, «Lista para el kit»; resumida en la tarea 4 de `PLAN.md` |
| Su `curso.json` y la fase 1 escritos | Probar `formato_academia.py` con un curso real | `curso.json` **hecho** (commit 068fd7c del curso, 8 de noviembre de 2026): 8 fases y 31 módulos con su fichero previsto, todos con `"disponible": false`, y los retos con `"retos_disponibles": false`. Revisado a mano: encaja con `FORMATO.md`. Fase 1: pendiente |

| El curso inicial espera del kit | Para | Estado |
|---|---|---|
| `formato_academia.py` | Comprobar y cerrar su fase 1 | **Hecho** (8 de noviembre de 2026): `herramientas/formato_academia.py` |
| `generar_indice.py` | Generar `00-indice.md` (sus módulos ya lo enlazan) | **Hecho** (8 de noviembre de 2026): `herramientas/nucleo/generar_indice.py` |
| `generar_chuleta_global.py` y `comprobar_mermaid.py` | Generar `99-chuleta-global.md` y comprobar sus diagramas | **Hecho** (8 de noviembre de 2026): `herramientas/nucleo/` |
| Verificar con salidas en español (`LC_ALL`), rama `main`, Git con autor y fechas fijos, servidor HTTP local y compatibilidad con bash 3.2 | Sus ejercicios y retos de las fases 2 a 8 | Anotado en la tarea 4 de `PLAN.md`; pendiente |
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

## Avisos de los cursos

Lo que las sesiones de los cursos encuentren que no encaja con `FORMATO.md` o con el kit (el autor lo trae aquí):

- **Curso inicial, 8 de noviembre de 2026:** que un módulo con `"disponible": false` pueda llevar su fichero previsto en `curso.json`, y lo mismo el `retos` de una fase sin retos escritos. **Resuelto** el mismo día en `FORMATO.md`, apartado 3.2 (los retos, con `"retos_disponibles": false`).
- **Curso inicial, 8 de noviembre de 2026:** títulos del curso, las fases, los módulos, los ejercicios y los retos en texto plano, en `curso.json` y en los encabezados, y que lo compruebe `formato_academia.py`. **Resuelto** el mismo día en `FORMATO.md`, apartados 3.2 y 13; la comprobación entra en la tarea 2.
- **Curso inicial, 8 de noviembre de 2026:** que no se avise de la falta de retos en una fase que solo contiene el proyecto final (su aviso 3). **Resuelto** el mismo día en `FORMATO.md`, apartado 6.
