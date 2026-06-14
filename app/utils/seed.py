from app import db
from app.models.usuario import Usuario


def seed_admin():
    """Crea un usuario administrador por defecto si no existe ningún usuario."""
    if Usuario.query.first() is None:
        admin = Usuario(usuario="admin", nombre="Administrador", rol="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        encargado = Usuario(usuario="encargado", nombre="Encargado de Ventas", rol="encargado")
        encargado.set_password("encargado123")
        db.session.add(encargado)

        db.session.commit()
