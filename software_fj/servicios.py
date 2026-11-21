# -*- coding: utf-8 -*-
"""
===============================================================================
 Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
 Módulo:  servicios.py  (Parte 3)
 Autor:   Leonardo Albeiro Garatejo Mendez - Grupo 213023_170
 Curso:   Programación (213023) - UNAD - Fase 4
===============================================================================
 Servicios que ofrece la empresa Software FJ.

   Servicio (clase ABSTRACTA, hereda de EntidadSistema)
   ├── ReservaSala     -> se cobra por HORA, según la capacidad de la sala
   ├── AlquilerEquipo  -> se cobra por DÍA y por cada unidad alquilada
   └── Asesoria        -> se cobra por HORA, según el nivel del asesor

 Conceptos de POO aplicados:
   - ABSTRACCIÓN: Servicio define qué debe saber hacer todo servicio, pero no
     se puede crear un "servicio genérico" (sus métodos son abstractos).
   - HERENCIA: los tres servicios reciben de Servicio el nombre, la tarifa,
     la disponibilidad y el cálculo de impuestos y descuentos.
   - POLIMORFISMO y SOBREESCRITURA: los tres responden a calcular_costo(),
     describir() y validar_parametros(), cada uno a su manera.
   - SOBRECARGA (simulada): calcular_costo acepta tres formas de llamarse:
         calcular_costo(duracion)
         calcular_costo(duracion, impuesto)
         calcular_costo(duracion, impuesto, descuento)
     Python no permite varios métodos con el mismo nombre (el último borra
     a los anteriores), por eso se usan parámetros opcionales (=None).
   - ENCAPSULACIÓN: los datos son privados (_) y se modifican solo por
     propiedades que validan lo que reciben.

 Métodos que usa la Parte 4 (Reserva):
   servicio.verificar_disponibilidad()  -> lanza ServicioNoDisponibleError
   servicio.validar_parametros(duracion) -> devuelve la duración validada
   servicio.calcular_costo(duracion[, impuesto[, descuento]])
===============================================================================
"""

from abc import ABC, abstractmethod          # Herramientas para clases abstractas

from .entidad import EntidadSistema          # Clase base de la Parte 2 (Diego)
from .excepciones import (                   # Excepciones personalizadas (Parte 1)
    DatoInvalidoError,
    ServicioNoDisponibleError,
    CalculoInconsistenteError,
)
from .registro_log import (                  # Log y validaciones (Parte 1)
    logger,
    validar_obligatorio,
    convertir_numero,
)


