from app import db


class ViajeAsiento(db.Model):
    __tablename__ = "viaje_asiento"

    id_viaje_asiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_viaje = db.Column(db.Integer, db.ForeignKey("viaje.id_viaje"), nullable=False)
    id_asiento = db.Column(db.Integer, db.ForeignKey("asiento.id_asiento"), nullable=False)
    numero = db.Column(db.Integer, nullable=False)  # copia del número de asiento para consulta rápida
    ocupado = db.Column(db.Boolean, nullable=False, default=False)

    asiento = db.relationship("Asiento")
    detalle_venta = db.relationship("VentaDetalle", backref="viaje_asiento", uselist=False)

    __table_args__ = (db.UniqueConstraint("id_viaje", "id_asiento", name="uq_viajeasiento"),)

    def __repr__(self):
        return f"<ViajeAsiento viaje={self.id_viaje} num={self.numero} ocupado={self.ocupado}>"
