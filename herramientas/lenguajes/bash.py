"""El comprobador de los scripts de bash (para verificar_codigo.py; no se ejecuta a mano).

- ¿Es mío? Los ficheros .sh.
- Compatibilidad con bash 3.2 (la de macOS): busca lo que no existe en ella (arrays asociativos, mapfile,
  cambios de mayúsculas con ${var,,}, |&, &>>…). Funciona siempre, sin nada instalado. Es una búsqueda de
  texto: puede no ver algo escrito de forma rara, y por eso, con Docker, los scripts se ejecutan además con
  bash 3.2.57 (ver verificar_codigo.py).
- Ejecutarlo: «bash fichero.sh» (con los argumentos de args.txt y la entrada de entrada.txt), en la terminal del
  kit (servicios/terminal.py).
"""
import re
import shlex

EXTENSIONES = {".sh"}

# (expresión, qué es y desde qué bash existe). Se buscan en cada línea sin comentarios ni texto entre comillas simples
NO_EXISTE_EN_3_2 = [
    (re.compile(r"\b(declare|typeset|local)\s+(-\w*A\w*)\b"), "arrays asociativos (bash 4.0)"),
    (re.compile(r"\b(declare|typeset|local)\s+(-\w*n\w*)\b"), "referencias con -n (bash 4.3)"),
    (re.compile(r"(^|[;&|(]\s*|\s)(mapfile|readarray)\b"), "mapfile/readarray (bash 4.0)"),
    (re.compile(r"\$\{[#!]?\w+(\[[^\]]*\])?(,,?|\^\^?)[^}]*\}"), "cambiar mayúsculas con ${var,,} o ${var^^} (bash 4.0)"),
    (re.compile(r"\$\{\w+(\[[^\]]*\])?@[QEPAaUuLK]\}"), "transformaciones ${var@…} (bash 4.4)"),
    (re.compile(r"\|&"), "|& (bash 4.0): usa 2>&1 |"),
    (re.compile(r"&>>"), "&>> (bash 4.0): usa >> fichero 2>&1"),
    (re.compile(r"(^|[;&|\s])coproc\b"), "coproc (bash 4.0)"),
    (re.compile(r";;&|;&\s*$"), ";& o ;;& en un case (bash 4.0)"),
    (re.compile(r"\[\[\s+-v\s"), "[[ -v variable ]] (bash 4.2)"),
    (re.compile(r"\$\{\w+\[-\d+\]\}"), "índices negativos ${array[-1]} (bash 4.3)"),
    (re.compile(r"\bwait\s+-n\b"), "wait -n (bash 4.3)"),
    (re.compile(r"\bshopt\s+-s\s+(globstar|lastpipe|autocd|dirspell|checkjobs)\b"), "esa opción de shopt (bash 4.0 o posterior)"),
    (re.compile(r"\bread\b[^;|&]*\s-\w*i\b"), "read -i (bash 4.0)"),
    (re.compile(r"\$\{?(BASHPID|EPOCHSECONDS|EPOCHREALTIME|BASH_ARGV0)\b"), "esa variable (bash 4.0 o posterior)"),
    (re.compile(r"\{-?\d+\.\.-?\d+\.\.-?\d+\}"), "{inicio..fin..paso} (bash 4.0)"),
    (re.compile(r"\{0\d+\.\.\d+\}"), "{01..10} con ceros delante (bash 4.0)"),
]
COMILLAS_SIMPLES = re.compile(r"'[^']*'")


def es_mio(fichero):
    return fichero.suffix in EXTENSIONES


def incompatibilidades_3_2(texto):
    """[(número de línea, qué)] con lo que no existe en bash 3.2."""
    encontradas = []
    for n, linea in enumerate(texto.splitlines(), 1):
        codigo = COMILLAS_SIMPLES.sub("''", linea)
        if codigo.lstrip().startswith("#"):
            continue
        codigo = re.sub(r"\s#.*$", "", codigo)
        for patron, que in NO_EXISTE_EN_3_2:
            if patron.search(codigo):
                encontradas.append((n, que))
    return encontradas


def orden(fichero, carpeta, bash="bash"):
    """La orden para ejecutar el script, con los argumentos de args.txt si lo hay."""
    argumentos = []
    args = carpeta / "args.txt"
    if args.is_file():
        argumentos = shlex.split(args.read_text(encoding="utf-8").strip())
    return [bash, fichero.name, *argumentos]
