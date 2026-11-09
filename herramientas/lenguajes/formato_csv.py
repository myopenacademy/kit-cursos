"""El comprobador de los ficheros CSV y TSV (para verificar_codigo.py; no se ejecuta a mano).

Lee el fichero con el separador del separador.txt de su carpeta (`;`, `|` o la palabra `tabulador`; si no hay,
la coma; un .tsv, siempre con tabulador) y comprueba que todas las filas tienen las mismas columnas que la
primera (la cabecera) y que no queda ninguna comilla sin cerrar. Con la biblioteca de Python.

La codificación: UTF-8, salvo que la carpeta tenga un codificacion.txt con el nombre que entiende iconv
(`WINDOWS-1252`, `ISO-8859-15`…): entonces el fichero se convierte desde esa codificación y se comprueba como
cualquier otro. Si con codificacion.txt el fichero resulta ser UTF-8 (y no solo ASCII), es un error: lo más
probable es que se convirtiera y se olvidara quitar el codificacion.txt.

Además, comparar(): un .csv (o .tsv) y un .json con el mismo nombre en la misma carpeta tienen que tener los
mismos datos, con las reglas que pidió el curso inicial para su reto 3 de la fase 4 (FORMATO.md, apartado 7.1).
"""
import codecs
import csv
import io
import json
import re
from decimal import Decimal

EXTENSIONES = {".csv", ".tsv"}
NOMBRES = {"tabulador": "\t", "coma": ",", "punto y coma": ";"}
NUMERO = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?")
BOOLEANOS = {"sí": True, "true": True, "no": False, "false": False}


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def separador(carpeta, fichero=None):
    if fichero is not None and fichero.suffix.lower() == ".tsv":
        return "\t"
    ruta = carpeta / "separador.txt" if carpeta else None
    if not ruta or not ruta.is_file():
        return ","
    texto = ruta.read_text(encoding="utf-8").strip()
    return NOMBRES.get(texto.lower(), texto)


def nombre_del_separador(sep):
    return "tabulador" if sep == "\t" else sep


class MalLeido(ValueError):
    """El fichero no se puede leer: (línea, qué)."""

    def __init__(self, linea, mensaje):
        super().__init__(mensaje)
        self.linea, self.mensaje = linea, mensaje


def codificacion(carpeta):
    """El nombre del codificacion.txt de la carpeta (como lo escribe iconv), o None si no hay."""
    ruta = carpeta / "codificacion.txt" if carpeta else None
    if not ruta or not ruta.is_file():
        return None
    return ruta.read_text(encoding="utf-8").strip()


def texto(fichero, carpeta):
    """El contenido del fichero ya convertido a texto, según su codificación."""
    datos = fichero.read_bytes()
    nombre = codificacion(carpeta)
    if nombre is None:
        if datos.startswith(codecs.BOM_UTF8):
            raise MalLeido(1, "empieza por un BOM (los bytes EF BB BF de «UTF-8 con BOM»): guárdalo en UTF-8 sin BOM")
        try:
            return datos.decode("utf-8")
        except UnicodeDecodeError:
            raise MalLeido(_linea_del_byte(datos, 0), "no está en UTF-8 (si está en otra codificación a propósito, "
                                                      "dila en un codificacion.txt en su carpeta, como WINDOWS-1252)")
    try:
        python = codecs.lookup(nombre).name
    except LookupError:
        raise MalLeido(0, f"el codificacion.txt de su carpeta dice «{nombre}», que no es una codificación conocida "
                          "(escríbela como la llama iconv: WINDOWS-1252, ISO-8859-15…)")
    if python not in ("utf-8", "utf-8-sig") and not datos.isascii():
        try:
            datos.decode("utf-8")
            raise MalLeido(0, f"el codificacion.txt de su carpeta dice «{nombre}», pero el fichero está en UTF-8 "
                              "(¿ya lo has convertido? entonces sobra el codificacion.txt)")
        except UnicodeDecodeError:
            pass
    if python == "utf-8" and datos.startswith(codecs.BOM_UTF8):
        raise MalLeido(1, "empieza por un BOM (los bytes EF BB BF de «UTF-8 con BOM»): guárdalo en UTF-8 sin BOM")
    try:
        return datos.decode(python)
    except UnicodeDecodeError as e:
        raise MalLeido(_linea_del_byte(datos, e.start), f"no se puede leer como {nombre} (codificacion.txt)")


def _linea_del_byte(datos, inicio):
    """La línea del primer byte que no se puede leer (desde inicio, o el primero que no es UTF-8)."""
    try:
        datos.decode("utf-8")
    except UnicodeDecodeError as e:
        inicio = max(inicio, e.start)
    return datos.count(b"\n", 0, inicio) + 1


def leer(fichero, carpeta):
    """[(línea donde empieza la fila, campos)], sin las líneas vacías. Lanza MalLeido."""
    sep = separador(carpeta, fichero)
    if len(sep) != 1:
        raise MalLeido(0, f"el separador.txt de su carpeta debe ser un solo carácter o «tabulador» (es «{sep}»)")
    lector = csv.reader(io.StringIO(texto(fichero, carpeta), newline=""), delimiter=sep, strict=True)
    filas, inicio = [], 1
    try:
        for fila in lector:
            if fila:
                filas.append((inicio, fila))
            inicio = lector.line_num + 1
    except csv.Error as e:
        raise MalLeido(lector.line_num, f"CSV mal escrito: {e}")
    return filas


