# -*- coding: utf-8 -*-
"""
===============================================================================
 Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
 Módulo:  registro_log.py  (Parte 1)
 Autor:   Leonardo Albeiro Garatejo Mendez - Grupo 213023_170
 Curso:   Programación (213023) - UNAD - Fase 4
===============================================================================
 Este módulo ofrece a todo el equipo tres herramientas:

 1. logger
    Registra eventos y errores en el archivo logs/software_fj.log
    y también los muestra en pantalla.

 2. ejecutar_operacion(descripcion, funcion, *args, **kwargs)
    Ejecuta cualquier operación del sistema de forma SEGURA usando
    try / except / else / finally. Si la operación falla, el error queda
    en el log y el programa sigue funcionando: la aplicación nunca se detiene.

 3. convertir_numero(valor, campo) y validar_obligatorio(valor, campo)
    Validaciones reutilizables. convertir_numero aplica ENCADENAMIENTO
    de excepciones (raise ... from ...): convierte un error técnico de
    Python en un error del negocio sin perder la causa original.
===============================================================================
"""

import logging                      # Módulo estándar de Python para registrar eventos
from pathlib import Path            # Manejo de rutas compatible con Windows y Linux

from .excepciones import (          # Excepciones personalizadas del sistema (Parte 1)
    SoftwareFJError,
    DatoInvalidoError,
    ParametroFaltanteError,
)

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DEL LOG
# -----------------------------------------------------------------------------
# Carpeta "logs" ubicada en la raíz del proyecto (un nivel arriba de este archivo)
CARPETA_LOGS = Path(__file__).resolve().parent.parent / "logs"
ARCHIVO_LOG = CARPETA_LOGS / "software_fj.log"

# Formato de cada línea: fecha y hora | nivel | mensaje
FORMATO = "%(asctime)s | %(levelname)-8s | %(message)s"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def _configurar_logger():
    """Crea y configura el logger del sistema una sola vez."""
    CARPETA_LOGS.mkdir(exist_ok=True)               # Crea la carpeta logs si no existe
    registro = logging.getLogger("software_fj")     # Logger con nombre propio del proyecto
    registro.setLevel(logging.DEBUG)                # Acepta todos los niveles de mensajes
    registro.propagate = False                      # Evita mensajes duplicados en Jupyter

    # En un notebook las celdas se ejecutan varias veces; si el logger ya tiene
    # manejadores, no se agregan de nuevo (de lo contrario cada línea saldría repetida).
    if registro.handlers:
        return registro

    formateador = logging.Formatter(FORMATO, FORMATO_FECHA)

    # Manejador de ARCHIVO: guarda todo (DEBUG en adelante) en logs/software_fj.log
    en_archivo = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    en_archivo.setLevel(logging.DEBUG)
    en_archivo.setFormatter(formateador)

    # Manejador de PANTALLA: muestra solo lo importante (INFO en adelante)
    en_pantalla = logging.StreamHandler()
    en_pantalla.setLevel(logging.INFO)
    en_pantalla.setFormatter(formateador)

    registro.addHandler(en_archivo)
    registro.addHandler(en_pantalla)
    return registro


logger = _configurar_logger()   # Objeto que importan los demás módulos


# -----------------------------------------------------------------------------
# 2. EJECUCIÓN SEGURA DE OPERACIONES
# -----------------------------------------------------------------------------
class ResultadoOperacion:
    """Resumen de una operación ejecutada con ejecutar_operacion().

    Atributos:
        descripcion -> texto que describe la operación
        exitosa     -> True si terminó bien, False si falló
        valor       -> lo que devolvió la operación (si fue exitosa)
        error       -> la excepción capturada (si falló)
    """

    def __init__(self, descripcion, exitosa, valor=None, error=None):
        self.descripcion = descripcion
        self.exitosa = exitosa
        self.valor = valor
        self.error = error

    def __repr__(self):
        estado = "ÉXITO" if self.exitosa else "FALLO"
        return f"<ResultadoOperacion {estado}: {self.descripcion}>"


