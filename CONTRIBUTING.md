# Cómo contribuir al kit de cursos

Gracias por querer mejorar el kit. Toda ayuda cuenta: una errata, una explicación más clara, un fallo de una herramienta o una comprobación que falta.

## Antes de empezar

- El kit tiene dos partes: **el formato** ([`FORMATO.md`](FORMATO.md)), que es el contrato entre la academia y los cursos, y **las herramientas** ([`herramientas/`](herramientas/README.md)), que lo comprueban.
- Escribe en **español de España**, tuteando.
- Si escribes un curso y algo no encaja con el formato o con las herramientas, ábrelo como *issue*: así se cambia el kit, no se hace un apaño en el curso.

## Cómo proponer un cambio

1. **Erratas, mensajes poco claros y fallos pequeños de las herramientas:** abre directamente una *pull request*.
2. **Cambios en `FORMATO.md`:** abre antes una *issue* para hablarlo. El formato **solo se cambia desde el kit**, con la aprobación del autor, y cada cambio sube su versión, dice qué cursos hay que poner al día y no impide a la academia leer las versiones anteriores (`FORMATO.md`, apartado 15).
3. **Una herramienta nueva o una comprobación nueva:** abre antes una *issue* con el caso real que la necesita (un curso, un módulo, un ejemplo).
4. En la *pull request*, explica qué cambias y por qué.

## Lo que se pide a cada cambio de las herramientas

- **Python 3.11 o posterior y solo la biblioteca de Python.** La única excepción aprobada es PyYAML, solo para comprobar YAML. Nada más sin hablarlo antes.
- **Pruebas:** cada cambio con las suyas, y todas pasando:

  ```bash
  python3 -m unittest discover -s herramientas/pruebas
  ```

  Las pruebas de la terminal del kit y de Mermaid necesitan Docker, y Node y Chrome; sin ellos, esas pruebas se saltan o lo dicen.
- **Su `--help`** al día y su apartado en [`herramientas/README.md`](herramientas/README.md).
- **Mensajes de error que digan el fichero, la línea y qué falta.**
- **Rutas relativas** siempre; lo que dependa de la máquina (dónde está Chrome…), en variables de entorno.
- **Los cursos de ejemplo** (`herramientas/pruebas/cursos/`) los usa también la academia en sus pruebas: si cambias algo en ellos, dilo en la *pull request*.

## Lo que el kit no puede comprobar

- **macOS:** la terminal del kit es Linux (Ubuntu, con Docker). Los scripts se ejecutan también con bash 3.2, el de macOS, pero no se comprueban las diferencias de las órdenes de BSD (`sed`, `date`, `ls`…) ni los mensajes de zsh. Si usas un Mac y ves algo distinto de lo que dice un curso o el kit, avísanos con una *issue*.
- **Windows:** Git Bash no se prueba en una máquina real; lo que se cuida es que los ficheros viajen con saltos de línea LF.

## Licencia de lo que aportes

Al contribuir aceptas que tu aportación se publique con la licencia del kit: MIT ([`LICENSE`](LICENSE)).
