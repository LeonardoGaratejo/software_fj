# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto colaborativo de la **Fase 4 – Componente práctico** del curso **Programación (213023)**,
grupo **213023_170**, Universidad Nacional Abierta y a Distancia (UNAD).

Sistema orientado a objetos, **sin base de datos**, que gestiona clientes, servicios
(reserva de salas, alquiler de equipos y asesorías especializadas) y reservas. Toda la
información vive en objetos y listas; el único archivo que se escribe es el **log** de
eventos y errores (`logs/software_fj.log`).

## Estructura del repositorio

```
software_fj/
├── README.md
├── .gitignore
├── software_fj/              # Paquete con el código fuente
│   ├── __init__.py
│   ├── excepciones.py        # Parte 1 – Excepciones personalizadas
│   ├── registro_log.py       # Parte 1 – Log y ejecución segura de operaciones
│   ├── entidad.py            # Parte 2 – Clase abstracta EntidadSistema
│   ├── cliente.py            # Parte 2 – Clase Cliente
│   ├── servicios.py          # Parte 3 – Servicio abstracto y 3 servicios
│   └── reserva.py            # Parte 4 – Clase Reserva
├── simulaciones.ipynb        # Parte 5 – Mínimo 10 operaciones simuladas
└── logs/                     # Aquí se genera software_fj.log al ejecutar
```

## Reparto del trabajo (una rama y un issue por integrante)

| Parte | Rama | Archivos | Qué entrega |
|---|---|---|---|
| 1 | `parte-1-excepciones-log` | `excepciones.py`, `registro_log.py` | Jerarquía de excepciones personalizadas, configuración del log, función `ejecutar_operacion` (try/except/else/finally) y `convertir_numero` (encadenamiento) |
| 2 | `parte-2-cliente` | `entidad.py`, `cliente.py` | Clase abstracta `EntidadSistema` y clase `Cliente` con validaciones y datos encapsulados |
| 3 | `parte-3-servicios` | `servicios.py` | Clase abstracta `Servicio` y `ReservaSala`, `AlquilerEquipo`, `Asesoria` con polimorfismo y sobrecarga de `calcular_costo` |
| 4 | `parte-4-reserva` | `reserva.py` | Clase `Reserva` con `confirmar`, `cancelar` y `procesar` |
| 5 | `parte-5-simulaciones` | `simulaciones.ipynb` | Al menos 10 operaciones válidas e inválidas que demuestran que el sistema nunca se detiene |

Cada integrante trabaja en su rama y abre un *pull request* hacia `main`.

## Contrato entre las partes

Para que las piezas encajen sin esperar a los demás, cada parte respeta estos nombres:

**Parte 1 – `excepciones.py`** (ya disponible)
- `SoftwareFJError` (base de todas)
- `DatoInvalidoError`, `ParametroFaltanteError`, `ClienteInvalidoError`,
  `ServicioNoDisponibleError`, `ReservaInvalidaError`,
  `OperacionNoPermitidaError`, `CalculoInconsistenteError`

**Parte 1 – `registro_log.py`** (ya disponible)
- `logger` → registrar eventos con `logger.info(...)` y errores con `logger.error(...)`
- `ejecutar_operacion(descripcion, funcion, *args, **kwargs)` → ejecuta cualquier
  operación sin detener el programa y devuelve un `ResultadoOperacion`
  (`.exitosa`, `.valor`, `.error`)
- `convertir_numero(valor, campo)` → convierte a número o lanza `DatoInvalidoError`
  encadenada (`raise ... from ...`)
- `validar_obligatorio(valor, campo)` → lanza `ParametroFaltanteError` si el valor está vacío

**Parte 2** – `EntidadSistema(ABC)` con `id` y el método abstracto `describir()`.
`Cliente(EntidadSistema)` con `nombre`, `documento`, `correo`, `telefono` privados y validados.

**Parte 3** – `Servicio(EntidadSistema, ABC)` con `nombre`, `tarifa_base`, `disponible` y los
métodos abstractos `calcular_costo(...)`, `describir()` y `validar_parametros(...)`.
`calcular_costo` admite sobrecarga simulada: `calcular_costo(duracion)`,
`calcular_costo(duracion, impuesto)` y `calcular_costo(duracion, impuesto, descuento)`.

**Parte 4** – `Reserva(cliente, servicio, duracion)` con estado
(`pendiente`, `confirmada`, `cancelada`, `procesada`) y los métodos
`confirmar()`, `cancelar()` y `procesar()`.

**Parte 5** – `simulaciones.ipynb` importa todo desde el paquete `software_fj`
y ejecuta cada operación con `ejecutar_operacion`.

## Cómo ejecutar

```bash
git clone <URL-del-repositorio>
cd software_fj
jupyter notebook simulaciones.ipynb     # o abrirlo en VS Code / Google Colab
```

Solo se usa la biblioteca estándar de Python 3 (`abc`, `logging`, `datetime`).