def ejecutar_operacion(descripcion, funcion, *args, **kwargs):
    """Ejecuta funcion(*args, **kwargs) sin que un error detenga el programa.

    Aplica los cuatro bloques del manejo de excepciones:
        try     -> intenta ejecutar la operación
        except  -> si falla, registra el error y continúa
        else    -> solo se ejecuta si NO hubo error: registra el éxito
        finally -> se ejecuta SIEMPRE: cierra el registro de la operación

    Devuelve un ResultadoOperacion; nunca lanza excepciones hacia afuera.
    """
    logger.info("INICIO   | %s", descripcion)
    resultado = None

    try:
        valor = funcion(*args, **kwargs)            # Se intenta la operación

    except SoftwareFJError as error:
        # Error PREVISTO del negocio: dato inválido, servicio no disponible, etc.
        logger.error("FALLO    | %s | %s: %s", descripcion, type(error).__name__, error)
        # Si el error fue encadenado (raise ... from ...), también se registra la causa
        if error.__cause__ is not None:
            causa = error.__cause__
            logger.error("  CAUSA  | %s: %s", type(causa).__name__, causa)
        resultado = ResultadoOperacion(descripcion, False, error=error)

    except Exception as error:
        # Error NO previsto (posible falla de programación). Se registra con el
        # rastreo completo (exc_info=True) para poder corregirlo, pero el sistema sigue.
        logger.critical("INESPERADO | %s | %s: %s", descripcion,
                        type(error).__name__, error, exc_info=True)
        resultado = ResultadoOperacion(descripcion, False, error=error)

    else:
        # Solo llega aquí si el bloque try terminó sin errores
        logger.info("ÉXITO    | %s", descripcion)
        resultado = ResultadoOperacion(descripcion, True, valor=valor)

    finally:
        # Se ejecuta pase lo que pase: deja constancia de que la operación terminó
        logger.debug("FIN      | %s", descripcion)

    return resultado


# -----------------------------------------------------------------------------
# 3. VALIDACIONES REUTILIZABLES
# -----------------------------------------------------------------------------
def validar_obligatorio(valor, campo):
    """Verifica que un valor no esté vacío. Devuelve el valor sin espacios sobrantes.

    Lanza ParametroFaltanteError si el valor es None o un texto vacío.
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.", detalle=valor)
    return valor.strip() if isinstance(valor, str) else valor


def convertir_numero(valor, campo):
    """Convierte un valor a número decimal (float).

    ENCADENAMIENTO DE EXCEPCIONES:
    Si Python no puede convertir el valor, lanza ValueError o TypeError.
    Ese error técnico se transforma en DatoInvalidoError usando
    "raise ... from error", de modo que el nuevo error conserva la causa
    original en su atributo __cause__ y el log puede mostrar ambas.
    """
    validar_obligatorio(valor, campo)               # Primero: que no venga vacío
    try:
        return float(str(valor).replace(",", "."))  # Acepta "1500,5" y "1500.5"
    except (TypeError, ValueError) as error:
        raise DatoInvalidoError(
            f"El campo '{campo}' debe ser numérico.", detalle=valor
        ) from error                                # <- encadenamiento


# -----------------------------------------------------------------------------
# Prueba rápida de la Parte 1 (solo se ejecuta si se corre este archivo directamente)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(ejecutar_operacion("Convertir '2500' a número", convertir_numero, "2500", "tarifa"))
    print(ejecutar_operacion("Convertir 'abc' a número", convertir_numero, "abc", "tarifa"))
    print(ejecutar_operacion("Validar nombre vacío", validar_obligatorio, "  ", "nombre"))
    print(ejecutar_operacion("División por cero (error no previsto)", lambda: 10 / 0))
    print(f"Log generado en: {ARCHIVO_LOG}")
