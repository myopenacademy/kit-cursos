"""El comprobador de los ficheros YAML (para verificar_codigo.py; no se ejecuta a mano).

Que el fichero sea YAML válido (todos sus documentos), con PyYAML (`python3-yaml` en Ubuntu, `pip install
pyyaml`): la única librería que necesita el kit fuera de la de Python, y solo aquí (decisión del autor). Si no
está, verificar_codigo.py avisa de que no ha podido comprobar los YAML.
"""
EXTENSIONES = {".yaml", ".yml"}

try:
    import yaml
except ImportError:          # pragma: no cover - depende de la máquina
    yaml = None


class SinPyYAML(RuntimeError):
    pass


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def cargar(fichero, carpeta=None):
    if yaml is None:
        raise SinPyYAML("falta PyYAML para comprobar los YAML (en Ubuntu, python3-yaml; con pip, pyyaml)")
    documentos = list(yaml.safe_load_all(fichero.read_text(encoding="utf-8")))
    return documentos[0] if len(documentos) == 1 else documentos


def errores(fichero, carpeta=None):
    try:
        cargar(fichero)
    except SinPyYAML:
        raise
    except yaml.YAMLError as e:
        marca = getattr(e, "problem_mark", None)
        problema = getattr(e, "problem", None) or str(e).split("\n")[0]
        return [((marca.line + 1) if marca else 0, f"YAML no válido: {problema}"
                 + (f" (columna {marca.column + 1})" if marca else ""))]
    except UnicodeDecodeError:
        return [(0, "no está en UTF-8")]
    return []
