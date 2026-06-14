from datetime import datetime
from app import db
from app.models.viaje import Viaje
from app.models.viaje_asiento import ViajeAsiento
from app.models.bus import Bus
from app.models.chofer import Chofer


def listar_viajes():
    return Viaje.query.order_by(Viaje.fecha_viaje.desc(), Viaje.hora_salida.desc()).all()


def obtener_viaje(id_viaje):
    return Viaje.query.get_or_404(id_viaje)


def _parse_fecha(fecha_str):
    return datetime.strptime(fecha_str, "%Y-%m-%d").date()


def _parse_hora(hora_str):
    return datetime.strptime(hora_str, "%H:%M").time()


def crear_viaje(origen, destino, fecha_viaje, hora_salida, precio, id_bus, id_chofer):
    bus = Bus.query.get_or_404(id_bus)

    viaje = Viaje(
        origen=origen.strip(),
        destino=destino.strip(),
        fecha_viaje=_parse_fecha(fecha_viaje),
        hora_salida=_parse_hora(hora_salida),
        precio=precio,
        id_bus=id_bus,
        id_chofer=id_chofer,
    )
    db.session.add(viaje)
    db.session.flush()  # para obtener id_viaje

    # Generar los asientos del viaje a partir de la plantilla de asientos del bus
    for asiento in bus.asientos:
        db.session.add(ViajeAsiento(id_viaje=viaje.id_viaje, id_asiento=asiento.id_asiento, numero=asiento.numero))

    db.session.commit()
    return viaje


def actualizar_viaje(id_viaje, origen, destino, fecha_viaje, hora_salida, precio, id_bus, id_chofer, estado):
    viaje = obtener_viaje(id_viaje)

    if viaje.tiene_ventas:
        raise ValueError("No se puede editar el viaje: ya tiene ventas registradas.")

    bus_cambio = int(id_bus) != viaje.id_bus

    viaje.origen = origen.strip()
    viaje.destino = destino.strip()
    viaje.fecha_viaje = _parse_fecha(fecha_viaje)
    viaje.hora_salida = _parse_hora(hora_salida)
    viaje.precio = precio
    viaje.id_chofer = id_chofer
    viaje.estado = estado

    if bus_cambio:
        viaje.id_bus = id_bus
        # Regenerar asientos del viaje según el nuevo bus
        for va in list(viaje.viaje_asientos):
            db.session.delete(va)
        bus = Bus.query.get_or_404(id_bus)
        for asiento in bus.asientos:
            db.session.add(ViajeAsiento(id_viaje=viaje.id_viaje, id_asiento=asiento.id_asiento, numero=asiento.numero))

    db.session.commit()
    return viaje


def eliminar_viaje(id_viaje):
    viaje = obtener_viaje(id_viaje)
    if viaje.tiene_ventas:
        raise ValueError("No se puede eliminar el viaje: ya tiene ventas registradas.")
    db.session.delete(viaje)
    db.session.commit()
