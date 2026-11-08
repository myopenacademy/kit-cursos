"""La terminal en la que se ejecutan los scripts y las sesiones de los cursos (para verificar_codigo.py; no se
ejecuta a mano).

CON DOCKER (la verificación completa): un contenedor de la imagen de servicios/terminal/Dockerfile (Ubuntu
26.04.1, Git 2.56.0 con sus traducciones, bash 3.2.57 además de la de Ubuntu, español y hora de Madrid), SIN RED
(--network none), con el nombre de máquina «ordenador» y la persona «alumno». La imagen se llama
kit-terminal:<huella del Dockerfile> y se construye la primera vez que hace falta (necesita internet esa vez).
Los ficheros de la carpeta del ejemplo se copian a /home/alumno con una fecha fija (15 de enero de 2026, 10:00),
para que «ls -l» no cambie de una verificación a otra.

SIN DOCKER (la verificación parcial): una bash del equipo, en una carpeta temporal que hace de carpeta personal,
con el español, la hora de Madrid y la misma configuración de Git (nombre, correo y rama main). La red NO se puede
cortar sin permisos de administrador: solo se apuntan los proxies a una dirección muerta, que para curl, git y
los gestores de paquetes, pero no a un programa que abra la conexión por su cuenta. Las versiones son las del
equipo, así que una salida puede cambiar. Tampoco hay bash 3.2. Quien la usa debe avisar de todo esto.

EL RELOJ DE GIT (terminal/git-reloj, en los dos casos delante del git de verdad): los commits tienen fechas
fijas que avanzan un minuto cada uno desde el 15 de enero de 2026 a las 10:00, así que sus identificadores salen
siempre iguales y «git log» parece un historial real.

LAS SESIONES: cada orden se teclea en una bash interactiva con terminal (una pseudoterminal de 100 columnas), con
el indicador «$ », cuando la anterior ha terminado (cuando vuelve el indicador), y el resultado es la PANTALLA
FINAL, interpretada como lo haría una terminal (retornos de carro, borrados, colores fuera). Sin paginador
(GIT_PAGER y PAGER son «cat»): con una salida que no cabe en la pantalla, «git log» o «man» se quedarían esperando
una tecla; con una que cabe, se ve igual. Sale de las sesiones
«En tu terminal» del curso de Java (servidor_linux.py y bases_de_datos.py).
"""
import fcntl
import hashlib
import os
import re
import select
import shutil
import struct
import subprocess
import sys
import tempfile
import termios
import time
import uuid
from pathlib import Path

DOCKERFILE = Path(__file__).resolve().parent / "terminal" / "Dockerfile"
USUARIO = "alumno"
CASA = f"/home/{USUARIO}"
FECHA_FICHEROS = "2026-01-15 10:00:00"
ANCHO = 100
ESPERA_ORDEN = 120          # segundos que puede tardar una orden de una sesión
ESPERA_SCRIPT = 60          # segundos que puede tardar un script
INDICADOR = re.compile(r"\$")
CTRL_C = re.compile(r"^@ctrl-c\s+(\d+(?:\.\d+)?)\s*$")
CONFIG_GIT = "[user]\n\tname = Ana García\n\temail = ana@example.com\n[init]\n\tdefaultBranch = main\n"
PROXY_MUERTO = "http://127.0.0.1:9"

# Interpretar la pantalla (de bases_de_datos.py del curso de Java)
SECUENCIA = re.compile(r"\x1b\[([0-9;?]*)([A-Za-z@])|\x1b\][^\x07]*\x07|\x1b[=>()][0-9A-Za-z]?|\r|\n|\x08|\x07"
                       r"|[^\x1b\r\n\x08\x07]")
OSC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
COLOR = re.compile(r"\x1b\[[0-9;:]*m")


class ErrorDeTerminal(RuntimeError):
    pass


def hay_docker():
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "info"], capture_output=True).returncode == 0


def _docker(*argumentos, entrada=None, comprobar=True):
    r = subprocess.run(["docker", *argumentos], input=entrada, capture_output=True)
    if comprobar and r.returncode != 0:
        raise ErrorDeTerminal(f"docker {' '.join(argumentos[:2])} falla:\n"
                              f"{(r.stdout + r.stderr).decode('utf-8', 'replace').strip()[-2000:]}")
    return r


def imagen():
    """El nombre de la imagen de la terminal, construyéndola si todavía no existe."""
    huella = hashlib.sha256(DOCKERFILE.read_bytes()).hexdigest()[:12]
    nombre = f"kit-terminal:{huella}"
    if _docker("image", "inspect", nombre, comprobar=False).returncode != 0:
        print(f"Construyendo la imagen {nombre} (la primera vez tarda unos minutos y necesita internet)…",
              file=sys.stderr, flush=True)
        _docker("build", "-q", "-t", nombre, str(DOCKERFILE.parent))
    return nombre


