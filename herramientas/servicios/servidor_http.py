#!/usr/bin/env python3
"""El servidor HTTP local del kit: responde a curl en las sesiones y los scripts de un curso, sin internet.

Lo arranca la terminal del kit (servicios/terminal.py) antes de una sesión o un script cuya carpeta tiene un
servidor.json, y lo para después; no hace falta ejecutarlo a mano (aunque se puede, para probar un servidor.json:
ver «Uso»). Es genérico: no sabe nada de ninguna API. Cada ejemplo describe la suya en su servidor.json
(FORMATO.md, apartado 7.1):

    {
      "puerto": 8080,
      "rutas": [
        {"metodo": "GET", "ruta": "/libros", "estado": 200, "cuerpo": [{"id": 1, "titulo": "Niebla"}]},
        {"metodo": "GET", "ruta": "/libros/1", "estado": 200, "cuerpo": {"id": 1, "titulo": "Niebla"}},
        {"metodo": "POST", "ruta": "/libros", "estado": 201, "cabeceras": {"Location": "/libros/2"},
         "cuerpo": {"id": 2}},
        {"metodo": "GET", "ruta": "/estado", "estado": 200, "cuerpo": "Todo en orden\\n"}
      ]
    }

  - "puerto": opcional, 8080 si no se dice (entre 1024 y 65535). Escucha en localhost (127.0.0.1 y ::1).
  - "rutas": una o más. Cada una, con:
      "metodo"     GET, POST, PUT, PATCH, DELETE, HEAD u OPTIONS, en mayúsculas.
      "ruta"       empieza por «/». Sin «?», vale para cualquier consulta (/libros y /libros?autor=x); con «?», solo
                   para esa consulta exacta (y va antes que la que no la lleva).
      "estado"     el código de estado (200, 201, 404…), de los que conoce HTTP.
      "cabeceras"  opcional: nombre y valor, como texto; salen en ese orden.
      "cuerpo"     opcional: un TEXTO se envía tal cual (Content-Type «text/plain; charset=utf-8» si no se dice
                   otro); CUALQUIER OTRO VALOR (objeto, lista, número…) se envía como JSON con sangría de 2
                   espacios y un salto de línea al final (Content-Type «application/json» si no se dice otro).
                   Sin cuerpo, la respuesta va vacía.
    No se repite el mismo método con la misma ruta. Content-Length lo pone el servidor (no va en "cabeceras").

Lo que responde, siempre igual (para que la pantalla de una sesión no cambie):
  - HTTP/1.1, con la línea de estado de HTTP («HTTP/1.1 404 Not Found»), las cabeceras de la ruta, Content-Type
    (si hay cuerpo) y Content-Length. Nada más: ni Date ni Server, que cambiarían o dirían la versión de Python.
    Si el curso quiere enseñarlas, las pone en "cabeceras" con un valor fijo.
  - HEAD: lo mismo que GET (si no hay una ruta HEAD), sin el cuerpo.
  - Una ruta que no existe: 404 con {"error": "No existe la ruta /x"}. Una que existe con otro método: 405 con la
    cabecera Allow y {"error": "La ruta /x no admite POST"}.
  - El cuerpo de la petición (curl -d) se lee y no se usa: las respuestas son fijas.

Uso (lo hace la terminal del kit):
    python3 servidor_http.py servidor.json                  # en primer plano, hasta Ctrl+C
    python3 servidor_http.py servidor.json --fondo          # escucha, se va al fondo y dice su PID
    python3 servidor_http.py servidor.json --comprobar      # solo comprueba el fichero
Termina con 0 si arranca (o el fichero está bien), con 1 si el fichero está mal o el puerto está ocupado y con 2
si los argumentos están mal. Solo la biblioteca de Python.
"""
import errno
import json
import os
import re
import socket
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

NOMBRE = "servidor.json"
PUERTO = 8080
METODOS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
CLAVES = {"puerto", "rutas"}
CLAVES_RUTA = {"metodo", "ruta", "estado", "cabeceras", "cuerpo"}
OBLIGATORIAS = ("metodo", "ruta", "estado")
NOMBRE_CABECERA = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+")


class ServidorMal(ValueError):
    """El servidor.json está mal: `problemas` es una lista de (línea, mensaje)."""

    def __init__(self, problemas):
        super().__init__("\n".join(f"línea {n}: {m}" if n else m for n, m in problemas))
        self.problemas = problemas


