"""Punto de entrada exclusivo para el build de PyInstaller (ver galago.spec).

Separado de galago.py a propósito: si el script de entrada se llamara
`galago.py`, el análisis estático de PyInstaller confunde el script con el
paquete `galago/` (mismo nombre) y falla al resolver `galago.__main__`. En
modo desarrollo esto no pasa porque `python galago.py` sí ejecuta el código
en tiempo real (el truco de sys.path funciona ahí), pero PyInstaller solo
analiza el código sin correrlo.
"""
from galago.__main__ import main

if __name__ == "__main__":
    main()
