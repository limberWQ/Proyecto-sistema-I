from app import db
from app.models.bus import Bus
from app.models.viaje import Viaje


def listar_buses():
    return Bus.query.order_by(Bus.id_bus.desc()).all()


def obtener_bus(id_bus):
    return Bus.query.get_or_404(id_bus)


def crear_bus(placa, modelo, capacidad):
    bus = Bus(placa=placa.strip().upper(), modelo=modelo.strip(), capacidad=int(capacidad))
    bus.generar_asientos()
    db.session.add(bus)
    db.session.commit()
    return bus


def actualizar_bus(id_bus, placa, modelo, capacidad, activo):
    bus = obtener_bus(id_bus)
    nueva_capacidad = int(capacidad)

    bus.placa = placa.strip().upper()
    bus.modelo = modelo.strip()
    bus.activo = activo

    if nueva_capacidad != bus.capacidad:
        # Solo se permite cambiar la capacidad si el bus no tiene viajes con ventas
        if bus_tiene_viajes_con_ventas(bus):
            raise ValueError("No se puede cambiar la capacidad: el bus tiene viajes con ventas registradas.")
        # Regenerar asientos
        for asiento in list(bus.asientos):
            db.session.delete(asiento)
        bus.capacidad = nueva_capacidad
        bus.generar_asientos()

    db.session.commit()
    return bus


def bus_tiene_viajes_con_ventas(bus):
    for viaje in bus.viajes:
        if viaje.tiene_ventas:
            return True
    return False


def eliminar_bus(id_bus):
    bus = obtener_bus(id_bus)
    if bus.viajes:
        raise ValueError("No se puede eliminar el bus: tiene viajes asociados.")
    db.session.delete(bus)
    db.session.commit()
