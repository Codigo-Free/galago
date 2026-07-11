from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class InputState:
    """Snapshot de un frame de entrada.

    `quit`/`enter`/`space` son eventos puntuales (KEYDOWN de ese frame);
    `move`/`shoot` reflejan el estado continuo del teclado (tecla mantenida).
    """
    quit: bool = False
    enter: bool = False
    space: bool = False
    move: int = 0       # -1 izquierda, 0 quieto, 1 derecha
    shoot: bool = False


class InputProvider(Protocol):
    def poll(self) -> InputState:
        ...
