# [RELLENAR: nombre del curso] de MyOpenAcademy

[RELLENAR: si el curso está dentro de la carpeta común del autor: «Se suma a `../../CLAUDE.md` (reglas comunes) y `../CLAUDE.md` (reglas de todos los cursos).». Si no, borra esta línea.]

## Antes de hacer nada en cada sesión

1. Lee `PLAN-CURSO.md` y `ESTADO.md` de esta carpeta, y el contrato `../kit-cursos/FORMATO.md`.
2. Resume al autor en pocas líneas dónde se quedó el trabajo y qué toca a continuación.

## Qué es

[RELLENAR: qué enseña el curso y a quién va dirigido.] Identificador del curso: `[RELLENAR: id]`. En GitHub irá en `[RELLENAR: cuenta]/curso-[RELLENAR: nombre]`.

## Reglas de este curso

- Escribe en **español de España**, tuteando.
- **La calidad y la exactitud van por delante de la velocidad.** No recortes: cada módulo tiene la extensión que el tema necesite.
- Se escribe para un **principiante absoluto** en lo que trata el curso; solo se da por sabido lo que diga «Conviene saber antes».
- **Cumple `../kit-cursos/FORMATO.md`** (versión 1): estructura, nombres, plantilla de módulo (`../kit-cursos/plantillas/modulo.md`), retos de fase, títulos en texto plano. No lo copies ni lo cambies desde aquí: si algo no encaja, anótalo en `ESTADO.md` («Avisos para el kit») y díselo al autor.
- Teoría, ejemplos y ejercicios **de menor a mayor complejidad**, con **casos reales**; ejercicios en **cuatro niveles** (básico, intermedio, avanzado y caso real) con pistas y **soluciones completas, comentadas y explicadas**.
- **Verifica versiones y APIs** en la documentación oficial antes de escribir, y **fecha en el texto** los datos que caducan («a 8 de noviembre de 2026»). Nunca inventes APIs.
- **Ejecuta todo el código** antes de incluirlo. Cada programa completo va en `codigo/` de su fase, enlazado con «📁 Código». Las pruebas sueltas que no se publican, en `.verificacion/` (fuera de Git).
- **Salidas en español:** las salidas que muestra el curso son las de un sistema en español; el kit verifica con `LC_ALL=es_ES.UTF-8`.
- **Scripts de bash compatibles con bash 3.2** (el que trae macOS): nada de arrays asociativos, `mapfile`/`readarray`, `${var,,}`, `${var^^}`, `|&` ni `&>>`. Las diferencias de órdenes entre macOS y Linux (`sed -i`, `date`…) se avisan en el texto.
- **Git:** la rama principal es `main`.
- **Rutas relativas siempre**; lo que dependa de la máquina, en variables de entorno.
- **Nombres estables:** el temario y los nombres de fichero se cierran antes de escribir; los identificadores de `curso.json` no cambian nunca.

## Forma de trabajo

- **Por fases.** Al terminar cada módulo: `python3 ../kit-cursos/herramientas/formato_academia.py`, las comprobaciones del código de la fase, `ESTADO.md` al día y **un commit por módulo** (Conventional Commits: `docs(fase-01): añade el módulo …`).
- **Después de cada módulo, actualiza toda la documentación** que le afecte: índice, chuleta global, enlaces, `ESTADO.md`, plan, portada, roadmaps, módulos anteriores y proyecto.
- **Al cerrar cada fase:** comprobación entera tras el último cambio, enlaces de todo el curso, Mermaid, y apuntarlo en `ESTADO.md`. **Para** para que el autor la revise.
- **No cambies el plan por tu cuenta:** propón el cambio y espera la aprobación del autor.
- Commit o publicación solo cuando el autor lo pida o el plan lo diga.
