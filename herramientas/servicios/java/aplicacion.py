#!/usr/bin/env python3
"""Arranca una aplicación web de Spring Boot, le hace las peticiones de su peticiones.txt con curl y la para (para
lenguajes/java.py; no se ejecuta a mano). Va en la imagen de Java (/opt/kit-java/aplicacion.py) y, sin Docker, se usa
desde aquí: así, con y sin Docker, todo pasa igual, dentro de la terminal (con Docker, sin red: solo localhost).

    python3 aplicacion.py < encargo.json

El encargo (JSON, por la entrada estándar):
    {"servidores": [{"tipo": "java", "carpeta": "...", "orden": ["java", ..., "Api.java"]},
                    {"tipo": "spring", "carpeta": "...", "orden": ["java", "-jar", "...jar", "--server.port=8082"],
                     "puerto": 8082, "nombre": "catalogo"}],
     "aplicacion": {"carpeta": "...", "orden": ["java", ..., "paquete.Clase"], "nombre": "Aplicacion.java"},
     "peticiones": ".../peticiones.txt", "espera": 60}
Escribe en la salida estándar un JSON: {"sesion": "..."} si todo va bien, o {"error": "..."} (y termina con 1).

Sale de herramientas/verificar_codigo.py (aplicacion_web, sesion_curl, campo_json) y herramientas/paginas.py
(servidor, un_servidor) del curso de Java, con las mismas reglas:
  - Los servidores del servidor.txt se arrancan antes, en orden, cada uno cuando el anterior ya escucha, y se paran
    al final en el orden contrario. Un programa de Java escribe en su primera línea «Escuchando en
    http://localhost:PUERTO/»; otro proyecto de Spring Boot, se espera a que acepte conexiones en su puerto.
  - La aplicación se arranca en un puerto libre (--server.port) y se espera a que acepte conexiones.
  - Cada línea de peticiones.txt: un comentario (#, se muestra delante de la orden siguiente), «curl …» (con
    -sS; localhost:8080 pasa a ser el puerto real, y en la respuesta vuelve a ser 8080), «VAR=$(curl … | jq -r
    .campo)» (guarda la respuesta, o ese campo, sin mostrar nada; luego $VAR o ${VAR}), «curl … | jq -r .campo»
    (solo ese campo), «sleep N» (espera) y «cp origen destino» (copia, relativo a la carpeta de peticiones.txt;
    al terminar, el destino vuelve a quedar como estaba).
  - De cada respuesta se quita la cabecera Date, y los métodos de la cabecera Allow se ordenan.
"""
import contextlib
import json
import re
import shlex
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

PUERTO_DEL_TEXTO = "localhost:8080"
CABECERA_DATE = re.compile(r"^Date: .*\n", re.M | re.I)
CABECERA_ALLOW = re.compile(r"^Allow: (.*)$", re.M)
ESCUCHANDO = re.compile(r"(http://localhost:\d+)/?")
ASIGNACION_CURL = re.compile(r"^([A-Z][A-Z0-9_]*)=\$\((curl .+?)(?:\s*\|\s*jq -r (\.[A-Za-z0-9_.]+))?\)$")
VARIABLE_CURL = re.compile(r"\$\{?([A-Z][A-Z0-9_]*)\}?")
COPIA = re.compile(r"^cp (\S+ \S+)$")
ESPERA = re.compile(r"^sleep (\d+(?:\.\d+)?)$")
TUBERIA_JQ = re.compile(r"^(curl .+?)\s*\|\s*jq -r (\.[A-Za-z0-9_.]+)$")


class Fallo(RuntimeError):
    pass


def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def campo_json(texto, ruta):
    """Lo que daría «jq -r .a.b» con un JSON sencillo: el campo (texto tal cual; otro valor, en JSON)."""
    valor = json.loads(texto)
    for parte in [p for p in ruta.split(".") if p]:
        valor = valor.get(parte) if isinstance(valor, dict) else None
    return valor if isinstance(valor, str) else json.dumps(valor)


def leer_en_hilo(proceso, registro):
    threading.Thread(target=lambda: registro.extend(proceso.stdout), daemon=True).start()


def parar(proceso):
    proceso.terminate()
    try:
        proceso.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proceso.kill()
        proceso.wait()


def esperar_puerto(proceso, puerto, registro, nombre, espera):
    limite = time.monotonic() + espera
    while True:
        if proceso.poll() is not None:
            time.sleep(0.2)
            raise Fallo(f"{nombre} termina sin llegar a escuchar (código {proceso.returncode}):\n"
                        + "".join(registro)[-2000:])
        try:
            socket.create_connection(("127.0.0.1", puerto), timeout=1).close()
            return
        except OSError:
            if time.monotonic() > limite:
                raise Fallo(f"{nombre} no escucha en el puerto {puerto} tras {espera} s:\n" + "".join(registro)[-2000:])
            time.sleep(0.2)


