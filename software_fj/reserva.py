from software_fj.entidad import EntidadSistema
from software_fj.cliente import Cliente      # Para validar que el cliente sea un Cliente real
from software_fj.servicios import Servicio   # Para validar que el servicio sea un Servicio real
from software_fj.excepciones import (
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
)
from software_fj.registro_log import logger


class Reserva(EntidadSistema):
    """Administra las reservas de clientes y servicios."""

    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"

    def __init__(self, id_reserva, cliente, servicio, duracion):
        super().__init__(id_reserva)

        # Se valida el TIPO y no solo que exista: un texto u otro objeto
        # cualquiera no puede usarse como cliente o como servicio.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError(
                "La reserva requiere un cliente válido.", detalle=cliente
            )

        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError(
                "La reserva requiere un servicio válido.", detalle=servicio
            )

        try:
            servicio.verificar_disponibilidad()
            duracion_validada = servicio.validar_parametros(duracion)
        except Exception as exc:
            raise ReservaInvalidaError(
                "Los datos de la reserva no son válidos."
            ) from exc

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion_validada
        self._estado = self.PENDIENTE
        self._costo_total = servicio.calcular_costo(duracion)

        logger.info(
            "Reserva creada: %s para cliente %s",
            self.id,
            getattr(cliente, "id", "sin-id"),
        )

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self):
        if self._estado != self.PENDIENTE:
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        self._servicio.verificar_disponibilidad()

        self._estado = self.CONFIRMADA

        logger.info("Reserva %s confirmada", self.id)

        return True

    def cancelar(self, motivo="Sin especificar"):
        if self._estado == self.CANCELADA:
            raise OperacionNoPermitidaError(
                "La reserva ya fue cancelada."
            )

        self._estado = self.CANCELADA

        logger.info(
            "Reserva %s cancelada: %s",
            self.id,
            motivo,
        )

        return True

    def procesar(self):
        if self._estado != self.CONFIRMADA:
            raise OperacionNoPermitidaError(
                "Solo se pueden procesar reservas confirmadas."
            )

        logger.info("Reserva %s procesada", self.id)

        return True

    def describir(self):
        return (
            f"Reserva {self.id}: "
            f"cliente={self.cliente.id}, "
            f"servicio={self.servicio.nombre}, "
            f"duracion={self._duracion}, "
            f"estado={self.estado}, "
            f"costo={self.costo_total:.2f}"
        )