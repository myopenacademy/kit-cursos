"""Pruebas de nucleo/comprobar_mermaid.py. Necesitan Node.js (npx) y Chrome: si no están, se saltan.
La primera vez, npx descarga mermaid-cli (tarda un poco).

Desde la raíz del kit:
    python3 -m unittest discover -s herramientas/pruebas -v
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
SCRIPT = PRUEBAS.parent / "nucleo" / "comprobar_mermaid.py"
BUENO = PRUEBAS / "cursos" / "bueno"
HAY_CHROME = bool(os.environ.get("CHROME_PATH")) or any(
    shutil.which(n) for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"))


@unittest.skipUnless(shutil.which("npx") and HAY_CHROME, "hace falta Node.js (npx) y Chrome")
class ComprobarMermaid(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mermaid-pruebas-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ejecutar(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd, timeout=900)

    def escribir(self, rel, diagrama):
        ruta = self.tmp / rel
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(f"# Prueba\n\nTexto.\n\n```mermaid\n{diagrama}\n```\n", encoding="utf-8")
        return ruta

    def test_el_curso_bueno_se_dibuja(self):
        r = self.ejecutar(cwd=BUENO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("1 diagramas en 1 ficheros", r.stdout)

    def test_un_diagrama_mal_escrito_dice_fichero_linea_y_version(self):
        self.escribir("malo.md", "flowchart LR\n    A -->")
        r = self.ejecutar("malo.md", cwd=self.tmp)
        self.assertEqual(r.returncode, 1)
        self.assertIn("malo.md:5: Mermaid 12.2.0", r.stdout)
        self.assertIn("malo.md:5: Mermaid 10.9.8", r.stdout)
        self.assertIn("Parse error", r.stdout)

    def test_se_ignora_verificacion_dentro_del_curso(self):
        self.escribir(".verificacion/malo.md", "flowchart LR\n    A -->")
        r = self.ejecutar(cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("0 diagramas en 0 ficheros", r.stdout)

    def test_se_revisan_los_md_de_codigo(self):
        self.escribir("fase-01/codigo/01-x/ejemplos/2.1-a/README.md", "flowchart LR\n    A -->")
        r = self.ejecutar(cwd=self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("2.1-a/README.md:5: Mermaid 12.2.0", r.stdout)

    def test_se_salta_lo_que_esta_mal_a_proposito(self):
        # Un README roto en una carpeta con debe-fallar.txt, y el módulo que lo muestra en un bloque
        roto = self.escribir("fase-01/codigo/01-x/ejemplos/2.1-roto/README.md", "flowchart LR\n    A -->")
        (roto.parent / "debe-fallar.txt").write_text("El diagrama está mal a propósito.\n", encoding="utf-8")
        (self.tmp / "fase-01" / "01-x.md").write_text(
            "# 01.01 X\n\n````markdown\n# Roto\n\n```mermaid\nflowchart LR\n    A -->\n```\n````\n\n"
            "📁 **Código:** [`codigo/01-x/ejemplos/2.1-roto/`](codigo/01-x/ejemplos/2.1-roto/)\n\n"
            "```mermaid\nflowchart LR\n    A --> B\n```\n", encoding="utf-8")
        r = self.ejecutar(cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("1 diagramas en 1 ficheros", r.stdout)

    def test_argumentos_mal(self):
        self.assertEqual(self.ejecutar("no-existe.md", cwd=self.tmp).returncode, 2)
        self.assertEqual(self.ejecutar("--rapido", cwd=self.tmp).returncode, 2)


if __name__ == "__main__":
    unittest.main()
