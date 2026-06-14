from datetime import date
from app import db


class Factura(db.Model):
    __tablename__ = "factura"

    id_factura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nro_factura = db.Column(db.String(30), nullable=False, unique=True)
    fecha_emision = db.Column(db.Date, nullable=False, default=date.today)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    id_venta = db.Column(db.Integer, db.ForeignKey("venta.id_venta"), nullable=False, unique=True)

    def __repr__(self):
        return f"<Factura {self.nro_factura}>"