def pantalla(texto):
    """Lo que queda en una terminal tras escribir `texto` en ella: interpreta el retorno de carro, el salto de
    línea, el retroceso y las secuencias que mueven el cursor y borran (las demás, como los colores, no cambian el
    texto). Devuelve las líneas, sin espacios al final."""
    texto = COLOR.sub("", OSC.sub("", texto))
    lineas, fila, col = [[]], 0, 0

    def linea(i):
        while len(lineas) <= i:
            lineas.append([])
        return lineas[i]

    for m in SECUENCIA.finditer(texto):
        t = m.group(0)
        if t == "\r":
            col = 0
        elif t == "\n":
            fila += 1
            linea(fila)
        elif t == "\x08":
            col = max(0, col - 1)
        elif t.startswith("\x1b["):
            n = int(m.group(1)) if m.group(1).isdigit() else None
            orden = m.group(2)
            if orden == "A":
                fila = max(0, fila - (n or 1))
            elif orden == "B":
                fila += n or 1
                linea(fila)
            elif orden == "C":
                col += n or 1
            elif orden == "D":
                col = max(0, col - (n or 1))
            elif orden == "G":
                col = (n or 1) - 1
            elif orden == "K":
                actual = linea(fila)
                if not n:
                    del actual[col:]
                elif n == 1:
                    actual[:col] = [" "] * min(col, len(actual))
                else:
                    actual.clear()
            elif orden == "J" and not n:
                del linea(fila)[col:]
                del lineas[fila + 1:]
        elif not t.startswith("\x1b") and t != "\x07":
            if col >= ANCHO:
                fila, col = fila + 1, 0
            actual = linea(fila)
            actual.extend(" " * (col - len(actual)))
            if col < len(actual):
                actual[col] = t
            else:
                actual.append(t)
            col += 1
    return ["".join(l).rstrip() for l in lineas]


def ordenes_de(texto):
    """Las órdenes de un sesion.txt, cada una con los segundos tras los que se pulsa Ctrl+C (o None)."""
    ordenes = []
    for linea in texto.splitlines():
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        ctrl_c = CTRL_C.match(linea.strip())
        if ctrl_c:
            if not ordenes:
                raise ErrorDeTerminal("«@ctrl-c» sin una orden antes")
            ordenes[-1] = (ordenes[-1][0], float(ctrl_c.group(1)))
        else:
            ordenes.append((linea, None))
    return ordenes


def _teclear(orden_de_la_shell, ordenes, **opciones):
    """Teclea las órdenes en una bash con terminal y devuelve la pantalla, desde la primera orden hasta el último
    indicador (sin él). Sale de servidor_linux._teclear del curso de Java."""
    maestro, esclavo = os.openpty()
    fcntl.ioctl(esclavo, termios.TIOCSWINSZ, struct.pack("HHHH", 50, ANCHO, 0, 0))
    proceso = subprocess.Popen(orden_de_la_shell, stdin=esclavo, stdout=esclavo, stderr=esclavo,
                               start_new_session=True, **opciones)
    os.close(esclavo)
    bruto = b""

    def leer(segundos):
        nonlocal bruto
        listos, _, _ = select.select([maestro], [], [], segundos)
        if listos:
            try:
                bruto += os.read(maestro, 65536)
            except OSError:
                return False
        return True

    def esperar_indicador(lineas_antes, espera, orden="", continuacion=False):
        limite = time.time() + espera
        while time.time() < limite:
            if not leer(0.05):
                break
            actual = pantalla(bruto.decode("utf-8", "replace"))
            if len(actual) > lineas_antes and (actual[-1] == ">" if continuacion else INDICADOR.fullmatch(actual[-1])):
                return len(actual)
        raise ErrorDeTerminal(f"la orden «{orden}» no termina:\n"
                              + "\n".join(pantalla(bruto.decode("utf-8", "replace"))[-30:]))

    try:
        lineas = esperar_indicador(0, 30, "(arrancar bash)")
        inicio = lineas - 1
        for orden, ctrl_c in ordenes:
            os.write(maestro, (orden + "\r").encode("utf-8"))
            if ctrl_c is not None:
                limite = time.time() + ctrl_c
                while time.time() < limite:
                    leer(0.05)
                os.write(maestro, b"\x03")
            lineas = esperar_indicador(lineas, ESPERA_ORDEN, orden, orden.rstrip().endswith("\\"))
    finally:
        proceso.kill()
        proceso.wait()
        os.close(maestro)
    final = pantalla(bruto.decode("utf-8", "replace"))[inicio:]
    if final and INDICADOR.fullmatch(final[-1]):
        final.pop()
    return "\n".join(final) + "\n"


def _copiables(carpeta, excluir):
    return [f for f in sorted(carpeta.iterdir()) if f.name not in excluir and f.name not in {"target", "build"}]


