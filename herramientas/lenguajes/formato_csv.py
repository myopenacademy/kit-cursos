"""El comprobador de los ficheros CSV (para verificar_codigo.py; no se ejecuta a mano).

Lee el fichero con el separador del separador.txt de su carpeta (`;`, `|` o la palabra `tabulador`; si no hay,
la coma) y comprueba que todas las filas tienen las mismas columnas que la primera (la cabecera) y que no queda
ninguna comilla sin cerrar. Con la biblioteca de Python.
"""
import csv

EXTENSIONES = {".csv"}
NOMBRES = {"tabulador": "\t", "coma": ",", "punto y coma": ";"}


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def separador(carpeta):
    fichero = carpeta / "separador.txt" if carpeta else None
    if not fichero or not fichero.is_file():
        return ","
    texto = fichero.read_text(encoding="utf-8").strip()
    return NOMBRES.get(texto.lower(), texto)


def filas(fichero, carpeta):
    with fichero.open(encoding="utf-8", newline="") as f:
        return list(csv.reader(f, delimiter=separador(carpeta), strict=True))


def errores(fichero, carpeta=None):
    sep = separador(carpeta)
    if len(sep) != 1:
        return [(0, f"el separador.txt de su carpeta debe ser un solo carácter o «tabulador» (es «{sep}»)")]
    try:
        with fichero.open(encoding="utf-8", newline="") as f:
            lector = csv.reader(f, delimiter=sep, strict=True)
            cabecera, problemas = None, []
            for fila in lector:
                if not fila:
                    continue
                if cabecera is None:
                    cabecera = len(fila)
                elif len(fila) != cabecera:
                    problemas.append((lector.line_num, f"CSV: la fila tiene {len(fila)} columnas y la cabecera {cabecera} "
                                                       f"(separador «{'tabulador' if sep == chr(9) else sep}»)"))
            if cabecera is None:
                return [(0, "CSV vacío")]
            return problemas
    except csv.Error as e:
        return [(getattr(lector, "line_num", 0), f"CSV mal escrito: {e}")]
    except UnicodeDecodeError:
        return [(0, "no está en UTF-8")]
