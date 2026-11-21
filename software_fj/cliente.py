import re
from software_fj.entidad import EntidadSistema
from software_fj.excepciones import ClienteInvalidoError, DatoInvalidoError
from software_fj.registro_log import logger, validar_obligatorio


class Cliente(EntidadSistema):
    """Representa un cliente del sistema con atributos privados y validados."""

    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str,
    ):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        logger.info("Cliente registrado: id=%s, nombre=%s", self.id, self._nombre)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        nombre_limpio = str(validar_obligatorio(valor, "nombre")).strip()
        if len(nombre_limpio) < 2:
            raise ClienteInvalidoError(
                "El nombre del cliente debe tener al menos 2 caracteres."
            )
        self._nombre = nombre_limpio

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        doc_limpio = str(validar_obligatorio(valor, "documento")).strip()
        if not doc_limpio.isdigit() or len(doc_limpio) < 5:
            raise DatoInvalidoError(
                f"Documento inválido ({valor}): debe contener al menos 5 dígitos numéricos."
            )
        self._documento = doc_limpio

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        correo_limpio = str(validar_obligatorio(valor, "correo")).strip()
        patron_correo = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(patron_correo, correo_limpio):
            raise DatoInvalidoError(f"Correo electrónico inválido: {valor}")
        self._correo = correo_limpio

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        tel_limpio = str(validar_obligatorio(valor, "telefono")).strip()
        if not tel_limpio.isdigit() or len(tel_limpio) < 7:
            raise DatoInvalidoError(
                f"Teléfono inválido ({valor}): debe contener al menos 7 dígitos numéricos."
            )
        self._telefono = tel_limpio

    def describir(self) -> str:
        return (
            f"Cliente(id={self.id}, nombre={self._nombre}, "
            f"documento={self._documento}, correo={self._correo}, telefono={self._telefono})"
        )