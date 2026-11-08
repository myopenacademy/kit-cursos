# Estado del kit de cursos

> Actualízalo al terminar cada tarea. Es la memoria entre sesiones: lo que no esté aquí o en `PLAN.md` no lo sabrá la sesión siguiente.

## Dónde estamos

**8 de noviembre de 2026:** repositorio creado desde la sesión de la raíz, con `CLAUDE.md`, `PLAN.md`, `ESTADO.md`, `README.md`, `.gitignore` y `FORMATO.md` (versión 1, aprobada en el paso 0 y movida aquí desde la raíz). Ninguna herramienta ni plantilla todavía.

Resueltas con el autor las tres decisiones del apartado 4 de `PLAN.md`, y ajustado `FORMATO.md` dentro de la versión 1: fichero previsto de los módulos y los retos no disponibles (lo pidió el curso inicial) ficheros de verificación `debe-fallar.txt` y `separador.txt`, y títulos en texto plano (el curso de Java tendrá que quitar el formato de 88 títulos de ejercicio al adaptarlo).

**En paralelo:** una sesión en `../curso-inicial/` cierra su temario y escribe su fase 1 siguiendo `FORMATO.md`; cuando exista `formato_academia.py`, se comprueba con él.

## Siguiente paso

Tarea 1 de `PLAN.md`: el README del kit y las plantillas.

## Dependencias con el curso inicial

Se trabaja a la vez que `../curso-inicial/`. **Lee su `ESTADO.md` (solo leer) al empezar cada sesión y antes de cerrar cada tarea**, y actualiza esta tabla.

| El kit espera del curso inicial | Para | Estado |
|---|---|---|
| Qué ejercicios y retos de herramientas lleva (terminal, Git, Markdown, JSON, YAML, XML, CSV) y qué hay que comprobar de cada uno | Tarea 4 (comprobadores de formatos) y decisión 1 del apartado 4 de `PLAN.md` | Pendiente |
| Su `curso.json` y la fase 1 escritos | Probar `formato_academia.py` con un curso real | `curso.json` **hecho** (commit 068fd7c del curso, 8 de noviembre de 2026): 8 fases y 31 módulos con su fichero previsto, todos con `"disponible": false`, y los retos con `"retos_disponibles": false`. Revisado a mano: encaja con `FORMATO.md`. Fase 1: pendiente |

| El curso inicial espera del kit | Para | Estado |
|---|---|---|
| `formato_academia.py` | Comprobar y cerrar su fase 1 | Pendiente |
| Plantillas (`curso.json`, módulo, retos) | Puede empezar sin ellas, siguiendo `FORMATO.md` | Pendiente |
| Ajustes de `FORMATO.md` (sus avisos 1 y 2): fichero previsto de los módulos con `"disponible": false` y de los retos con `"retos_disponibles": false`; títulos en texto plano | Escribir su `curso.json` con los nombres cerrados | **Hecho** (8 de noviembre de 2026, dentro de la versión 1). El curso ya los aplicó (su commit 068fd7c) |

Si algo bloquea, dilo al autor: él pasa la información de una sesión a otra.

## Hecho

| Fecha | Qué |
|---|---|
| 2026-11-08 | Repositorio creado; `FORMATO.md` versión 1 movido desde la raíz. |
| 2026-11-08 | Decisiones 1 a 3 del apartado 4 de `PLAN.md`. Ajustes de `FORMATO.md` dentro de la versión 1 (apartados 3.2, 7, 13 y 15). |

## Avisos de los cursos

Lo que las sesiones de los cursos encuentren que no encaja con `FORMATO.md` o con el kit (el autor lo trae aquí):

- **Curso inicial, 8 de noviembre de 2026:** que un módulo con `"disponible": false` pueda llevar su fichero previsto en `curso.json`, y lo mismo el `retos` de una fase sin retos escritos. **Resuelto** el mismo día en `FORMATO.md`, apartado 3.2 (los retos, con `"retos_disponibles": false`).
- **Curso inicial, 8 de noviembre de 2026:** títulos del curso, las fases, los módulos, los ejercicios y los retos en texto plano, en `curso.json` y en los encabezados, y que lo compruebe `formato_academia.py`. **Resuelto** el mismo día en `FORMATO.md`, apartados 3.2 y 13; la comprobación entra en la tarea 2.
