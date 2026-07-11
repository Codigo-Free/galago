from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class InputState:
    """Snapshot de un frame de entrada.

    `quit`/`enter`/`space`/`high_scores`/`left`/`right`/`up`/`down` son eventos
    puntuales (KEYDOWN de ese frame); `move`/`shoot` reflejan el estado
    continuo del teclado (tecla mantenida).
    """
    quit: bool = False
    enter: bool = False
    space: bool = False
    move: int = 0       # -1 izquierda, 0 quieto, 1 derecha
    shoot: bool = False
    high_scores: bool = False  # tecla H, entra a la pantalla de high scores desde el título
    left: bool = False         # flecha izquierda, mueve el cursor en la pantalla de iniciales
    right: bool = False        # flecha derecha
    up: bool = False           # flecha arriba, cicla la letra hacia adelante
    down: bool = False         # flecha abajo, cicla la letra hacia atrás


class InputProvider(Protocol):
    def poll(self) -> InputState:
        ...
