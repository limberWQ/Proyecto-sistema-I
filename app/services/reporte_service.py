from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func
from app import db
from app.models.venta import Venta
from app.models.venta_detalle import VentaDetalle
from app.models.viaje import Viaje
from app.models.pasajero import Pasajero
from app.models.movimiento_caja import MovimientoCaja


PERIODOS_VALIDOS = ("hoy", "semana", "mes", "anio", "todo", "personalizado")


def _rango_fechas(periodo, fecha_desde=None, fecha_hasta=None):
    """Calcula el rango de fechas según el período seleccionado.

    Devuelve (inicio, fin). Cuando el período es "todo", devuelve
    (None, None) para indicar "sin límite de fechas": es la propia
    lógica de cada reporte la que decide no filtrar, en vez de
    inventar una fecha mínima arbitraria.
    """
    hoy = date.today()
    if periodo == "hoy":
        return hoy, hoy
    elif periodo == "semana":
        inicio = hoy - timedelta(days=hoy.weekday())
        return inicio, hoy
    elif periodo == "mes":
        return hoy.replace(day=1), hoy
    elif periodo == "anio":
        return hoy.replace(month=1, day=1), hoy
    elif periodo == "todo":
        return None, None
    elif periodo == "personalizado" and fecha_desde and fecha_hasta:
        return (
            datetime.strptime(fecha_desde, "%Y-%m-%d").date(),
            datetime.strptime(fecha_hasta, "%Y-%m-%d").date(),
        )
    return hoy.replace(day=1), hoy


# ── Reporte de Ventas ──────────────────────────────────────────────────────────

def reporte_ventas(periodo, fecha_desde=None, fecha_hasta=None):
    inicio, fin = _rango_fechas(periodo, fecha_desde, fecha_hasta)

    query = Venta.query
    if inicio and fin:
        query = query.filter(
            func.date(Venta.fecha_venta) >= inicio,
            func.date(Venta.fecha_venta) <= fin,
        )
    ventas = query.order_by(Venta.fecha_venta.desc()).all()

    total_activas = sum(
        Decimal(str(v.monto)) for v in ventas if v.estado != "anulada"
    )
    total_anuladas = sum(
        1 for v in ventas if v.estado == "anulada"
    )
    total_boletos = sum(
        len(v.detalles_activos) for v in ventas if v.estado != "anulada"
    )

    return {
        "ventas": ventas,
        "total_ingresos": total_activas,
        "total_anuladas": total_anuladas,
        "total_boletos": total_boletos,
        "inicio": inicio,
        "fin": fin,
        "periodo": periodo,
    }


# ── Reporte de Viajes ──────────────────────────────────────────────────────────

def reporte_viajes(periodo, fecha_desde=None, fecha_hasta=None):
    inicio, fin = _rango_fechas(periodo, fecha_desde, fecha_hasta)

    query = Viaje.query
    if inicio and fin:
        query = query.filter(
            Viaje.fecha_viaje >= inicio,
            Viaje.fecha_viaje <= fin,
        )
    viajes = query.order_by(Viaje.fecha_viaje.desc()).all()

    # Enriquecer con datos de ventas
    datos = []
    for v in viajes:
        ventas_activas = [vt for vt in v.ventas if vt.estado != "anulada"]
        boletos = sum(len(vt.detalles_activos) for vt in ventas_activas)
        recaudado = sum(Decimal(str(vt.monto)) for vt in ventas_activas)
        ocupacion = (
            round(boletos / len(v.viaje_asientos) * 100, 1)
            if v.viaje_asientos else 0
        )
        datos.append({
            "viaje": v,
            "boletos_vendidos": boletos,
            "capacidad": len(v.viaje_asientos),
            "ocupacion_pct": ocupacion,
            "recaudado": recaudado,
        })

    # Ordenar por boletos vendidos (más populares primero)
    datos.sort(key=lambda x: x["boletos_vendidos"], reverse=True)

    total_viajes = len(viajes)
    total_boletos = sum(d["boletos_vendidos"] for d in datos)
    total_recaudado = sum(d["recaudado"] for d in datos)

    return {
        "datos": datos,
        "total_viajes": total_viajes,
        "total_boletos": total_boletos,
        "total_recaudado": total_recaudado,
        "inicio": inicio,
        "fin": fin,
        "periodo": periodo,
    }


# ── Reporte de Caja ────────────────────────────────────────────────────────────

def reporte_caja(periodo, fecha_desde=None, fecha_hasta=None):
    inicio, fin = _rango_fechas(periodo, fecha_desde, fecha_hasta)

    query = MovimientoCaja.query
    if inicio and fin:
        query = query.filter(
            func.date(MovimientoCaja.fecha) >= inicio,
            func.date(MovimientoCaja.fecha) <= fin,
        )
    movimientos = query.order_by(MovimientoCaja.fecha.desc()).all()

    total_ingresos = sum(
        Decimal(str(m.monto)) for m in movimientos if m.tipo == "ingreso"
    )
    total_egresos = sum(
        Decimal(str(m.monto)) for m in movimientos if m.tipo == "egreso"
    )
    saldo = total_ingresos - total_egresos

    return {
        "movimientos": movimientos,
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "saldo": saldo,
        "inicio": inicio,
        "fin": fin,
        "periodo": periodo,
    }


# ── Reporte de Pasajeros ───────────────────────────────────────────────────────

def reporte_pasajeros(periodo, fecha_desde=None, fecha_hasta=None):
    inicio, fin = _rango_fechas(periodo, fecha_desde, fecha_hasta)

    # Pasajeros que tuvieron su PRIMERA compra en el período
    # (se consideran "nuevos" si su venta más antigua cae en el rango)
    subquery = (
        db.session.query(
            Venta.id_pasajero,
            func.min(func.date(Venta.fecha_venta)).label("primera_compra"),
        )
        .group_by(Venta.id_pasajero)
        .subquery()
    )

    nuevos_q = (
        db.session.query(Pasajero, subquery.c.primera_compra)
        .join(subquery, Pasajero.id_pasajero == subquery.c.id_pasajero)
    )
    if inicio and fin:
        nuevos_q = nuevos_q.filter(
            subquery.c.primera_compra >= str(inicio),
            subquery.c.primera_compra <= str(fin),
        )
    nuevos = nuevos_q.order_by(subquery.c.primera_compra.desc()).all()

    # Pasajeros más frecuentes (en el período, o de todo el historial si no hay rango)
    frecuentes_q = (
        db.session.query(
            Pasajero,
            func.count(Venta.id_venta).label("total_compras"),
            func.sum(Venta.monto).label("total_gastado"),
        )
        .join(Venta, Venta.id_pasajero == Pasajero.id_pasajero)
        .filter(Venta.estado != "anulada")
    )
    if inicio and fin:
        frecuentes_q = frecuentes_q.filter(
            func.date(Venta.fecha_venta) >= inicio,
            func.date(Venta.fecha_venta) <= fin,
        )
    frecuentes = (
        frecuentes_q
        .group_by(Pasajero.id_pasajero)
        .order_by(func.count(Venta.id_venta).desc())
        .limit(10)
        .all()
    )

    return {
        "nuevos": nuevos,
        "frecuentes": frecuentes,
        "total_nuevos": len(nuevos),
        "inicio": inicio,
        "fin": fin,
        "periodo": periodo,
    }