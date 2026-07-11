import sys
from pathlib import Path


def resource_root() -> Path:
    """Raíz desde donde resolver `assets/` y otros recursos empaquetados.

    Corriendo empaquetado con PyInstaller, los datos agregados con
    `datas=[('assets', 'assets')]` se extraen a `sys._MEIPASS` en tiempo de
    ejecución. Corriendo desde el código fuente, es la raíz del repo.
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    # src/galago/paths.py -> src/galago -> src -> raíz del repo
    return Path(__file__).resolve().parents[2]
