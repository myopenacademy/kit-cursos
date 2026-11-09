"""El comprobador de los ficheros INI (para verificar_codigo.py; no se ejecuta a mano).

INI no tiene una norma: cada programa lo lee a su manera. Se comprueba lo que aceptan casi todos, con
configparser de la biblioteca de Python: cada clave dentro de una sección ([nombre]), con «=» o «:», sin
secciones ni claves repetidas (en la misma sección) y con comentarios que empiezan por «;» o «#». Los «%» se
dejan tal cual (sin la interpolación propia de configparser).
"""
import configparser

EXTENSIONES = {".ini"}


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def errores(fichero, carpeta=None):
    """[(línea, qué)] si no es válido; [] si lo es."""
    lector = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        lector.read_string(fichero.read_text(encoding="utf-8"), source=fichero.name)
    except configparser.MissingSectionHeaderError as e:
        return [(e.lineno, f"INI: la clave «{e.line.strip()}» está antes de la primera sección ([nombre])")]
    except configparser.DuplicateSectionError as e:
        return [(e.lineno or 0, f"INI: la sección [{e.section}] está repetida")]
    except configparser.DuplicateOptionError as e:
        return [(e.lineno or 0, f"INI: la clave «{e.option}» está repetida en la sección [{e.section}]")]
    except configparser.ParsingError as e:
        return [(linea, f"INI: la línea no es ni una sección, ni una clave con «=», ni un comentario: «{texto.strip()}»")
                for linea, texto in e.errors]
    except UnicodeDecodeError:
        return [(0, "no está en UTF-8")]
    return []
