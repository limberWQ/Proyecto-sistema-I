from app import db


class Pasajero(db.Model):
    __tablename__ = "pasajero"

    id_pasajero = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ci = db.Column(db.String(20), nullable=False, unique=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))

    ventas = db.relationship("Venta", backref="pasajero")

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def __repr__(self):
        return f"<Pasajero {self.ci}>"