@contextlib.contextmanager
def un_servidor(servidor, espera):
    proceso = subprocess.Popen(servidor["orden"], cwd=servidor["carpeta"], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    try:
        if servidor["tipo"] == "java":
            primera = []
            hilo = threading.Thread(target=lambda: primera.append(proceso.stdout.readline()), daemon=True)
            hilo.start()
            hilo.join(espera)
            linea = primera[0] if primera else ""
            if not ESCUCHANDO.search(linea):
                proceso.kill()
                raise Fallo(f"{servidor['nombre']} no ha escrito su dirección (Escuchando en http://localhost:...):\n"
                            f"{linea}{proceso.stdout.read()[-1500:]}")
            threading.Thread(target=lambda: proceso.stdout.read(), daemon=True).start()   # que no se llene
        else:
            registro = []
            leer_en_hilo(proceso, registro)
            esperar_puerto(proceso, servidor["puerto"], registro, servidor["nombre"], espera)
        yield
    finally:
        parar(proceso)


def sesion(encargo):
    espera = encargo.get("espera", 60)
    lista = Path(encargo["peticiones"])
    app = encargo["aplicacion"]
    partes, comentarios, variables, copiados = [], [], {}, {}
    with contextlib.ExitStack() as pila:
        for servidor in encargo.get("servidores", []):
            pila.enter_context(un_servidor(servidor, espera))
        puerto = puerto_libre()
        proceso = subprocess.Popen([*app["orden"], f"--server.port={puerto}"], cwd=app["carpeta"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                   errors="replace")
        registro = []
        leer_en_hilo(proceso, registro)
        pila.callback(parar, proceso)
        esperar_puerto(proceso, puerto, registro, app["nombre"], espera)
        pila.callback(lambda: [destino.write_bytes(antes) if antes is not None else destino.unlink(missing_ok=True)
                               for destino, antes in copiados.items()])

        def mostrar(*lineas):
            nonlocal comentarios
            partes.append("\n".join([*comentarios, *lineas]))
            comentarios = []

        for linea in lista.read_text(encoding="utf-8").splitlines():
            if not linea.strip():
                continue
            if linea.startswith("#"):
                comentarios.append(linea.rstrip())
                continue
            pausa = ESPERA.match(linea.strip())
            if pausa:
                time.sleep(float(pausa.group(1)))
                mostrar("$ " + linea.rstrip())
                continue
            copia = COPIA.match(linea.strip())
            if copia:
                origen, destino = (lista.parent / ruta for ruta in shlex.split(copia.group(1)))
                destino = destino / origen.name if destino.is_dir() else destino
                if destino.resolve() not in copiados:
                    copiados[destino.resolve()] = destino.read_bytes() if destino.exists() else None
                destino.write_bytes(origen.read_bytes())
                mostrar("$ " + linea.rstrip())
                continue
            asignacion = ASIGNACION_CURL.match(linea.strip())
            tuberia = None if asignacion else TUBERIA_JQ.match(linea.strip())
            orden_curl = asignacion.group(2) if asignacion else tuberia.group(1) if tuberia else linea
            orden_curl = VARIABLE_CURL.sub(lambda m: variables.get(m.group(1), m.group(0)), orden_curl)
            argumentos = shlex.split(orden_curl)
            if not argumentos or argumentos[0] != "curl":
                raise Fallo(f"{lista.name}: cada línea es una orden curl, sleep, cp o un comentario (#): {linea}")
            argumentos = [a.replace(PUERTO_DEL_TEXTO, f"localhost:{puerto}") for a in argumentos[1:]]
            try:
                r = subprocess.run(["curl", "-sS", *argumentos], cwd=lista.parent, capture_output=True, timeout=espera)
            except subprocess.TimeoutExpired:
                raise Fallo(f"{lista.name}: {linea}\nno termina en {espera} s")
            if r.returncode != 0:
                raise Fallo(f"{lista.name}: {linea}\nfalla (código {r.returncode}): {r.stderr.decode('utf-8', 'replace')}"
                            f"\n--- registro de la aplicación ---\n" + "".join(registro)[-2000:])
            salida = r.stdout.decode("utf-8", "replace")
            if asignacion:
                variables[asignacion.group(1)] = (campo_json(salida, asignacion.group(3)) if asignacion.group(3)
                                                  else salida.strip())
                mostrar("$ " + linea.rstrip())
                continue
            if tuberia:
                mostrar("$ " + linea.rstrip(), campo_json(salida, tuberia.group(2)))
                continue
            respuesta = CABECERA_DATE.sub("", salida.replace("\r\n", "\n"))
            respuesta = respuesta.replace(f"localhost:{puerto}", PUERTO_DEL_TEXTO)
            respuesta = CABECERA_ALLOW.sub(lambda m: "Allow: " + ", ".join(sorted(x.strip() for x in m.group(1).split(","))),
                                           respuesta)
            respuesta = "\n".join(l.rstrip() for l in respuesta.rstrip().splitlines())
            mostrar("$ " + linea.rstrip(), respuesta)
    return "\n\n".join(partes)


def main():
    if len(sys.argv) > 1:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    try:
        print(json.dumps({"sesion": sesion(json.load(sys.stdin))}, ensure_ascii=False))
    except (Fallo, OSError, ValueError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
