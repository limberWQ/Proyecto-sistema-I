from datetime import datetime
from sqlalchemy import and_

from app import db
from app.models.viaje import Viaje
from app.models.viaje_asiento import ViajeAsiento
from app.models.bus import Bus
from app.models.chofer import Chofer


def listar_viajes():
    return Viaje.query.order_by(
        Viaje.fecha_viaje.desc(),
        Viaje.hora_salida.desc()
    ).all()


def obtener_viaje(id_viaje):
    return Viaje.query.get_or_404(id_viaje)


def filtrar_viaje(fecha=None, origen=None, destino=None, estado=None):
    query = Viaje.query
    filtros = []

    if fecha:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        filtros.append(db.func.date(Viaje.fecha_viaje) == fecha_obj)

    if estado:
        filtros.append(Viaje.estado == estado)

    if origen:
        filtros.append(Viaje.origen == origen)

    if destino:
        filtros.append(Viaje.destino == destino)

    if filtros:
        query = query.filter(and_(*filtros))

    return query.all()


def _parse_fecha(fecha_str):
    return datetime.strptime(fecha_str, "%Y-%m-%d").date()


def _parse_hora(hora_str):
    return datetime.strptime(hora_str, "%H:%M").time()


def _validar_disponibilidad(id_bus, id_chofer, fecha_viaje, excluir_id_viaje=None):
    """
    Un bus y un chofer solo pueden estar asignados a UN viaje por día
    (los viajes interdepartamentales duran varias horas, así que no
    tiene sentido permitir dos viajes el mismo día para el mismo
    bus/chofer). Valida que ambos estén activos y libres esa fecha.
    """
    bus = Bus.query.get(id_bus)
    if bus is None:
        raise ValueError("El bus seleccionado no existe.")
    if not bus.activo:
        raise ValueError(
            f"El bus {bus.placa} está marcado como inactivo y no puede "
            f"ser asignado a un viaje. Actívalo primero desde el módulo de Buses."
        )

    chofer = Chofer.query.get(id_chofer)
    if chofer is None:
        raise ValueError("El chofer seleccionado no existe.")
    if not chofer.activo:
        raise ValueError(
            f"El chofer {chofer.nombre_completo} está marcado como inactivo "
            f"y no puede ser asignado a un viaje. Actívalo primero desde el módulo de Choferes."
        )

    query = Viaje.query.filter(
        Viaje.fecha_viaje == fecha_viaje,
        Viaje.estado != "cancelado",
    )
    if excluir_id_viaje:
        query = query.filter(Viaje.id_viaje != excluir_id_viaje)

    for v in query.all():
        if v.id_bus == int(id_bus):
            raise ValueError(
                f"El bus {bus.placa} ya está asignado al viaje "
                f"{v.origen} → {v.destino} el {v.fecha_viaje.strftime('%d/%m/%Y')} "
                f"a las {v.hora_salida.strftime('%H:%M')}. Un bus solo puede tener "
                f"un viaje por día."
            )
        if v.id_chofer == int(id_chofer):
            raise ValueError(
                f"El chofer {chofer.nombre_completo} ya está asignado al viaje "
                f"{v.origen} → {v.destino} el {v.fecha_viaje.strftime('%d/%m/%Y')} "
                f"a las {v.hora_salida.strftime('%H:%M')}. Un chofer solo puede tener "
                f"un viaje por día."
            )


def buses_y_choferes_ocupados(fecha_viaje, excluir_id_viaje=None):
    """
    Devuelve (ids_bus_ocupados, ids_chofer_ocupados) para una fecha dada,
    usado por el formulario para deshabilitar opciones ya asignadas
    antes de que el usuario intente enviar el formulario.
    """
    query = Viaje.query.filter(
        Viaje.fecha_viaje == fecha_viaje,
        Viaje.estado != "cancelado",
    )
    if excluir_id_viaje:
        query = query.filter(Viaje.id_viaje != excluir_id_viaje)

    ids_bus = set()
    ids_chofer = set()
    for v in query.all():
        ids_bus.add(v.id_bus)
        ids_chofer.add(v.id_chofer)

    return ids_bus, ids_chofer


def crear_viaje(origen, destino, fecha_viaje, hora_salida, precio, id_bus, id_chofer):
    fecha = _parse_fecha(fecha_viaje)
    hora = _parse_hora(hora_salida)

    _validar_disponibilidad(id_bus, id_chofer, fecha)

    bus = Bus.query.get_or_404(id_bus)

    viaje = Viaje(
        origen=origen.strip(),
        destino=destino.strip(),
        fecha_viaje=fecha,
        hora_salida=hora,
        precio=precio,
        id_bus=id_bus,
        id_chofer=id_chofer,
    )

    db.session.add(viaje)
    db.session.flush()

    # Generar los asientos del viaje
    for asiento in bus.asientos:
        db.session.add(
            ViajeAsiento(
                id_viaje=viaje.id_viaje,
                id_asiento=asiento.id_asiento,
                numero=asiento.numero
            )
        )

    db.session.commit()
    return viaje


def actualizar_viaje(
    id_viaje,
    origen,
    destino,
    fecha_viaje,
    hora_salida,
    precio,
    id_bus,
    id_chofer,
    estado,
):
    viaje = obtener_viaje(id_viaje)

    if viaje.tiene_ventas:
        raise ValueError(
            "No se puede editar el viaje: ya tiene ventas registradas."
        )

    fecha = _parse_fecha(fecha_viaje)
    hora = _parse_hora(hora_salida)

    _validar_disponibilidad(
        id_bus,
        id_chofer,
        fecha,
        excluir_id_viaje=id_viaje
    )

    bus_cambio = int(id_bus) != viaje.id_bus

    viaje.origen = origen.strip()
    viaje.destino = destino.strip()
    viaje.fecha_viaje = fecha
    viaje.hora_salida = hora
    viaje.precio = precio
    viaje.id_chofer = id_chofer
    viaje.estado = estado

    if bus_cambio:
        viaje.id_bus = id_bus

        # Regenerar los asientos del viaje según el nuevo bus
        for va in list(viaje.viaje_asientos):
            db.session.delete(va)

        bus = Bus.query.get_or_404(id_bus)

        for asiento in bus.asientos:
            db.session.add(
                ViajeAsiento(
                    id_viaje=viaje.id_viaje,
                    id_asiento=asiento.id_asiento,
                    numero=asiento.numero
                )
            )

    db.session.commit()
    return viaje


def eliminar_viaje(id_viaje):
    viaje = obtener_viaje(id_viaje)

    if viaje.tiene_ventas:
        raise ValueError(
            "No se puede eliminar el viaje: ya tiene ventas registradas."
        )

    db.session.delete(viaje)
    db.session.commit()