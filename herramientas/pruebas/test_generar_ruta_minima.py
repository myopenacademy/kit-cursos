"""Pruebas de nucleo/generar_ruta_minima.py, sobre una copia del curso de ejemplo bueno (cursos/bueno/).

La copia se amplía en una carpeta temporal (el curso bueno no se toca: la academia lo usa tal cual): un
tercer módulo en la fase 1 (01.03, fuera de la ruta y enlazado desde «Conviene saber antes» del 01.01) y
una segunda fase entera fuera de la ruta. La ruta mínima tiene el 01.01, el 01.02 (todavía pendiente) y la
única etapa del proyecto.

Desde la raíz del kit:
    python3 -m unittest discover -s herramientas/pruebas -v
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
HERRAMIENTAS = PRUEBAS.parent
sys.path.insert(0, str(HERRAMIENTAS))
sys.path.insert(0, str(HERRAMIENTAS / "nucleo"))
import formato_academia  # noqa: E402
import generar_ruta_minima  # noqa: E402

BUENO = PRUEBAS / "cursos" / "bueno"
SCRIPT = HERRAMIENTAS / "nucleo" / "generar_ruta_minima.py"
MODULO_01 = "fase-01-primeros-pasos/01-ficheros-json.md"

RUTA = {"modulos": ["ejemplo.ficheros-json", "ejemplo.ficheros-yaml"], "etapas": ["ejemplo.etapa.primer-catalogo"]}

RESUMEN = ("> **2 módulos · ~2 h** (el curso entero: 4 módulos, ~7 h) · **Proyecto:** etapa 1\n"
           "> **Disponibles:** 1 de los 2 módulos de la ruta (los demás aparecen como «Pendiente»)")
MODULOS = """### Fase 01 — Primeros pasos

| # | Módulo | Tiempo |
|---|---|---|
| 01.01 | [Ficheros JSON](fase-01-primeros-pasos/01-ficheros-json.md) | 2 h |
| 01.02 | Ficheros YAML | — |

**~2 h** · Fuera de la ruta: 01.03

### Fase 02 — Más formatos