def _linea_de_ruta(texto, i):
    """La línea en la que empieza la ruta número i (desde 0): la de su clave «"metodo"» o «"ruta"» número i."""
    for clave in ("metodo", "ruta"):
        apariciones = [m.start() for m in re.finditer(rf'"{clave}"\s*:', texto)]
        if len(apariciones) > i:
            return texto.count("\n", 0, apariciones[i]) + 1
    return 0


def cargar(fichero):
    """Lee y comprueba un servidor.json. Devuelve {"puerto": n, "rutas": [...]} o lanza ServidorMal."""
    try:
        texto = open(fichero, encoding="utf-8").read()
    except UnicodeDecodeError:
        raise ServidorMal([(0, "no está en UTF-8")])
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ServidorMal([(e.lineno, f"no es un JSON válido: {e.msg} (columna {e.colno})")])
    if not isinstance(datos, dict):
        raise ServidorMal([(1, 'tiene que ser un objeto con "rutas" (y, si se quiere, "puerto")')])
    problemas = []
    for clave in sorted(set(datos) - CLAVES):
        problemas.append((0, f'clave desconocida «{clave}» (se admiten "puerto" y "rutas")'))
    puerto = datos.get("puerto", PUERTO)
    if type(puerto) is not int or not 1024 <= puerto <= 65535:
        problemas.append((0, f'"puerto" tiene que ser un número entero entre 1024 y 65535 (es {json.dumps(puerto)})'))
    rutas = datos.get("rutas")
    if not isinstance(rutas, list) or not rutas:
        problemas.append((0, 'falta "rutas": una lista con una o más rutas'))
        raise ServidorMal(problemas)
    vistas = {}
    for i, r in enumerate(rutas):
        n = _linea_de_ruta(texto, i)
        donde = f"ruta {i + 1}"
        if not isinstance(r, dict):
            problemas.append((n, f"{donde}: tiene que ser un objeto"))
            continue
        for clave in sorted(set(r) - CLAVES_RUTA):
            problemas.append((n, f"{donde}: clave desconocida «{clave}» (se admiten {', '.join(sorted(CLAVES_RUTA))})"))
        for clave in OBLIGATORIAS:
            if clave not in r:
                problemas.append((n, f'{donde}: falta "{clave}"'))
        metodo, ruta, estado = r.get("metodo"), r.get("ruta"), r.get("estado")
        if "metodo" in r and metodo not in METODOS:
            problemas.append((n, f'{donde}: "metodo" tiene que ser uno de {", ".join(METODOS)} (es {json.dumps(metodo)})'))
        if "ruta" in r and (not isinstance(ruta, str) or not ruta.startswith("/") or re.search(r"\s|#", ruta)):
            problemas.append((n, f'{donde}: "ruta" tiene que empezar por «/», sin espacios ni «#» (es {json.dumps(ruta)})'))
        if "estado" in r:
            try:
                HTTPStatus(estado)
                if type(estado) is not int:
                    raise ValueError
            except ValueError:
                problemas.append((n, f'{donde}: "estado" tiene que ser un código de estado de HTTP, como 200 o 404 '
                                     f"(es {json.dumps(estado)})"))
        cabeceras = r.get("cabeceras", {})
        if not isinstance(cabeceras, dict):
            problemas.append((n, f'{donde}: "cabeceras" tiene que ser un objeto con nombre y valor'))
        else:
            for nombre, valor in cabeceras.items():
                if not NOMBRE_CABECERA.fullmatch(nombre):
                    problemas.append((n, f"{donde}: nombre de cabecera no válido «{nombre}»"))
                elif nombre.lower() == "content-length":
                    problemas.append((n, f"{donde}: Content-Length lo pone el servidor (quítala de \"cabeceras\")"))
                if not isinstance(valor, str) or re.search(r"[\r\n]", valor):
                    problemas.append((n, f"{donde}: el valor de la cabecera «{nombre}» tiene que ser un texto de una línea"))
        if isinstance(metodo, str) and isinstance(ruta, str):
            if (metodo, ruta) in vistas:
                problemas.append((n, f"{donde}: {metodo} {ruta} repite la ruta {vistas[metodo, ruta]}"))
            vistas.setdefault((metodo, ruta), i + 1)
    if problemas:
        raise ServidorMal(problemas)
    return {"puerto": puerto, "rutas": rutas}


