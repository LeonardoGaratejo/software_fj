from abc import ABC, abstractmethod
from software_fj.registro_log import validar_obligatorio


class EntidadSistema(ABC):
    """Clase base abstracta para todas las entidades del sistema Software FJ."""

    def __init__(self, id_entidad: str):
        self._id = validar_obligatorio(id_entidad, "id")

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""
        pass

    def __str__(self) -> str:
        return self.describir()