# Kit de cursos de MyOpenAcademy

Se suma a `../../CLAUDE.md` (reglas comunes) y `../CLAUDE.md` (reglas de todos los cursos).

## Antes de hacer nada en cada sesión

1. Lee `../../README.md`, `../../PLAN.md` (sobre todo los apartados 7 y 8.2) y `../../ESTADO.md`.
2. Lee `PLAN.md`, `ESTADO.md` y `FORMATO.md` de esta carpeta.
3. Resume al autor en pocas líneas dónde se quedó el trabajo y qué toca a continuación.

## Qué es

El formato y las herramientas para escribir, verificar e instalar cursos en MyOpenAcademy. En GitHub irá en `myopenacademy/kit-cursos`. Los cursos lo usan desde `../kit-cursos/`, sin copiarlo.

## Reglas del kit

- **`FORMATO.md` es el contrato** entre la academia y los cursos, y **solo se cambia desde aquí**. Cada cambio se propone al autor, sube la versión del formato y anota qué cursos hay que poner al día. Si una sesión de un curso encuentra algo que no encaja, lo anota en el `ESTADO.md` de su curso y el autor lo trae aquí.
- **Lo justo:** primero, solo lo que necesita el curso inicial (pseudocódigo y herramientas: Markdown, JSON, YAML, XML, CSV, Git, terminal). Lo de Java y lo demás, cuando lo pida su curso.
- **Parte mínima pública** (`FORMATO.md`, plantillas y `formato_academia.py`): documentada para personas, sencilla y sin instalar nada raro. Las herramientas avanzadas son opcionales.
- **Origen:** las herramientas salen de `../../../Curso Java Completo/herramientas/`, que **solo se lee** (para copiar contenido de su repositorio, solo comandos de Git de lectura: `git show`, `git ls-tree`, `git cat-file`). Se separa lo genérico de lo de Java en un núcleo y ejecutores por lenguaje (`PLAN.md`).
- **Python 3.11 o posterior, sin librerías adicionales**, salvo las que el autor apruebe (el curso de Java ya aceptó PyYAML y jsonschema; para comprobar YAML hará falta PyYAML).
- Cada herramienta, con su `--help`, documentada en `herramientas/README.md` y con pruebas.
- **Rutas relativas** siempre; lo que dependa de la máquina (dónde está Node, Chrome…), en variables de entorno, nunca en el código.
- Mensajes de error que digan **fichero, línea y qué falta**.
- **Fiabilidad:** sobre una copia del curso de Java, el kit tiene que dar el mismo resultado que las herramientas originales (cuando se separe lo de Java).
- Escribe en español de España, tuteando. Commit cuando el autor lo pida o el plan lo diga.