**Fuera de la ruta** (1 módulo, ~2 h): para después."""
PROYECTO = """| Etapa | Qué se construye |
|---|---|
| ◆ 1 | [El primer catálogo](proyecto/01-primer-catalogo.md) |"""
CONSULTAS = """| Módulo | Lo piden |
|---|---|
| 01.03 [Ficheros XML](fase-01-primeros-pasos/03-ficheros-xml.md) | 01.01 |"""


def cabecera(numero, titulo, horas):
    return (f"# {numero} {titulo}\n\n> **Conviene saber antes:** Nada\n> **Tiempo estimado:** {horas} horas\n"
            "> **Nivel:** Básico · Ampliación\n\n## Qué aprenderás\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="generar-ruta-minima-"))
        self.raiz = self.tmp / "curso-ejemplo"
        shutil.copytree(BUENO, self.raiz)
        (self.raiz / "fase-01-primeros-pasos/03-ficheros-xml.md").write_text(
            cabecera("01.03", "Ficheros XML", 3), encoding="utf-8")
        (self.raiz / "fase-02-mas-formatos").mkdir()
        (self.raiz / "fase-02-mas-formatos/01-ficheros-csv.md").write_text(
            cabecera("02.01", "Ficheros CSV", 2), encoding="utf-8")
        self.cambiar_modulo_01("> **Conviene saber antes:** ",
                               "> **Conviene saber antes:** [01.03 Ficheros XML, 1.1](03-ficheros-xml.md#11-qué-es) · ")

        def ampliar(d):
            d["fases"][0]["modulos"].append({"id": "ejemplo.ficheros-xml", "fichero": "fase-01-primeros-pasos/03-ficheros-xml.md",
                                             "titulo": "Ficheros XML", "ejercicios": []})
            d["fases"].append({"id": "ejemplo.fase.mas-formatos", "carpeta": "fase-02-mas-formatos", "titulo": "Más formatos",
                               "modulos": [{"id": "ejemplo.ficheros-csv", "fichero": "fase-02-mas-formatos/01-ficheros-csv.md",
                                            "titulo": "Ficheros CSV", "ejercicios": []}]})
            d["partes"][0]["fases"].append("ejemplo.fase.mas-formatos")
            d["ruta_minima"] = json.loads(json.dumps(RUTA))
        self.cambiar_json(ampliar)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ejecutar(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd)

    def cambiar_json(self, cambio):
        d = json.loads((self.raiz / "curso.json").read_text(encoding="utf-8"))
        cambio(d)
        (self.raiz / "curso.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    def cambiar_modulo_01(self, antes, despues):
        f = self.raiz / MODULO_01
        texto = f.read_text(encoding="utf-8")
        self.assertIn(antes, texto)
        f.write_text(texto.replace(antes, despues, 1), encoding="utf-8")

    def plantilla(self, texto, nombre="RUTA-MINIMA.plantilla.md"):
        (self.raiz / nombre).write_text(texto, encoding="utf-8")
        self.cambiar_json(lambda d: d["ruta_minima"].update(plantilla=nombre))

    def ruta(self):
        return (self.raiz / "RUTA-MINIMA.md").read_text(encoding="utf-8")


class ConPlantilla(Base):
    def test_cada_hueco_se_rellena(self):
        self.plantilla("# Mi ruta\n\n{{resumen}}\n\n## Los módulos\n\n{{modulos}}\n\n## El proyecto\n\n{{proyecto}}\n\n"
                       "## Consultas puntuales\n\n{{consultas}}\n\n---\n📚 [Índice](00-indice.md)\n")
        r = self.ejecutar(str(self.raiz))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.ruta(), f"# Mi ruta\n\n{RESUMEN}\n\n## Los módulos\n\n{MODULOS}\n\n## El proyecto\n\n{PROYECTO}\n\n"
                                      f"## Consultas puntuales\n\n{CONSULTAS}\n\n---\n📚 [Índice](00-indice.md)\n")
        self.assertIn("✅ Generado", r.stdout)
        self.assertIn("2 módulos", r.stdout)

    def test_solo_el_hueco_obligatorio(self):
        self.plantilla("# Ruta\n\nTexto del curso.\n\n{{modulos}}\n")
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertEqual(texto, f"# Ruta\n\nTexto del curso.\n\n{MODULOS}\n")

    def test_un_hueco_que_no_existe_es_un_error(self):
        self.plantilla("{{modulos}}\n\n{{indice}}\n")
        r = self.ejecutar(str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("{{indice}}", r.stderr)
        self.assertFalse((self.raiz / "RUTA-MINIMA.md").exists())

    def test_sin_el_hueco_modulos_es_un_error(self):
        self.plantilla("{{resumen}}\n")
        r = self.ejecutar(str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("{{modulos}}", r.stderr)
        self.assertFalse((self.raiz / "RUTA-MINIMA.md").exists())

    def test_usa_los_huecos_de_formato_academia(self):
        self.assertIs(generar_ruta_minima.HUECOS_RUTA_MINIMA, formato_academia.HUECOS_RUTA_MINIMA)


class SinPlantilla(Base):
    def test_texto_generico_con_las_cuatro_partes(self):
        r = self.ejecutar(str(self.raiz))
        self.assertEqual(r.returncode, 0, r.stderr)
        texto = self.ruta()
        self.assertTrue(texto.startswith("# 🧭 Ruta mínima — Curso de ejemplo\n\n" + RESUMEN + "\n\n"), texto)
        for parte in (MODULOS, PROYECTO, CONSULTAS, "## Los módulos", "## El proyecto", "## Consultas puntuales",
                      "📚 [Índice](00-indice.md)"):
            self.assertIn(parte, texto)
        self.assertNotIn("{{", texto)
        self.assertTrue(texto.endswith("➡️ [Primer módulo](fase-01-primeros-pasos/01-ficheros-json.md)\n"), texto)

    def test_desde_la_raiz_del_curso_sin_argumentos(self):
        r = self.ejecutar(cwd=self.raiz)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(MODULOS, self.ruta())

    def test_el_fichero_generado_cumple_el_formato(self):
        self.ejecutar(str(self.raiz))
        informe, _ = formato_academia.comprobar(self.raiz)
        self.assertEqual([e for e in informe.errores if "RUTA-MINIMA" in e[0] or "RUTA-MINIMA" in e[2]], [])
        self.assertEqual([a for a in informe.avisos if "RUTA-MINIMA" in a[0] or "RUTA-MINIMA" in a[2]], [])


class Contenido(Base):
    def test_modulo_pendiente_sin_enlace_ni_horas(self):
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertIn("| 01.02 | Ficheros YAML | — |", texto)
        self.assertNotIn("02-ficheros-yaml.md", texto)

    def test_sin_pendientes_no_hay_linea_de_disponibles(self):
        self.cambiar_json(lambda d: d["ruta_minima"].update(modulos=["ejemplo.ficheros-json"]))
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertIn("> **1 módulo · ~2 h** (el curso entero: 4 módulos, ~7 h) · **Proyecto:** etapa 1\n\n", texto)
        self.assertNotIn("**Disponibles:**", texto)

    def test_resumen_sin_etapas(self):
        self.cambiar_json(lambda d: d["ruta_minima"].pop("etapas"))
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertIn("> **2 módulos · ~2 h** (el curso entero: 4 módulos, ~7 h)\n", texto)
        self.assertIn("Ninguna etapa del proyecto entra en la ruta mínima.", texto)
        self.assertNotIn("| ◆ 1 |", texto)

    def test_resumen_con_varias_etapas(self):
        def tres_etapas(d):
            for i in (2, 3):
                d["proyecto"]["etapas"].append({"id": f"ejemplo.etapa.e{i}", "fichero": f"proyecto/0{i}-e{i}.md", "titulo": f"Etapa {i}"})
            d["ruta_minima"]["etapas"] = ["ejemplo.etapa.primer-catalogo", "ejemplo.etapa.e2", "ejemplo.etapa.e3"]
        self.cambiar_json(tres_etapas)
        (self.raiz / "proyecto/02-e2.md").write_text("# Etapa 2\n", encoding="utf-8")
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertIn("· **Proyecto:** etapas 1, 2 y 3\n", texto)
        self.assertIn("| ◆ 2 | [Etapa 2](proyecto/02-e2.md) |\n| ◆ 3 | Etapa 3 |", texto)

    def test_consultas_desde_requisitos_previos(self):
        self.cambiar_modulo_01("> **Conviene saber antes:**", "> **Requisitos previos:**")
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertIn(CONSULTAS, texto)

    def test_sin_consultas(self):
        self.cambiar_json(lambda d: d["ruta_minima"].update(
            modulos=["ejemplo.ficheros-json", "ejemplo.ficheros-yaml", "ejemplo.ficheros-xml"]))
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertIn("Ninguna: los módulos de la ruta no piden ninguno que esté fuera de ella.", texto)
        self.assertNotIn("| Módulo | Lo piden |", texto)
        self.assertIn("**~5 h**\n", texto)

    def test_los_enlaces_externos_no_son_consultas(self):
        texto, _ = generar_ruta_minima.generar(self.raiz)
        self.assertNotIn("ejemplo-destino", texto)


class Comprobar(Base):
    def test_al_dia(self):
        self.assertEqual(self.ejecutar(str(self.raiz)).returncode, 0)
        r = self.ejecutar("--comprobar", str(self.raiz))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("está al día", r.stdout)

    def test_desfasado(self):
        self.ejecutar(str(self.raiz))
        self.cambiar_json(lambda d: d["fases"][0].update(titulo="Los primeros pasos"))
        r = self.ejecutar("--comprobar", str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no está al día", r.stdout)
        self.assertNotIn("Los primeros pasos", self.ruta())

    def test_falta(self):
        r = self.ejecutar("--comprobar", str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("Falta", r.stdout)
        self.assertFalse((self.raiz / "RUTA-MINIMA.md").exists())


class Errores(Base):
    def test_sin_ruta_minima(self):
        self.cambiar_json(lambda d: d.pop("ruta_minima"))
        for args in ((str(self.raiz),), ("--comprobar", str(self.raiz))):
            r = self.ejecutar(*args)
            self.assertEqual(r.returncode, 1)
            self.assertIn("no tiene «ruta_minima»", r.stderr)
            self.assertFalse((self.raiz / "RUTA-MINIMA.md").exists())

    def test_modulo_que_no_existe(self):
        self.cambiar_json(lambda d: d["ruta_minima"]["modulos"].append("ejemplo.no-existe"))
        r = self.ejecutar(str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("ejemplo.no-existe", r.stderr)
        self.assertIn("formato_academia.py", r.stderr)

    def test_sin_curso_json(self):
        (self.raiz / "curso.json").unlink()
        r = self.ejecutar(str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("No se puede generar", r.stderr)

    def test_argumentos_mal(self):
        self.assertEqual(self.ejecutar("--rapido").returncode, 2)
        self.assertEqual(self.ejecutar("/no/existe").returncode, 2)
        r = self.ejecutar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("RUTA-MINIMA.md", r.stdout)


if __name__ == "__main__":
    unittest.main()