def filas(fichero, carpeta):
    return [f for _, f in leer(fichero, carpeta)]


def errores(fichero, carpeta=None):
    """[(línea, qué)] si no es válido; [] si lo es."""
    try:
        leidas = leer(fichero, carpeta)
    except MalLeido as e:
        return [(e.linea, e.mensaje)]
    if not leidas:
        return [(0, "CSV vacío")]
    sep = nombre_del_separador(separador(carpeta, fichero))
    cabecera = len(leidas[0][1])
    return [(linea, f"CSV: la fila tiene {len(fila)} columnas y la cabecera {cabecera} (separador «{sep}»)")
            for linea, fila in leidas[1:] if len(fila) != cabecera]


# -- la comparación con su JSON ----------------------------------------------------------------------------

def _tipo(valor):
    if valor is None:
        return "null"
    if isinstance(valor, bool):
        return "un booleano"
    if isinstance(valor, Decimal):
        return "un número"
    if isinstance(valor, list):
        return "una lista"
    if isinstance(valor, dict):
        return "un objeto"
    return "un texto"


def _valor(campo, valor):
    """None si el campo del CSV vale lo mismo que el valor del JSON; si no, qué pasa."""
    if valor is None:
        return None if campo == "" else f"en el JSON es null, que en el CSV es el campo vacío, y el campo es «{campo}»"
    if isinstance(valor, bool):
        if campo not in BOOLEANOS:
            return (f"en el JSON es el booleano {str(valor).lower()} y en el CSV «{campo}»: un booleano se escribe "
                    "sí, no, true o false (exactamente así, en minúscula)")
        if BOOLEANOS[campo] != valor:
            return f"en el JSON es {str(valor).lower()} y en el CSV «{campo}», que es {str(not valor).lower()}"
        return None
    if isinstance(valor, Decimal):
        if campo == "":
            return f"en el JSON es el número {valor} y en el CSV el campo está vacío (un vacío solo vale como null)"
        if not NUMERO.fullmatch(campo):
            return (f"en el JSON es el número {valor} y en el CSV «{campo}», que no se lee como número (sin ceros "
                    "a la izquierda, con punto decimal y sin separador de miles: si es un código, en el JSON va "
                    "como texto, entre comillas)")
        if Decimal(campo) != valor:
            return f"en el JSON es el número {valor} y en el CSV {campo}"
        return None
    if isinstance(valor, str):
        if valor == "":
            return ("en el JSON es el texto vacío \"\", y un campo vacío del CSV solo vale como null"
                    if campo == "" else f"en el JSON es el texto vacío \"\" y en el CSV «{campo}»")
        if valor == campo:
            return None
        if campo == "":
            return f"en el JSON es el texto «{valor}» y en el CSV el campo está vacío (un vacío solo vale como null)"
        return f"en el JSON es el texto «{valor}» y en el CSV «{campo}»"
    return f"en el JSON es {_tipo(valor)}, y un CSV solo tiene textos, números, booleanos y vacíos"


def comparar(fichero, carpeta, json_fichero):
    """[(línea del CSV, qué)]: lo que no coincide entre el CSV y el JSON con el mismo nombre (los dos válidos)."""
    nombre = json_fichero.name
    try:
        leidas = leer(fichero, carpeta)
    except MalLeido as e:
        return [(e.linea, e.mensaje)]
    datos = json.loads(json_fichero.read_text(encoding="utf-8"), parse_float=Decimal, parse_int=Decimal)
    if not isinstance(datos, list):
        return [(0, f"{nombre} debe ser una lista ([…]) con un objeto por fila de datos del CSV, y es {_tipo(datos)}")]
    if not leidas:
        return []
    (linea_cabecera, cabecera), filas_de_datos = leidas[0], leidas[1:]
    problemas = []
    repetidas = sorted({c for c in cabecera if cabecera.count(c) > 1})
    if repetidas:
        return [(linea_cabecera, "la cabecera repite " + ", ".join(f"«{c}»" for c in repetidas)
                 + f": así no se puede comparar con {nombre} (cada clave de un objeto JSON es única)")]
    for n, ((linea, fila), objeto) in enumerate(zip(filas_de_datos, datos), 1):
        donde = f"fila {n} de datos (comparada con el objeto {n} de {nombre})"
        if not isinstance(objeto, dict):
            problemas.append((linea, f"{donde}: en el JSON no es un objeto ({{…}}), sino {_tipo(objeto)}"))
            continue
        faltan = [c for c in cabecera if c not in objeto]
        sobran = [c for c in objeto if c not in cabecera]
        if faltan:
            problemas.append((linea, f"{donde}: al objeto le falta " + ", ".join(f"«{c}»" for c in faltan)
                              + " (debe tener exactamente las claves de la cabecera)"))
        if sobran:
            problemas.append((linea, f"{donde}: al objeto le sobra " + ", ".join(f"«{c}»" for c in sobran)
                              + " (no está en la cabecera del CSV)"))
        for clave, campo in zip(cabecera, fila):
            if clave in objeto:
                diferencia = _valor(campo, objeto[clave])
                if diferencia:
                    problemas.append((linea, f"{donde}, clave «{clave}»: {diferencia}"))
    if len(filas_de_datos) != len(datos):
        ultima = leidas[-1][0]
        problemas.append((ultima, f"el CSV tiene {len(filas_de_datos)} filas de datos y {nombre}, {len(datos)} "
                                  "objetos (uno por fila, en el mismo orden)"))
    return problemas
