from app import db


class Bus(db.Model):
    __tablename__ = "bus"

    id_bus = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placa = db.Column(db.String(20), nullable=False, unique=True)
    modelo = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    asientos = db.relationship("Asiento", backref="bus", cascade="all, delete-orphan")
    viajes = db.relationship("Viaje", backref="bus")

    def generar_asientos(self):
        """Crea los asientos del bus según su capacidad (1..capacidad)."""
        from app.models.asiento import Asiento
        for n in range(1, self.capacidad + 1):
            self.asientos.append(Asiento(numero=n))

    def __repr__(self):
        return f"<Bus {self.placa}>"
