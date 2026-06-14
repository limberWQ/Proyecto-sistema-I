from app import db
from app.models.chofer import Chofer


def listar_choferes():
    return Chofer.query.order_by(Chofer.id_chofer.desc()).all()


def obtener_chofer(id_chofer):
    return Chofer.query.get_or_404(id_chofer)


def crear_chofer(ci, nombres, apellidos, licencia, telefono):
    chofer = Chofer(
        ci=ci.strip(),
        nombres=nombres.strip(),
        apellidos=apellidos.strip(),
        licencia=licencia.strip(),
        telefono=(telefono or "").strip(),
    )
    db.session.add(chofer)
    db.session.commit()
    return chofer


def actualizar_chofer(id_chofer, ci, nombres, apellidos, licencia, telefono, activo):
    chofer = obtener_chofer(id_chofer)
    chofer.ci = ci.strip()
    chofer.nombres = nombres.strip()
    chofer.apellidos = apellidos.strip()
    chofer.licencia = licencia.strip()
    chofer.telefono = (telefono or "").strip()
    chofer.activo = activo
    db.session.commit()
    return chofer


def eliminar_chofer(id_chofer):
    chofer = obtener_chofer(id_chofer)
    if chofer.viajes:
        raise ValueError("No se puede eliminar el chofer: tiene viajes asociados.")
    db.session.delete(chofer)
    db.session.commit()