class Contenedor:
    """La terminal con Docker: `with Contenedor(carpeta) as t: t.ejecutar(...)`."""
    completa = True

    def __init__(self, carpeta, excluir=()):
        self.carpeta, self.excluir = Path(carpeta), set(excluir)

    def __enter__(self):
        self.nombre = f"kit-terminal-{uuid.uuid4().hex[:10]}"
        _docker("run", "-d", "--rm", "--network", "none", "--hostname", "ordenador", "--name", self.nombre,
                imagen(), "sleep", "infinity")
        try:
            for f in _copiables(self.carpeta, self.excluir):
                _docker("cp", str(f), f"{self.nombre}:{CASA}/{f.name}")
            _docker("exec", "-u", "0", self.nombre, "bash", "-c",
                    f"chown -R {USUARIO}:{USUARIO} {CASA} && find {CASA} -mindepth 1 -not -name '.*' "
                    f"-exec touch -h -d '{FECHA_FICHEROS}' {{}} +")
        except Exception:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *_):
        _docker("rm", "-f", self.nombre, comprobar=False)

    def ejecutar(self, orden, entrada=None, espera=ESPERA_SCRIPT):
        """Ejecuta la orden (lista) en la carpeta personal: (código, salida, salida de error)."""
        try:
            r = subprocess.run(["docker", "exec", "-i", "-w", CASA, self.nombre, *orden], input=entrada,
                               capture_output=True, timeout=espera)
        except subprocess.TimeoutExpired:
            raise ErrorDeTerminal(f"«{' '.join(orden)}» no termina en {espera} segundos")
        return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

    def sesion(self, ordenes):
        return _teclear(["docker", "exec", "-it", "-w", CASA, "-e", "TERM=xterm-256color", "-e", "PS1=$ ",
                         "-e", "PS2=> ", "-e", "GIT_PAGER=cat", "-e", "PAGER=cat", self.nombre,
                         "bash", "--noprofile", "--norc", "-i"], ordenes)


class Local:
    """La terminal sin Docker: una bash del equipo, sin aislar la red (ver la explicación del módulo)."""
    completa = False

    def __init__(self, carpeta, excluir=()):
        self.carpeta, self.excluir = Path(carpeta), set(excluir)

    def __enter__(self):
        self.casa = Path(tempfile.mkdtemp(prefix="kit-terminal-"))
        for f in _copiables(self.carpeta, self.excluir):
            (shutil.copytree if f.is_dir() else shutil.copy2)(f, self.casa / f.name)
        configuracion = Path(tempfile.mkdtemp(prefix="kit-git-")) / "gitconfig"
        configuracion.write_text(CONFIG_GIT, encoding="utf-8")
        # El reloj de Git, delante del git del equipo (como en la imagen)
        binarios = configuracion.parent / "bin"
        binarios.mkdir()
        shutil.copy2(DOCKERFILE.parent / "git-reloj", binarios / "git")
        self.entorno = {
            "PATH": f"{binarios}:{os.environ.get('PATH', '/usr/bin:/bin')}", "HOME": str(self.casa), "USER": USUARIO,
            "KIT_GIT_REAL": shutil.which("git") or "git", "KIT_RELOJ": str(configuracion.parent / "reloj"),
            "LANG": "es_ES.UTF-8", "LC_ALL": "es_ES.UTF-8", "LANGUAGE": "es_ES:es", "TZ": "Europe/Madrid",
            "TERM": "xterm-256color", "PS1": "$ ", "PS2": "> ", "COLUMNS": str(ANCHO), "GIT_PAGER": "cat", "PAGER": "cat",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": str(configuracion),
            **{v: PROXY_MUERTO for v in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy")},
            "no_proxy": "", "NO_PROXY": "",
        }
        self.entorno.pop("GIT_CONFIG_NOSYSTEM")            # la de sistema es la del kit (GIT_CONFIG_SYSTEM)
        self._config = configuracion
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.casa, ignore_errors=True)
        shutil.rmtree(self._config.parent, ignore_errors=True)

    def ejecutar(self, orden, entrada=None, espera=ESPERA_SCRIPT):
        try:
            r = subprocess.run(orden, input=entrada, capture_output=True, timeout=espera, cwd=self.casa, env=self.entorno)
        except subprocess.TimeoutExpired:
            raise ErrorDeTerminal(f"«{' '.join(orden)}» no termina en {espera} segundos")
        return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

    def sesion(self, ordenes):
        return _teclear(["bash", "--noprofile", "--norc", "-i"], ordenes, cwd=self.casa, env=self.entorno)


def terminal(carpeta, excluir=(), con_docker=None):
    """La terminal para la carpeta: con Docker si lo hay (o si con_docker es True), y si no, la local."""
    if con_docker is None:
        con_docker = hay_docker()
    return Contenedor(carpeta, excluir) if con_docker else Local(carpeta, excluir)
