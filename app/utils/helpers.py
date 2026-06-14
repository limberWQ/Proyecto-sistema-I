from datetime import datetime


def generar_nro_factura():
    """Genera un número de factura simple basado en fecha/hora."""
    return "F-" + datetime.now().strftime("%Y%m%d%H%M%S%f")


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
