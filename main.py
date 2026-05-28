"""
main.py — Punto de entrada del compilador
==========================================
Lenguaje de Comunicación Personal · Lenguajes y Autómatas

Equipo: Nicolás · Ricardo · Rasshid

Uso:
    python main.py

El compilador traduce secuencias de señas, sonidos y gestos
corporales a frases en español natural, facilitando la
comunicación del cuidador con una persona con discapacidad
comunicativa.
"""

import sys
import os

# Asegurarse de que el directorio del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Verificar dependencias antes de arrancar
def _verificar_dependencias():
    faltantes = []
    for modulo in ("ply", "tkinter"):
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(modulo)
    if faltantes:
        print("ERROR: Faltan dependencias requeridas:")
        for m in faltantes:
            print(f"  · {m}")
        print("\nInstala con:  pip install ply")
        sys.exit(1)

_verificar_dependencias()

import tkinter as tk
from interfaz import Interfaz


def main():
    root = tk.Tk()
    root.title("Compilador · Lenguaje de Comunicación Personal")
    app = Interfaz(root)
    root.mainloop()


if __name__ == "__main__":
    main()
