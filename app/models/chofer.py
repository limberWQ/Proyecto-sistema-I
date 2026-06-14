from app import db


class Chofer(db.Model):
    __tablename__ = "chofer"

    id_chofer = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ci = db.Column(db.String(20), nullable=False, unique=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    licencia = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(20))
    activo = db.Column(db.Boolean, nullable=False, default=True)

    viajes = db.relationship("Viaje", backref="chofer")

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def __repr__(self):
        return f"<Chofer {self.ci}>"
