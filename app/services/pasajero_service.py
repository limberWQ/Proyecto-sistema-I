from app import db
from app.models.pasajero import Pasajero


def listar_pasajeros():
    return Pasajero.query.order_by(Pasajero.id_pasajero.desc()).all()


def obtener_pasajero(id_pasajero):
    return Pasajero.query.get_or_404(id_pasajero)


def buscar_por_ci(ci):
    return Pasajero.query.filter_by(ci=ci.strip()).first()


def crear_pasajero(ci, nombres, apellidos, telefono):
    pasajero = Pasajero(
        ci=ci.strip(),
        nombres=nombres.strip(),
        apellidos=apellidos.strip(),
        telefono=(telefono or "").strip(),
    )
    db.session.add(pasajero)
    db.session.commit()
    return pasajero


def actualizar_pasajero(id_pasajero, ci, nombres, apellidos, telefono):
    pasajero = obtener_pasajero(id_pasajero)
    pasajero.ci = ci.strip()
    pasajero.nombres = nombres.strip()
    pasajero.apellidos = apellidos.strip()
    pasajero.telefono = (telefono or "").strip()
    db.session.commit()
    return pasajero


def eliminar_pasajero(id_pasajero):
    pasajero = obtener_pasajero(id_pasajero)
    if pasajero.ventas:
        raise ValueError("No se puede eliminar el pasajero: tiene ventas registradas.")
    db.session.delete(pasajero)
    db.session.commit()


def obtener_o_crear_pasajero(ci, nombres, apellidos, telefono):
    pasajero = buscar_por_ci(ci)
    if pasajero:
        # Actualiza datos por si cambiaron
        pasajero.nombres = nombres.strip()
        pasajero.apellidos = apellidos.strip()
        pasajero.telefono = (telefono or "").strip()
        db.session.commit()
        return pasajero
    return crear_pasajero(ci, nombres, apellidos, telefono)