def respuesta(config, metodo, objetivo):
    """(estado, [(cabecera, valor)], cuerpo en bytes) para una petición: la de su ruta, o 404 o 405."""
    partes = urlsplit(objetivo)
    camino = partes.path

    def buscar(m):
        exacta = [r for r in config["rutas"] if r["metodo"] == m and "?" in r["ruta"] and r["ruta"] == objetivo]
        return (exacta or [r for r in config["rutas"] if r["metodo"] == m and r["ruta"] == camino])[:1]

    elegida = buscar(metodo) or (buscar("GET") if metodo == "HEAD" else [])
    if not elegida:
        admitidos = [m for m in METODOS if any(r["metodo"] == m and r["ruta"].split("?")[0] == camino
                                               for r in config["rutas"])]
        if admitidos:
            if "GET" in admitidos and "HEAD" not in admitidos:
                admitidos.append("HEAD")
            return _componer(405, {"Allow": ", ".join(admitidos)},
                             {"error": f"La ruta {camino} no admite {metodo}"})
        return _componer(404, {}, {"error": f"No existe la ruta {camino}"})
    r = elegida[0]
    return _componer(r["estado"], r.get("cabeceras", {}), r["cuerpo"]) if "cuerpo" in r else \
        _componer(r["estado"], r.get("cabeceras", {}))


_SIN_CUERPO = object()


def _componer(estado, cabeceras, cuerpo=_SIN_CUERPO):
    lista = list(cabeceras.items())
    tiene_tipo = any(k.lower() == "content-type" for k, _ in lista)
    if cuerpo is _SIN_CUERPO:
        datos = b""
    elif isinstance(cuerpo, str):
        datos = cuerpo.encode("utf-8")
        if not tiene_tipo:
            lista.insert(0, ("Content-Type", "text/plain; charset=utf-8"))
    else:
        datos = (json.dumps(cuerpo, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if not tiene_tipo:
            lista.insert(0, ("Content-Type", "application/json"))
    lista.append(("Content-Length", str(len(datos))))
    return estado, lista, datos


class Atender(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    config = None

    def _atender(self):
        longitud = int(self.headers.get("Content-Length") or 0)
        if longitud:
            self.rfile.read(longitud)
        estado, cabeceras, cuerpo = respuesta(self.config, self.command, self.path)
        self.send_response_only(estado)          # sin Date ni Server (send_response las añadiría)
        for nombre, valor in cabeceras:
            self.send_header(nombre, valor)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(cuerpo)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _atender

    def log_message(self, *_):                    # nada en pantalla
        pass


class Servidor(ThreadingHTTPServer):
    address_family = socket.AF_INET6
    daemon_threads = True

    def server_bind(self):
        # Una sola escucha para ::1 y 127.0.0.1, como un servidor real en «localhost»
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


def arrancar(fichero):
    """El servidor, ya escuchando (sin atender todavía: serve_forever)."""
    config = cargar(fichero)
    Atender.config = config
    try:
        return Servidor(("::", config["puerto"]), Atender)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            raise ServidorMal([(0, f"el puerto {config['puerto']} ya está en uso (otro programa escucha en él)")])
        raise ServidorMal([(0, f"no se puede escuchar en el puerto {config['puerto']}: {e.strerror}")])


def main(argumentos):
    if not argumentos or "-h" in argumentos or "--help" in argumentos:
        print(__doc__)
        return 0 if argumentos else 2
    opciones = {a for a in argumentos if a.startswith("--")}
    ficheros = [a for a in argumentos if not a.startswith("--")]
    if len(ficheros) != 1 or opciones - {"--fondo", "--comprobar"}:
        print("Uso: servidor_http.py servidor.json [--fondo | --comprobar] (más en --help)", file=sys.stderr)
        return 2
    try:
        if "--comprobar" in opciones:
            cargar(ficheros[0])
            return 0
        servidor = arrancar(ficheros[0])
    except (ServidorMal, OSError) as e:
        for linea, mensaje in getattr(e, "problemas", [(0, str(e))]):
            print(f"{ficheros[0]}:{linea}: {mensaje}" if linea else f"{ficheros[0]}: {mensaje}", file=sys.stderr)
        return 1
    if "--fondo" in opciones:
        # Ya escucha: el hijo atiende y el padre dice su PID y termina (quien lo arranca sabe que está listo)
        pid = os.fork()
        if pid:
            print(pid, flush=True)
            return 0
        os.setsid()
        nulo = os.open(os.devnull, os.O_RDWR)
        for fd in (0, 1, 2):
            os.dup2(nulo, fd)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
