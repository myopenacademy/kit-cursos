# Plan del kit de cursos

> 8 de noviembre de 2026. Sale del plan general (`../../PLAN.md`, apartados 7 y 8.2) y del paso 0 (`FORMATO.md`).

## 1. Objetivo

Que se pueda **escribir un curso para MyOpenAcademy, verificarlo y saber que se puede instalar**. Primero, **lo justo para el curso inicial**; se amplía cuando lo pida el siguiente curso.

## 2. Estructura prevista

```
kit-cursos/
├── README.md                 ← qué es y cómo arrancar un curso nuevo, paso a paso
├── FORMATO.md                ← el contrato (versión 1)
├── plantillas/               ← lo que se copia al crear un curso, con huecos
│   ├── curso.json
│   ├── CLAUDE.md, PLAN-CURSO.md, ESTADO.md
│   ├── README.md, LICENSE, CONTRIBUTING.md, CHANGELOG.md, .gitignore
│   ├── modulo.md
│   └── retos.md
└── herramientas/
    ├── README.md
    ├── formato_academia.py   ← comprueba que un curso cumple FORMATO.md (la pieza central)
    ├── nucleo/               ← lo genérico: enlaces, Mermaid, índice y chuleta desde curso.json, argumentos…
    └── lenguajes/            ← un ejecutor por lenguaje o formato (al principio, los formatos del curso inicial)
```

## 3. Tareas para el curso inicial (versión mínima)

En este orden:

1. **README del kit** y **plantillas** (apartado 2), con `curso.json` de ejemplo y el módulo tipo de `FORMATO.md`.
2. **`formato_academia.py`**: todo lo del apartado 13 de `FORMATO.md` (`curso.json`, módulos, retos, glosario, proyecto, enlaces del mismo curso y entre cursos, imágenes, Mermaid, HTML, ficheros obligatorios), con errores y avisos, y el campo `transicion`. Con pruebas sobre cursos de ejemplo pequeños, buenos y malos.
3. **Del núcleo de las herramientas de Java**, lo que necesita el curso inicial:
   - `comprobar_enlaces.py`, ampliado a los enlaces entre cursos (dirección de GitHub → carpeta hermana).
   - `comprobar_mermaid.py` (necesita Node y Chrome; su ruta, en variables de entorno).
   - `generar_indice.py` y `generar_chuleta_global.py`, que pasan a leer `curso.json` en vez de una lista dentro del script.
   - `argumentos.py`.
4. **Comprobadores de los formatos del curso inicial** para sus ejemplos, ejercicios y retos: JSON, YAML, XML, CSV y Markdown; quizá comandos de terminal y Git (por decidir con el autor cuando se vea qué ejercicios lleva el curso).
5. **`herramientas/README.md`** con cada herramienta, sus requisitos y ejemplos.

**Después** (cuando lo pida el curso de Java): separar `verificar_codigo.py` (unas 1.500 líneas) en núcleo y ejecutores (Java, SQL, Node, páginas, Compose, Linux, plataformas…), `generar_modulo.py`, y la prueba de fiabilidad contra el curso de Java original. Y una comprobación de **todos los cursos a la vez**, para detectar enlaces rotos cuando un curso renombra un fichero.

## 4. Decisiones pendientes del autor

1. Qué se verifica de los ejercicios del curso inicial (formatos, comandos de terminal, Git) y cómo.
2. Si se acepta PyYAML como dependencia (hace falta para comprobar YAML de verdad).
3. Cómo se llaman y se organizan las herramientas (mantener los nombres del curso de Java o renombrar).
