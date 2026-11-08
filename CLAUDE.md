# Kit de cursos de MyOpenAcademy

Se suma a `../../CLAUDE.md` (reglas comunes) y `../CLAUDE.md` (reglas de todos los cursos).

## Antes de hacer nada en cada sesión

1. Lee `../../README.md`, `../../PLAN.md` (sobre todo los apartados 7 y 8.2) y `../../ESTADO.md`.
2. Lee `PLAN.md`, `ESTADO.md` y `FORMATO.md` de esta carpeta.
3. Lee, solo para saber cómo va, `../curso-inicial/ESTADO.md` y revisa la sección de dependencias de tu `ESTADO.md`: dile al autor si algo te bloquea o si la otra sesión necesita algo de esta.
4. Resume al autor en pocas líneas dónde se quedó el trabajo y qué toca a continuación.

## Coordinación con la sesión del curso inicial

El kit y el curso inicial (`../curso-inicial/`) se trabajan a la vez, en dos sesiones. El autor es quien pasa los mensajes de una a otra.

- **Orden:** la sesión del curso empieza primero (sus decisiones y su temario). Esta sesión puede empezar a la vez o un poco después.
- **Puedes avanzar sin el curso:** las decisiones 2 y 3 del apartado 4 de `PLAN.md`, las plantillas (tarea 1), `formato_academia.py` (tarea 2, se basa solo en `FORMATO.md`), las herramientas del núcleo sacadas del curso de Java (tarea 3) y su documentación.
- **Tienes que esperar al curso para:** los comprobadores de los formatos de sus ejercicios (tarea 4 y decisión 1 del apartado 4), que dependen de la lista de ejercicios y retos del curso; y para probar `formato_academia.py` con un curso real (su `curso.json` y su fase 1).
- **En cuanto `formato_academia.py` funcione**, avisa al autor para la sesión del curso: lo necesita para cerrar su fase 1.
- **Avísale al autor siempre que cambie algo que afecta a la otra sesión**: cuando termines algo que la otra espera, cuando necesites algo de ella o cuando encuentres algo que no encaja con `FORMATO.md`. Hazlo **al final de tu respuesta**, en un bloque aparte que empiece por «📣 **Para la sesión del curso inicial:**» y con el mensaje **listo para copiar y pegar** en la otra sesión (por ejemplo: «Mira el `ESTADO.md` del kit: ya está la lista de ejercicios del curso; con ella puedes hacer la tarea 4»).
- Antes de avisar, **actualiza la tabla de dependencias de tu `ESTADO.md`**, para que la otra sesión lo encuentre escrito aunque el autor no le pase el mensaje.
- **Si estás bloqueado** esperando a la otra sesión, dilo claramente, propón al autor en qué puedes avanzar mientras tanto y prepárale el mensaje para la otra.
- No toques nunca el repositorio de la otra sesión: solo lees su `ESTADO.md`.

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
