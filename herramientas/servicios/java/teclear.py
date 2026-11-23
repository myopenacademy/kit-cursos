#!/usr/bin/env python3
"""Ejecuta un programa en una terminal simulada (pty) y teclea las líneas de un fichero cuando las espera, como una
persona (para lenguajes/java.py; no se ejecuta a mano). Solo Linux (mira en /proc si el programa espera teclado).

    python3 teclear.py ENTRADA SEGUNDOS -- orden [argumentos...]

ENTRADA es el entrada.txt (o «-» si no hay); SEGUNDOS, lo que puede tardar. Escribe en la salida estándar la
transcripción (lo que muestra la terminal: preguntas, lo tecleado y las respuestas, también System.err) y termina
con el código del programa, o con 124 (y «no termina» en la salida de error) si se pasa de tiempo.

Sale de sesion_terminal() de herramientas/verificar_codigo.py del curso de Java: cada línea se teclea cuando el
programa está bloqueado leyendo de su entrada (/proc/<pid>/task/*/syscall) y lleva PAUSA_TECLADO segundos sin
escribir nada; y no se teclea la siguiente hasta que ha recogido la anterior (/proc/<pid>/io). Sin más líneas,
Ctrl+D (fin de la entrada). Va en la imagen de Java (/opt/kit-java/teclear.py) y, sin Docker, se usa desde aquí.
"""
import os
import platform
import pty
import select
import subprocess
import sys
import time
from pathlib import Path

PAUSA_TECLADO = 0.2     # segundos sin que el programa escriba nada antes de teclear la línea siguiente
# El número de la llamada read() en cada arquitectura (el original solo conocía x86_64)
LLAMADA_READ = {"x86_64": 0, "aarch64": 63}.get(platform.machine(), 0)
NO_TERMINA = 124


def esperando_teclado(pid):
    """True si algún hilo del proceso está bloqueado leyendo de su entrada estándar."""
    for tarea in Path(f"/proc/{pid}/task").glob("*"):
        try:
            campos = (tarea / "syscall").read_text().split()
        except OSError:
            continue
        if len(campos) > 1 and campos[0] == str(LLAMADA_READ) and int(campos[1], 16) == 0:   # read(0, ...)
            return True
    return False


def lecturas(pid):
    """Número de llamadas de lectura que ha completado el proceso (/proc/<pid>/io)."""
    try:
        for linea in Path(f"/proc/{pid}/io").read_text().splitlines():
            if linea.startswith("syscr:"):
                return int(linea.split()[1])
    except OSError:
        pass
    return -1


def teclear(orden, pendientes, espera):
    """(código, transcripción) del programa, o (None, lo que llevaba) si no termina a tiempo."""
    maestro, esclavo = pty.openpty()
    proceso = subprocess.Popen(orden, stdin=esclavo, stdout=esclavo, stderr=esclavo, close_fds=True)
    os.close(esclavo)
    salida, limite = bytearray(), time.time() + espera
    ultima_salida = time.time()
    while True:
        if time.time() > limite:
            proceso.kill()
            proceso.wait()
            os.close(maestro)
            return None, salida.decode("utf-8", errors="replace")
        listos, _, _ = select.select([maestro], [], [], 0.05)
        if listos:
            try:
                datos = os.read(maestro, 4096)
            except OSError:
                datos = b""
            if not datos:
                break
            salida += datos
            ultima_salida = time.time()
            continue
        if proceso.poll() is not None:
            continue   # termina de vaciar la salida; os.read dará fin de fichero
        # Como una persona: no teclea hasta que el programa lleva un rato callado
        if time.time() - ultima_salida >= PAUSA_TECLADO and esperando_teclado(proceso.pid):
            antes = lecturas(proceso.pid)
            os.write(maestro, (pendientes.pop(0) + "\n").encode() if pendientes else b"\x04")
            hasta = time.time() + 5   # hasta que el programa recoja lo tecleado
            while lecturas(proceso.pid) == antes and proceso.poll() is None and time.time() < hasta:
                time.sleep(0.01)
    proceso.wait()
    os.close(maestro)
    texto = salida.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "")
    return proceso.returncode, texto


def main():
    argumentos = sys.argv[1:]
    if len(argumentos) < 4 or argumentos[2] != "--":
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    entrada, espera, orden = argumentos[0], float(argumentos[1]), argumentos[3:]
    pendientes = Path(entrada).read_text(encoding="utf-8").splitlines() if entrada != "-" else []
    codigo, texto = teclear(orden, pendientes, espera)
    sys.stdout.write(texto)
    if codigo is None:
        print(f"no termina en {espera:g} s", file=sys.stderr)
        sys.exit(NO_TERMINA)
    sys.exit(codigo)


if __name__ == "__main__":
    main()
