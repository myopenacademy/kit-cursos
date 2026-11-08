# Kit de cursos de MyOpenAcademy

El formato y las herramientas para crear cursos para **MyOpenAcademy**, una academia de programación libre, gratuita y de código abierto que funciona como un juego con DLC: la academia es el juego y cada curso es una expansión que se instala, se actualiza sin perder el progreso y que cualquiera puede crear.

## Qué hay aquí

| Qué | Para qué |
|---|---|
| [`FORMATO.md`](FORMATO.md) | **El contrato**: cómo tiene que ser un curso para que la academia lo pueda instalar. Es lo primero que hay que leer. |
| [`plantillas/`](plantillas/) | Los ficheros que se copian al crear un curso, con huecos `[RELLENAR: …]`. |
| [`herramientas/`](herramientas/) | Las herramientas: [`formato_academia.py`](herramientas/README.md#formato_academiapy) (¿cumple el curso el formato?), las que verifican el código, generan el índice y la chuleta global y comprueban los diagramas, y dos cursos de ejemplo pequeños (`herramientas/pruebas/cursos/`). Empieza por [«Por dónde empezar»](herramientas/README.md#por-dónde-empezar). |

Para crear un curso basta con `FORMATO.md`, las plantillas y `formato_academia.py`, que solo necesita Python 3.11 o posterior, **sin Docker ni nada más**. Las demás herramientas son opcionales y cada una dice qué necesita: solo la **verificación completa del código** (`verificar_codigo.py`) pide Docker, y sin él verifica igualmente, de forma parcial y avisando.

## Las plantillas

| Plantilla | Qué es |
|---|---|
| [`curso.json`](plantillas/curso.json) | La identidad y la estructura del curso (`FORMATO.md`, apartado 3), con una fase, un módulo escrito, otro previsto y un proyecto por etapas. |
| [`modulo.md`](plantillas/modulo.md) | Un módulo con todas sus secciones, en orden (apartado 5). |
| [`retos.md`](plantillas/retos.md) | Los retos opcionales del final de una fase (apartado 6). |
| [`README.md`](plantillas/README.md) | La portada del curso (apartado 4). |
| [`LICENSE`](plantillas/LICENSE) | CC BY-SA 4.0 para el texto y MIT para el código (apartado 12). |
| [`CONTRIBUTING.md`](plantillas/CONTRIBUTING.md) | Cómo proponer cambios al curso. |
| [`CHANGELOG.md`](plantillas/CHANGELOG.md) | Qué cambia en cada versión (apartado 11). |
| [`.gitignore`](plantillas/.gitignore) | Lo que no se sube a Git. |
| [`CLAUDE.md`](plantillas/CLAUDE.md), [`PLAN-CURSO.md`](plantillas/PLAN-CURSO.md), [`ESTADO.md`](plantillas/ESTADO.md) | Opcionales: las reglas, el plan y el estado del curso, para quien lo escribe con un asistente (Claude Code u otro) o quiere llevar su planificación por escrito. |

## Cómo arrancar un curso nuevo

El kit y los cursos van en **carpetas hermanas**, y los cursos usan el kit desde ahí, sin copiarlo:

```text
Cursos/
├── kit-cursos/
├── curso-inicial/
└── curso-micurso/      ← el tuyo
```

1. **Crea el repositorio** del curso, `curso-<nombre>`, junto a `kit-cursos/`, y copia las plantillas de la raíz del curso (`modulo.md` y `retos.md` no: se copian dentro de cada fase cuando toque):

   ```bash
   mkdir curso-micurso
   cd curso-micurso
   git init -b main
   cp ../kit-cursos/plantillas/{curso.json,README.md,LICENSE,CONTRIBUTING.md,CHANGELOG.md,.gitignore} .
   cp ../kit-cursos/plantillas/{CLAUDE.md,PLAN-CURSO.md,ESTADO.md} .   # opcionales
   ```

2. **Decide lo general**: a quién va, qué conviene saber antes, versiones de las herramientas (comprobadas en su documentación oficial y con fecha), y el `id` del curso (corto, en minúsculas y único en la academia: `FORMATO.md`, apartado 3.3).
3. **Cierra el temario** antes de escribir: fases, módulos, nombres de fichero, tiempos, nivel, retos de cada fase y el proyecto para el portfolio. Escríbelo en `curso.json`; los módulos que aún no estén escritos llevan `"disponible": false`, y los retos aún sin escribir, `"retos_disponibles": false`.
4. **Escribe la primera fase** con `plantillas/modulo.md` y `plantillas/retos.md`, y comprueba el curso:

   ```bash
   python3 ../kit-cursos/herramientas/formato_academia.py
   ```

   Cada error dice el fichero, la línea y qué falta. Lo que se ejecuta al terminar cada módulo (declarar sus ejercicios, el índice, la chuleta global, el código, los diagramas) está en [«Por dónde empezar»](herramientas/README.md#por-dónde-empezar).

5. **El resto, fase a fase**, comprobando cada módulo al terminarlo y la fase entera al cerrarla.
6. **Publica**: anota la versión en `curso.json` y en `CHANGELOG.md`, etiquétala en Git (`v1.0.0`) e instálala en la academia.

Busca los huecos que te queden con `grep -rn RELLENAR .`.

## Licencia

MIT ([`LICENSE`](LICENSE)). Las plantillas de los cursos llevan su propia licencia, CC BY-SA 4.0 para el texto y MIT para el código.
