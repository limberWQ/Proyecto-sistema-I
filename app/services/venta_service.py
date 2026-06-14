from decimal import Decimal
from app import db
from app.models.venta import Venta
from app.models.venta_detalle import VentaDetalle
from app.models.viaje_asiento import ViajeAsiento
from app.models.viaje import Viaje
from app.models.movimiento_caja import MovimientoCaja
from app.services import pasajero_service
from app.services.factura_service import generar_factura


def listar_ventas():
    return Venta.query.order_by(Venta.id_venta.desc()).all()


def obtener_venta(id_venta):
    return Venta.query.get_or_404(id_venta)


def registrar_venta(id_viaje, ids_viaje_asiento, datos_pasajero, monto_pagado, id_usuario):
    """
    Registra una venta con uno o varios asientos.

    ids_viaje_asiento: lista de IDs de ViajeAsiento (asientos del viaje) a vender.
    datos_pasajero: dict con ci, nombres, apellidos, telefono.
    monto_pagado: monto entregado por el cliente (para calcular el cambio).
    """
    viaje = Viaje.query.get_or_404(id_viaje)

    if not ids_viaje_asiento:
        raise ValueError("Debe seleccionar al menos un asiento.")

    # Validar disponibilidad de los asientos seleccionados
    viaje_asientos = []
    for id_va in ids_viaje_asiento:
        va = ViajeAsiento.query.get(id_va)
        if va is None or va.id_viaje != viaje.id_viaje:
            raise ValueError("Asiento inválido para este viaje.")
        if va.ocupado:
            raise ValueError(f"El asiento {va.numero} ya está ocupado.")
        viaje_asientos.append(va)

    pasajero = pasajero_service.obtener_o_crear_pasajero(
        datos_pasajero["ci"], datos_pasajero["nombres"], datos_pasajero["apellidos"], datos_pasajero.get("telefono")
    )

    precio_unitario = Decimal(str(viaje.precio))
    total = precio_unitario * len(viaje_asientos)

    monto_pagado = Decimal(str(monto_pagado))
    if monto_pagado < total:
        raise ValueError(
            f"El monto pagado (Bs {monto_pagado}) es menor al total a pagar (Bs {total})."
        )
    cambio = monto_pagado - total

    venta = Venta(
        id_pasajero=pasajero.id_pasajero,
        id_viaje=viaje.id_viaje,
        id_usuario=id_usuario,
        monto=total,
        monto_pagado=monto_pagado,
        cambio=cambio,
        estado="activa",
    )
    db.session.add(venta)
    db.session.flush()

    for va in viaje_asientos:
        va.ocupado = True
        detalle = VentaDetalle(
            id_venta=venta.id_venta,
            id_viaje_asiento=va.id_viaje_asiento,
            precio=precio_unitario,
            estado="activo",
        )
        db.session.add(detalle)

    # Registrar ingreso en caja
    movimiento = MovimientoCaja(
        tipo="ingreso",
        concepto=f"Venta de boletos - Viaje {viaje.origen} -> {viaje.destino} ({viaje.fecha_viaje})",
        monto=total,
        id_usuario=id_usuario,
        id_venta=venta.id_venta,
    )
    db.session.add(movimiento)

    db.session.flush()

    # Generar factura automáticamente
    generar_factura(venta)

    db.session.commit()
    return venta


def rebajar_asiento(id_venta, id_venta_detalle, id_usuario, motivo="Rebaja de asiento"):
    """
    Anula un asiento dentro de una venta (rebaja parcial).
    Libera el asiento del viaje, recalcula el total de la venta/factura
    y registra un egreso en caja por el monto devuelto.
    """
    venta = obtener_venta(id_venta)
    detalle = VentaDetalle.query.get_or_404(id_venta_detalle)

    if detalle.id_venta != venta.id_venta:
        raise ValueError("El detalle no corresponde a esta venta.")
    if detalle.estado != "activo":
        raise ValueError("Este asiento ya fue rebajado anteriormente.")

    if len(venta.detalles_activos) <= 1:
        raise ValueError(
            "No se puede rebajar el último asiento de la venta. Anule la venta completa si corresponde."
        )

    monto_rebaja = Decimal(str(detalle.precio))

    detalle.estado = "rebajado"

    # Liberar el asiento del viaje
    va = ViajeAsiento.query.get(detalle.id_viaje_asiento)
    if va:
        va.ocupado = False

    # Recalcular el total de la venta
    venta.recalcular_monto()
    venta.estado = "rebajada"

    # Recalcular cambio (si el monto pagado ahora supera el nuevo total)
    nuevo_pagado = Decimal(str(venta.monto_pagado)) - monto_rebaja
    if nuevo_pagado < 0:
        nuevo_pagado = Decimal("0")
    venta.monto_pagado = nuevo_pagado
    venta.cambio = max(Decimal("0"), nuevo_pagado - Decimal(str(venta.monto)))

    # Actualizar el total de la factura asociada
    if venta.factura:
        venta.factura.total = venta.monto

    # Registrar egreso en caja por la devolución
    movimiento = MovimientoCaja(
        tipo="egreso",
        concepto=f"Rebaja/devolución asiento #{va.numero if va else ''} - Venta {venta.id_venta}: {motivo}",
        monto=monto_rebaja,
        id_usuario=id_usuario,
        id_venta=venta.id_venta,
    )
    db.session.add(movimiento)

    db.session.commit()
    return venta


def anular_venta(id_venta, id_usuario, motivo="Anulación de venta"):
    """Anula la venta completa: libera todos los asientos y registra el egreso total."""
    venta = obtener_venta(id_venta)

    if venta.estado == "anulada":
        raise ValueError("La venta ya está anulada.")

    monto_total = Decimal(str(venta.monto))

    for detalle in venta.detalles_activos:
        detalle.estado = "rebajado"
        va = ViajeAsiento.query.get(detalle.id_viaje_asiento)
        if va:
            va.ocupado = False

    venta.estado = "anulada"
    venta.monto = Decimal("0")
    venta.monto_pagado = Decimal("0")
    venta.cambio = Decimal("0")

    if venta.factura:
        venta.factura.total = Decimal("0")

    movimiento = MovimientoCaja(
        tipo="egreso",
        concepto=f"Anulación de venta {venta.id_venta}: {motivo}",
        monto=monto_total,
        id_usuario=id_usuario,
        id_venta=venta.id_venta,
    )
    db.session.add(movimiento)

    db.session.commit()
    return venta
