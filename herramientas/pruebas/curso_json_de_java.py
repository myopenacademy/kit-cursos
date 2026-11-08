#!/usr/bin/env python3
"""Genera un curso.json provisional para una copia del curso de Java original, que no lo tiene.

Sirve para dos cosas:
  - Probar formato_academia.py con mucho contenido real (199 módulos) y encontrar falsos positivos.
  - Ser el punto de partida del curso.json de curso-java/ cuando se adapte (PLAN.md del kit).

Lee de la carpeta del curso: los títulos de cada módulo («# NN.NN Título»), sus ejercicios
(«#### Ejercicio N · Título»), los títulos de las fases de 00-indice.md («## Fase NN — Título») y las
etapas de proyecto/. Los identificadores salen del nombre del fichero sin número (módulos y fases) y
del título (ejercicios), como propone FORMATO.md (apartado 3.3); a los ejercicios les añade su número
para que no se repitan. Es PROVISIONAL: al adaptar el curso hay que revisar a mano los títulos de las
etapas y los identificadores, que después ya no cambian.

Nunca se ejecuta sobre el curso original (que solo se lee): primero se saca una copia con Git, fuera
del kit, y se trabaja sobre ella:
    mkdir -p /tmp/java/curso-java
    git -C "../../../Curso Java Completo" archive HEAD | tar -x -C /tmp/java/curso-java
    python3 herramientas/pruebas/curso_json_de_java.py /tmp/java/curso-java
    python3 herramientas/formato_academia.py /tmp/java/curso-java

Escribe curso.json en la carpeta de la copia (si ya existe, no hace nada salvo con --sobrescribir).
"""
import json
import re
import sys
import unicodedata
from pathlib import Path


def nombre(texto):
    texto = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def generar(raiz):
    indice = (raiz / "00-indice.md").read_text(encoding="utf-8")
    fases = []
    for carpeta in sorted(p for p in raiz.glob("fase-*") if p.is_dir()):
        modulos = []
        for md in sorted(carpeta.glob("[0-9][0-9]-*.md")):
            texto = md.read_text(encoding="utf-8")
            titulo = re.search(r"^# \d{2}\.\d{2} (.+?)\s*$", texto, re.M)
            ident = "java." + md.stem[3:]
            ejercicios = [{"id": f"{ident}.{nombre(t)}-{n}", "titulo": t}
                          for n, t in re.findall(r"^#### Ejercicio (\d+) · (.+?)\s*$", texto, re.M)]
            modulos.append({"id": ident, "fichero": md.relative_to(raiz).as_posix(),
                            "titulo": titulo.group(1) if titulo else md.stem, "ejercicios": ejercicios})
        numero = carpeta.name[5:7]
        titulo = re.search(rf"^## Fase {numero} — (.+?)\s*$", indice, re.M)
        fases.append({"id": "java.fase." + carpeta.name[8:], "carpeta": carpeta.name,
                      "titulo": titulo.group(1) if titulo else carpeta.name, "modulos": modulos})
    etapas = []
    for md in sorted((raiz / "proyecto").glob("[0-9][0-9]-*.md")):
        titulo = re.search(r"^# (.+?)\s*$", md.read_text(encoding="utf-8"), re.M)
        etapas.append({"id": "java.etapa." + md.stem[3:], "fichero": md.relative_to(raiz).as_posix(),
                       "titulo": titulo.group(1) if titulo else md.stem})
    return {
        "formato": 1, "tipo": "curso", "id": "java", "titulo": "Java de 0 a experto",
        "descripcion": "De no saber programar a trabajar con Java y Spring Boot.",
        "version": "2.0.0", "idioma": "es", "repositorio": "https://github.com/myopenacademy/curso-java",
        "conviene_saber_antes": ["inicial"], "fases": fases,
        "proyecto": {"tipo": "etapas", "titulo": "Mi Biblioteca", "etapas": etapas},
        "equivalencias": [], "transicion": ["preguntas-de-repaso"],
    }


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__.strip())
        sys.exit(0 if args else 2)
    sobrescribir = "--sobrescribir" in args
    rutas = [a for a in args if not a.startswith("-")]
    raiz = Path(rutas[0]) if rutas else None
    if not raiz or not (raiz / "00-indice.md").is_file():
        print(f"No encuentro un curso de Java en {raiz} (falta 00-indice.md).", file=sys.stderr)
        sys.exit(2)
    destino = raiz / "curso.json"
    if destino.exists() and not sobrescribir:
        print(f"{destino} ya existe: no lo toco (usa --sobrescribir).", file=sys.stderr)
        sys.exit(1)
    datos = generar(raiz)
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    modulos = sum(len(f["modulos"]) for f in datos["fases"])
    print(f"✅ {destino}: {len(datos['fases'])} fases, {modulos} módulos y {len(datos['proyecto']['etapas'])} etapas.")


if __name__ == "__main__":
    main()
