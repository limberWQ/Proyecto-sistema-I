from datetime import date, time
from app import db


class Viaje(db.Model):
    __tablename__ = "viaje"

    id_viaje = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origen = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    fecha_viaje = db.Column(db.Date, nullable=False)
    hora_salida = db.Column(db.Time, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    id_bus = db.Column(db.Integer, db.ForeignKey("bus.id_bus"), nullable=False)
    id_chofer = db.Column(db.Integer, db.ForeignKey("chofer.id_chofer"), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="programado")  # programado | finalizado | cancelado

    viaje_asientos = db.relationship("ViajeAsiento", backref="viaje", cascade="all, delete-orphan")
    ventas = db.relationship("Venta", backref="viaje")

    @property
    def tiene_ventas(self):
        """True si el viaje tiene al menos una venta activa (no anulada)."""
        return any(v.estado != "anulada" for v in self.ventas)

    @property
    def asientos_ocupados(self):
        return sum(1 for va in self.viaje_asientos if va.ocupado)

    @property
    def asientos_disponibles(self):
        return len(self.viaje_asientos) - self.asientos_ocupados

    def __repr__(self):
        return f"<Viaje {self.origen}->{self.destino} {self.fecha_viaje}>"
