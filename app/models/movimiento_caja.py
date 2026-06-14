from datetime import datetime
from app import db


class MovimientoCaja(db.Model):
    __tablename__ = "movimiento_caja"

    id_movimiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tipo = db.Column(db.String(10), nullable=False)  # ingreso | egreso
    concepto = db.Column(db.String(150), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_venta = db.Column(db.Integer, db.ForeignKey("venta.id_venta"), nullable=True)  # si viene de una venta

    usuario = db.relationship("Usuario")
    venta = db.relationship("Venta")

    def __repr__(self):
        return f"<MovimientoCaja {self.tipo} {self.monto}>"
