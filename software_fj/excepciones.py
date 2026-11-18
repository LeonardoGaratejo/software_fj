# -*- coding: utf-8 -*-
"""
===============================================================================
 Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
 Módulo:  excepciones.py  (Parte 1)
 Autor:   Leonardo Albeiro Garatejo Mendez - Grupo 213023_170
 Curso:   Programación (213023) - UNAD - Fase 4
===============================================================================
 Jerarquía de EXCEPCIONES PERSONALIZADAS del sistema.

 ¿Por qué crear excepciones propias en lugar de usar ValueError o Exception?
   1. Dicen QUÉ falló en lenguaje del negocio ("servicio no disponible")
      y no solo en lenguaje de Python ("valor incorrecto").
   2. Al heredar todas de SoftwareFJError, el programa puede atrapar
      cualquier error del sistema con un solo "except SoftwareFJError",
      sin atrapar por accidente errores de programación (bugs).
   3. Cada una guarda un código y el detalle del dato que causó el
      problema, lo que facilita leer el archivo de log.

 Jerarquía:
   SoftwareFJError
   ├── DatoInvalidoError
   │   └── ClienteInvalidoError
   ├── ParametroFaltanteError
   ├── ServicioNoDisponibleError
   ├── ReservaInvalidaError
   ├── OperacionNoPermitidaError
   └── CalculoInconsistenteError
===============================================================================
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ.

    Todas las demás excepciones del proyecto heredan de esta clase.
    """

    codigo = "SFJ-000"  # Código general; cada subclase lo sobrescribe con el suyo

    def __init__(self, mensaje, detalle=None):
        # Se llama al constructor de Exception para que el mensaje
        # se muestre normalmente al imprimir la excepción
        super().__init__(mensaje)
        self.mensaje = mensaje  # Texto legible del error
        self.detalle = detalle  # Información adicional (dato recibido, campo, etc.)

    def __str__(self):
        # Formato uniforme para el log: [CÓDIGO] mensaje (detalle: ...)
        texto = f"[{self.codigo}] {self.mensaje}"
        if self.detalle is not None:
            texto += f" (detalle: {self.detalle})"
        return texto


class DatoInvalidoError(SoftwareFJError):
    """Un dato tiene un formato o un valor que no se acepta
    (texto donde va un número, valor negativo, correo mal escrito, etc.)."""

    codigo = "SFJ-100"


class ClienteInvalidoError(DatoInvalidoError):
    """Los datos de un cliente no superan las validaciones.

    Hereda de DatoInvalidoError porque es un caso particular de dato inválido:
    quien atrape DatoInvalidoError también atrapa este error.
    """

    codigo = "SFJ-110"


class ParametroFaltanteError(SoftwareFJError):
    """Falta un parámetro obligatorio (vacío o None)."""

    codigo = "SFJ-200"


class ServicioNoDisponibleError(SoftwareFJError):
    """Se intenta reservar un servicio que está deshabilitado o no existe."""

    codigo = "SFJ-300"


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no se puede crear con los datos recibidos
    (duración fuera de rango, cliente o servicio incorrecto, etc.)."""

    codigo = "SFJ-400"


class OperacionNoPermitidaError(SoftwareFJError):
    """La operación no está permitida en el estado actual
    (por ejemplo, confirmar una reserva que ya fue cancelada)."""

    codigo = "SFJ-500"


class CalculoInconsistenteError(SoftwareFJError):
    """Un cálculo produce un resultado ilógico
    (costo negativo, descuento mayor al total, impuesto fuera de rango)."""

    codigo = "SFJ-600"
