# Registro de cambios

Los cambios del kit de cursos de MyOpenAcademy, versión a versión. Las versiones siguen [versionado semántico](https://semver.org/lang/es/): la del kit es independiente de la del formato (`FORMATO.md`), que lleva su propio número.

## 1.1.0 — sin publicar

Pedida por el curso de Java (23 de noviembre de 2026) para adaptarse al kit, con lo que pidieron la academia y el autor por el camino. **El formato sigue en la versión 1**: los cambios son ampliaciones compatibles y forman la **revisión 1.1** de `FORMATO.md` (un curso que la usa sigue con `"formato": 1` y se instala en la academia 1.0.0, que ignora los campos que no conoce; comprobado el 23 de noviembre de 2026).

### Añadido

- **El ejecutor de Java** de `verificar_codigo.py` (`lenguajes/java.py`), sacado de las herramientas del curso de Java original: programas sueltos (también con `package` bajo `src/`), proyectos de Maven y Gradle (también multimódulo y con `settings.gradle` de Groovy), «**Sesión en la terminal:**», «**Salida de las pruebas:**» de JUnit (con el `salida-variable.txt` del `pom.xml`), `solo-compilar.txt` (y «Sin pruebas:», para construir sin ejecutar las pruebas), aplicaciones de Spring Boot probadas con `curl` (`peticiones.txt` y API simuladas con `servidor.txt`), y ventanas de JavaFX (`acciones.txt`) y Swing dibujadas sin pantalla y comparadas byte a byte («**La ventana:**»; la de ahora queda en `.verificacion/ventanas/`).
- **La imagen de Java** (`servicios/java/Dockerfile`), encima de la terminal del kit: Temurin 25.0.4.1+1, Maven 3.10.0 y Gradle 9.8.2 (las del autor con SDKMAN, fechadas el 23 de noviembre de 2026 con las más recientes anotadas), letras DejaVu y Pango fijados. **Ocupa 1,39 GB, unos 826 MB más que la terminal del kit** (aprobado por el autor). Gradle 9.8.2 pasará a la 9.9.x a la vez que el curso de Java revise sus versiones antes de publicar (la imagen y el curso, con las mismas); Temurin y Maven son parches y se quedan.
- **`verificar_codigo.py --preparar-java`**: la única vez que hay red. Llena la caché de Maven y Gradle (con Docker, el volumen `kit-java-cache` o el de `KIT_JAVA_CACHE`; sin Docker, `~/.m2/repository` o `KIT_JAVA_M2`, y `~/.gradle` o `GRADLE_USER_HOME`); después se verifica sin conexión.
- **`nucleo/generar_ruta_minima.py`**: genera `RUTA-MINIMA.md` desde `ruta_minima` de `curso.json`, con una plantilla del curso y sus huecos `{{resumen}}`, `{{modulos}}`, `{{proyecto}}` y `{{consultas}}`. `generar_indice.py` marca con 🧭 los módulos y las etapas de la ruta y enlaza a `RUTA-MINIMA.md`.
- **`FORMATO.md`, revisión 1.1** (23 y 24 de noviembre de 2026): los campos opcionales `ruta_minima` y `academia_minima` de `curso.json`; los ficheros de verificación de Java y sus salidas en el texto (7.1); un bloque puede enseñar un fichero de verificación; el ZIP de un enlace «📁 Código» dentro de un proyecto de Maven o Gradle es el del proyecto más exterior dentro de `codigo/` (solo la `codigo/` de una fase o de `proyecto/`; mezclados, el más exterior de todos; un Gradle sin `settings.gradle*`, la carpeta de su `build.gradle*` más exterior); y las partes, cada una un tramo de fases seguidas y en orden, sin partes vacías.
- **`formato_academia.py`**: comprueba `ruta_minima` (módulos y etapas que existen, sin repetir, y los huecos de su plantilla), `academia_minima` (`MAYOR.MENOR.PARCHE`) y las reglas nuevas de las partes, avisa si falta `RUTA-MINIMA.md` y si el texto de un «📁 Código» y su destino son carpetas distintas.
- `verificar_codigo.py --versiones` enseña también la lista de la imagen de Java.
- **Un curso de ejemplo de Java** para las pruebas (`herramientas/pruebas/cursos/java/`) y **la prueba de fiabilidad con el curso de Java** (`herramientas/pruebas/fiabilidad_java.py`): con su commit `cfb14f3e`, 2172 de 2244 bloques de Java coinciden con sus herramientas originales; lo que fallaba del kit está arreglado.

### Cambiado

- `verificar_codigo.py` tiene una lista de **ejecutores** (bash y Java): para cada fichero manda el primero que diga que es suyo.
- Un bloque igual a un fichero de verificación (`peticiones.txt`, `entrada.txt`…) cuenta como mostrado y no se ejecuta; antes era un error («el bloque no es igual a ningún fichero»).
- **Al verificar, la caché de Java es de solo lectura**: el volumen se monta con `:ro` (solo `--preparar-java` escribe en él), para que un programa o una construcción no cambien lo que usan los demás. Maven escribe en un repositorio local de cada contenedor con el del volumen detrás (`-Dmaven.repo.local.tail`), y Gradle, en un `GRADLE_USER_HOME` de cada contenedor con el volumen como caché de solo lectura (`GRADLE_RO_DEP_CACHE`).
- En `formato_academia.py`, el código en línea se lee como en CommonMark: un tramo de comillas invertidas no empieza a mitad de otro. Así da lo mismo que la academia (el `<template>` del 13.02 del curso de Java).

### Arreglado

- Con la revisión del código, antes de publicar: la imagen de una ventana nunca se guarda fuera de `.verificacion/ventanas/` (una imagen del texto fuera de la carpeta que se verifica es un error); un `server.port` que no es un número es un error con su fichero y su línea (con `${VARIABLE:número}`, el número), y un `solo-compilar.txt` que no está en UTF-8, también; con Maven y Gradle mezclados, el programa se construye con la herramienta de su módulo (antes, Maven siempre) y se copia el proyecto más exterior, como dice `FORMATO.md` 7.
- **Las pruebas ya no dependen del puerto 8080**: el servidor HTTP local de las pruebas escucha en un puerto libre que elige el sistema (con la academia en local, fallaban 37).
- Durante la prueba de fiabilidad (antes de publicar): programas sueltos con `package` bajo `src/`, Gradle sin demonio también en Docker («Timeout waiting to lock journal cache») y `--preparar-java` sin el *repackage* de Spring Boot (fallaba en proyectos sin clase con `main`).

## 1.0.0 — 23 de noviembre de 2026

La primera versión, publicada junto con la academia y el curso inicial (pack base 1.0). Preparada el 16 de noviembre de 2026.

- **`FORMATO.md`, versión 1**: el contrato entre la academia y los cursos (estructura, `curso.json`, módulos, retos, código y su verificación, enlaces, HTML, glosario, versiones, licencias y comprobación).
- **Plantillas** para arrancar un curso: `curso.json`, módulo, retos, `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`, `.gitignore` y `.gitattributes`, y los opcionales `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md`.
- **`formato_academia.py`**: comprueba que un curso cumple el formato y se puede instalar. Solo con Python.
- **Herramientas del núcleo**: `verificar_codigo.py` (bash, también con bash 3.2; sesiones de terminal, de Git y de `curl` con un servidor HTTP local; JSON, YAML, XML, CSV, TSV, TOML, INI, SVG y Markdown; y `--commit`, para verificar como en un clon), `declarar_ejercicios.py`, `generar_indice.py`, `generar_chuleta_global.py`, `comprobar_mermaid.py` (Mermaid 12.3.0 y 10.9.8) y `reemplazar.py`.
- **La terminal del kit**: una imagen de Docker sin red, en español, con Ubuntu 26.04.1, Git 2.56.0, bash 3.2.57 y las coreutils de GNU, para que las salidas sean las mismas en cualquier máquina.
- **Dos cursos de ejemplo** (`herramientas/pruebas/cursos/`), que usa también la academia.