# =============================================================================
# CLASE ABSTRACTA SERVICIO
# =============================================================================
class Servicio(EntidadSistema, ABC):
    """Molde general de todos los servicios de Software FJ.

    No se puede instanciar directamente: cada servicio concreto debe
    implementar calcular_costo(), describir() y validar_parametros().
    """

    # Cada servicio concreto sobrescribe estos datos de clase
    UNIDAD = "unidad"            # Unidad en que se cobra (hora, día...)
    DURACION_MINIMA = 1          # Duración mínima permitida
    DURACION_MAXIMA = 1          # Duración máxima permitida

    def __init__(self, id_servicio, nombre, tarifa_base, disponible=True):
        super().__init__(id_servicio)                       # El padre valida el id
        self.nombre = nombre                                # Pasa por el setter (valida)
        self.tarifa_base = tarifa_base                      # Pasa por el setter (valida)
        self._disponible = bool(disponible)                 # Estado inicial del servicio
        logger.info("Servicio creado: %s", self.describir())

    # ------------------------------------------------------------------ #
    # Propiedades con validación (encapsulación)
    # ------------------------------------------------------------------ #
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        # validar_obligatorio lanza ParametroFaltanteError si viene vacío
        self._nombre = str(validar_obligatorio(valor, "nombre del servicio")).strip()

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        # convertir_numero aplica encadenamiento: "abc" -> DatoInvalidoError from ValueError
        tarifa = convertir_numero(valor, "tarifa base")
        if tarifa <= 0:                                     # Una tarifa debe ser positiva
            raise DatoInvalidoError("La tarifa base debe ser mayor que cero.", detalle=valor)
        self._tarifa_base = tarifa

    @property
    def disponible(self):
        return self._disponible

    # ------------------------------------------------------------------ #
    # Disponibilidad del servicio
    # ------------------------------------------------------------------ #
    def habilitar(self):
        """Deja el servicio disponible para nuevas reservas."""
        self._disponible = True
        logger.info("Servicio habilitado: %s", self.nombre)

    def deshabilitar(self):
        """Saca el servicio de uso (mantenimiento, daño, etc.)."""
        self._disponible = False
        logger.info("Servicio deshabilitado: %s", self.nombre)

    def verificar_disponibilidad(self):
        """Lanza ServicioNoDisponibleError si el servicio está deshabilitado."""
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible en este momento.",
                detalle=self.id,
            )

    # ------------------------------------------------------------------ #
    # Lógica común que heredan los tres servicios
    # ------------------------------------------------------------------ #
    def _validar_duracion(self, duracion):
        """Convierte la duración a número y revisa que esté en el rango permitido.

        Los servicios la usan dentro de su propio validar_parametros().
        """
        valor = convertir_numero(duracion, f"duración ({self.UNIDAD}s)")
        if not self.DURACION_MINIMA <= valor <= self.DURACION_MAXIMA:
            raise DatoInvalidoError(
                f"La duración debe estar entre {self.DURACION_MINIMA} y "
                f"{self.DURACION_MAXIMA} {self.UNIDAD}s.",
                detalle=duracion,
            )
        return valor

    @staticmethod
    def _aplicar_ajustes(subtotal, impuesto=None, descuento=None):
        """Aplica el impuesto y el descuento a un subtotal (en porcentaje).

        Orden: primero se descuenta y luego se cobra el impuesto sobre lo que
        queda, como en una factura. Lanza CalculoInconsistenteError si los
        porcentajes no tienen sentido o el resultado no es lógico.
        """
        total = subtotal
        if descuento is not None:                           # Firma con descuento
            porcentaje = convertir_numero(descuento, "descuento (%)")
            if not 0 <= porcentaje <= 100:
                raise CalculoInconsistenteError(
                    "El descuento debe estar entre 0 % y 100 %.", detalle=descuento)
            total -= total * porcentaje / 100
        if impuesto is not None:                            # Firma con impuesto
            porcentaje = convertir_numero(impuesto, "impuesto (%)")
            if not 0 <= porcentaje <= 100:
                raise CalculoInconsistenteError(
                    "El impuesto debe estar entre 0 % y 100 %.", detalle=impuesto)
            total += total * porcentaje / 100
        if total < 0:                                       # Control final de seguridad
            raise CalculoInconsistenteError("El costo total no puede ser negativo.", detalle=total)
        return round(total, 2)

    def _calcular_con_firma(self, subtotal, impuesto, descuento):
        """Aplica la SOBRECARGA simulada y registra qué firma se usó."""
        if impuesto is None and descuento is not None:
            # La tercera firma del enunciado es (duracion, impuesto, descuento)
            raise CalculoInconsistenteError(
                "Para aplicar descuento también se debe indicar el impuesto "
                "(use 0 si no aplica).")
        if impuesto is None:
            firma = "calcular_costo(duracion)"
        elif descuento is None:
            firma = "calcular_costo(duracion, impuesto)"
        else:
            firma = "calcular_costo(duracion, impuesto, descuento)"
        total = self._aplicar_ajustes(subtotal, impuesto, descuento)
        logger.info("%s | %s | subtotal=%.2f total=%.2f", firma, self.nombre, subtotal, total)
        return total

    # ------------------------------------------------------------------ #
    # Métodos ABSTRACTOS: cada servicio DEBE implementarlos
    # ------------------------------------------------------------------ #
    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida la duración según las reglas del servicio y la devuelve."""

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=None, descuento=None):
        """Calcula el costo del servicio para la duración indicada."""

    # describir() ya es abstracto en EntidadSistema (Parte 2)


# =============================================================================
# SERVICIO 1: RESERVA DE SALAS (se cobra por hora)
# =============================================================================
class ReservaSala(Servicio):
    """Sala de reuniones. Las salas grandes tienen un recargo del 20 %."""

    UNIDAD = "hora"
    DURACION_MINIMA = 1
    DURACION_MAXIMA = 12                 # Máximo una jornada de 12 horas
    CAPACIDAD_GRANDE = 20                # Desde 20 personas se considera sala grande
    RECARGO_SALA_GRANDE = 0.20           # 20 % adicional

    def __init__(self, id_servicio, nombre, tarifa_base, capacidad, disponible=True):
        cap = convertir_numero(capacidad, "capacidad")      # Encadenamiento si no es número
        if cap < 1 or cap != int(cap):
            raise DatoInvalidoError("La capacidad debe ser un número entero de 1 o más.",
                                    detalle=capacidad)
        self._capacidad = int(cap)                          # Se guarda antes de llamar al padre,
        super().__init__(id_servicio, nombre, tarifa_base, disponible)  # que usa describir()

    @property
    def capacidad(self):
        return self._capacidad

    def validar_parametros(self, duracion):                 # SOBREESCRITURA
        return self._validar_duracion(duracion)

    def calcular_costo(self, duracion, impuesto=None, descuento=None):   # POLIMORFISMO
        horas = self.validar_parametros(duracion)
        subtotal = self.tarifa_base * horas
        if self._capacidad >= self.CAPACIDAD_GRANDE:        # Regla propia de las salas
            subtotal *= 1 + self.RECARGO_SALA_GRANDE
        return self._calcular_con_firma(subtotal, impuesto, descuento)

    def describir(self):                                    # SOBREESCRITURA
        estado = "disponible" if self.disponible else "no disponible"
        return (f"Sala '{self.nombre}' para {self._capacidad} personas, "
                f"${self.tarifa_base:,.0f} por hora ({estado})")


# =============================================================================
# SERVICIO 2: ALQUILER DE EQUIPOS (se cobra por día y por unidad)
# =============================================================================
class AlquilerEquipo(Servicio):
    """Equipos como portátiles o proyectores, alquilados por días."""

    UNIDAD = "día"
    DURACION_MINIMA = 1
    DURACION_MAXIMA = 30                 # Máximo un mes de alquiler

    def __init__(self, id_servicio, nombre, tarifa_base, unidades_disponibles, disponible=True):
        cant = convertir_numero(unidades_disponibles, "unidades disponibles")
        if cant < 1 or cant != int(cant):
            raise DatoInvalidoError("Las unidades disponibles deben ser un entero de 1 o más.",
                                    detalle=unidades_disponibles)
        self._unidades = int(cant)
        super().__init__(id_servicio, nombre, tarifa_base, disponible)

    @property
    def unidades_disponibles(self):
        return self._unidades

    def validar_parametros(self, duracion, cantidad=1):     # SOBREESCRITURA
        dias = self._validar_duracion(duracion)
        unidades = convertir_numero(cantidad, "cantidad de equipos")
        if not 1 <= unidades <= self._unidades:             # No se alquila lo que no hay
            raise DatoInvalidoError(
                f"Solo hay {self._unidades} unidades de '{self.nombre}'.", detalle=cantidad)
        return dias, unidades

    def calcular_costo(self, duracion, impuesto=None, descuento=None, cantidad=1):  # POLIMORFISMO
        dias, unidades = self.validar_parametros(duracion, cantidad)
        subtotal = self.tarifa_base * dias * unidades
        return self._calcular_con_firma(subtotal, impuesto, descuento)

    def describir(self):                                    # SOBREESCRITURA
        estado = "disponible" if self.disponible else "no disponible"
        return (f"Equipo '{self.nombre}' ({self._unidades} unidades), "
                f"${self.tarifa_base:,.0f} por día cada uno ({estado})")


# =============================================================================
# SERVICIO 3: ASESORÍAS ESPECIALIZADAS (se cobra por hora, según el nivel)
# =============================================================================
class Asesoria(Servicio):
    """Asesoría con un experto. El nivel cambia el valor de la hora."""

    UNIDAD = "hora"
    DURACION_MINIMA = 1
    DURACION_MAXIMA = 8                  # Máximo una jornada laboral
    NIVELES = {"basico": 1.0, "senior": 1.5, "experto": 2.0}   # Multiplicador por nivel

    def __init__(self, id_servicio, nombre, tarifa_base, especialidad, nivel="basico",
                 disponible=True):
        self._especialidad = str(validar_obligatorio(especialidad, "especialidad")).strip()
        nivel = str(validar_obligatorio(nivel, "nivel")).strip().lower()
        if nivel not in self.NIVELES:
            raise DatoInvalidoError(
                f"Nivel no válido. Opciones: {', '.join(self.NIVELES)}.", detalle=nivel)
        self._nivel = nivel
        super().__init__(id_servicio, nombre, tarifa_base, disponible)

    @property
    def especialidad(self):
        return self._especialidad

    @property
    def nivel(self):
        return self._nivel

    def validar_parametros(self, duracion):                 # SOBREESCRITURA
        return self._validar_duracion(duracion)

    def calcular_costo(self, duracion, impuesto=None, descuento=None):   # POLIMORFISMO
        horas = self.validar_parametros(duracion)
        subtotal = self.tarifa_base * self.NIVELES[self._nivel] * horas
        return self._calcular_con_firma(subtotal, impuesto, descuento)

    def describir(self):                                    # SOBREESCRITURA
        estado = "disponible" if self.disponible else "no disponible"
        return (f"Asesoría '{self.nombre}' en {self._especialidad}, nivel {self._nivel}, "
                f"${self.tarifa_base:,.0f} por hora base ({estado})")


# -----------------------------------------------------------------------------
# Prueba rápida de la Parte 3 (solo si se ejecuta este archivo directamente):
#   python -m software_fj.servicios
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    from .registro_log import ejecutar_operacion

    sala = ReservaSala("S1", "Sala Huila", 50000, 25)
    equipo = AlquilerEquipo("E1", "Portátil", 40000, 5)
    asesoria = Asesoria("A1", "Asesoría en redes", 80000, "Redes", "senior")

    # POLIMORFISMO: la misma llamada, cada servicio responde a su manera
    for servicio in (sala, equipo, asesoria):
        print(servicio.describir())
        print("  2 unidades de tiempo:", servicio.calcular_costo(2))

    # SOBRECARGA: las tres firmas de calcular_costo
    print(ejecutar_operacion("Sala 3 h", sala.calcular_costo, 3).valor)
    print(ejecutar_operacion("Sala 3 h + IVA 19 %", sala.calcular_costo, 3, 19).valor)
    print(ejecutar_operacion("Sala 3 h + IVA 19 % - 10 %", sala.calcular_costo, 3, 19, 10).valor)

    # Casos de error: el programa NO se detiene
    ejecutar_operacion("Tarifa con letras", ReservaSala, "S2", "Sala 2", "abc", 10)
    ejecutar_operacion("Sala por 20 horas", sala.calcular_costo, 20)
    ejecutar_operacion("Descuento de 150 %", sala.calcular_costo, 2, 19, 150)
    ejecutar_operacion("Alquilar 9 portátiles", equipo.calcular_costo, 2, None, None, 9)
    equipo.deshabilitar()
    ejecutar_operacion("Equipo en mantenimiento", equipo.verificar_disponibilidad)
    ejecutar_operacion("Nivel inexistente", Asesoria, "A2", "Asesoría", 50000, "Python", "master")
