"""Revisión común de los argumentos de las herramientas del núcleo (no se ejecuta a mano).

Sale de herramientas/argumentos.py del curso de Java, con un cambio: las herramientas viven en el kit
y se ejecutan desde la raíz del curso, así que las rutas relativas se buscan desde la carpeta actual.

Todas las herramientas la usan para que un error al escribir la orden no pase desapercibido:
  - `-h` o `--help` muestra la ayuda de la herramienta (su texto inicial) y termina con código 0;
  - una opción desconocida (que empieza por `-`) termina con código 2 y un mensaje;
  - una ruta que no existe termina con código 2 y un mensaje (sin esto, comprobar una ruta mal
    escrita revisaría 0 ficheros y daría un ✅ falso).
"""
import sys
from pathlib import Path


def revisar(ayuda, opciones=(), opciones_con_valor=(), rutas=True, maximo=None):
    """Devuelve (opciones usadas, valores de las opciones, argumentos sueltos), o termina si hay un error.

    ayuda: el texto inicial de la herramienta (__doc__), que se muestra con -h o --help.
    opciones: las opciones sin valor que admite (por ejemplo, "--comprobar").
    opciones_con_valor: las que llevan un valor detrás (por ejemplo, "--curso").
    rutas: si True, cada argumento suelto debe ser una ruta que existe.
    maximo: número máximo de argumentos sueltos.
    """
    argumentos = sys.argv[1:]
    if "-h" in argumentos or "--help" in argumentos:
        print(ayuda.strip())
        sys.exit(0)
    usadas, valores, sueltos = set(), {}, []
    i = 0
    while i < len(argumentos):
        a = argumentos[i]
        if a.startswith("-"):
            if a in opciones:
                usadas.add(a)
            elif a in opciones_con_valor:
                if i + 1 >= len(argumentos) or argumentos[i + 1].startswith("-"):
                    salir(f"Falta el valor de {a}.")
                valores[a] = argumentos[i + 1]
                i += 1
            else:
                salir(f"Opción desconocida: {a}.")
        else:
            sueltos.append(a)
        i += 1
    if maximo is not None and len(sueltos) > maximo:
        salir("Demasiados argumentos." if maximo else f"No admite argumentos ({' '.join(sueltos)}).")
    if rutas:
        no_existen = [a for a in sueltos if not Path(a).exists()]
        if no_existen:
            salir(f"No existe: {', '.join(no_existen)}. No se ha revisado nada.")
    return usadas, valores, sueltos


def salir(mensaje):
    print(f"❌ {mensaje} Usa --help para ver la ayuda.", file=sys.stderr)
    sys.exit(2)
