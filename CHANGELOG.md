# Registro de cambios

Los cambios del kit de cursos de MyOpenAcademy, versión a versión. Las versiones siguen [versionado semántico](https://semver.org/lang/es/): la del kit es independiente de la del formato (`FORMATO.md`), que lleva su propio número.

## 1.0.0 — pendiente de publicar

La primera versión, publicada junto con la academia y el curso inicial (pack base 1.0). Preparada el 16 de noviembre de 2026.

- **`FORMATO.md`, versión 1**: el contrato entre la academia y los cursos (estructura, `curso.json`, módulos, retos, código y su verificación, enlaces, HTML, glosario, versiones, licencias y comprobación).
- **Plantillas** para arrancar un curso: `curso.json`, módulo, retos, `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`, `.gitignore` y `.gitattributes`, y los opcionales `CLAUDE.md`, `PLAN-CURSO.md` y `ESTADO.md`.
- **`formato_academia.py`**: comprueba que un curso cumple el formato y se puede instalar. Solo con Python.
- **Herramientas del núcleo**: `verificar_codigo.py` (bash, también con bash 3.2; sesiones de terminal, de Git y de `curl` con un servidor HTTP local; JSON, YAML, XML, CSV, TSV, TOML, INI, SVG y Markdown; y `--commit`, para verificar como en un clon), `declarar_ejercicios.py`, `generar_indice.py`, `generar_chuleta_global.py`, `comprobar_mermaid.py` (Mermaid 12.3.0 y 10.9.8) y `reemplazar.py`.
- **La terminal del kit**: una imagen de Docker sin red, en español, con Ubuntu 26.04.1, Git 2.56.0, bash 3.2.57 y las coreutils de GNU, para que las salidas sean las mismas en cualquier máquina.
- **Dos cursos de ejemplo** (`herramientas/pruebas/cursos/`), que usa también la academia.
