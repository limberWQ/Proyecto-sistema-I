from app import db


class VentaDetalle(db.Model):
    __tablename__ = "venta_detalle"

    id_venta_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_venta = db.Column(db.Integer, db.ForeignKey("venta.id_venta"), nullable=False)
    id_viaje_asiento = db.Column(db.Integer, db.ForeignKey("viaje_asiento.id_viaje_asiento"), nullable=False, unique=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="activo")  # activo | rebajado (anulado individualmente)

    def __repr__(self):
        return f"<VentaDetalle venta={self.id_venta} asiento_viaje={self.id_viaje_asiento}>"
