from datetime import datetime
from app import db


class Venta(db.Model):
    __tablename__ = "venta"

    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_venta = db.Column(db.DateTime, nullable=False, default=datetime.now)
    id_pasajero = db.Column(db.Integer, db.ForeignKey("pasajero.id_pasajero"), nullable=False)
    id_viaje = db.Column(db.Integer, db.ForeignKey("viaje.id_viaje"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)

    monto = db.Column(db.Numeric(10, 2), nullable=False, default=0)       # total a pagar (suma de detalles activos)
    monto_pagado = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # con cuánto pagó el cliente
    cambio = db.Column(db.Numeric(10, 2), nullable=False, default=0)       # vuelto entregado

    estado = db.Column(db.String(20), nullable=False, default="activa")  # activa | rebajada | anulada

    detalles = db.relationship("VentaDetalle", backref="venta", cascade="all, delete-orphan")
    factura = db.relationship("Factura", backref="venta", uselist=False, cascade="all, delete-orphan")
    usuario = db.relationship("Usuario")

    @property
    def detalles_activos(self):
        return [d for d in self.detalles if d.estado == "activo"]

    def recalcular_monto(self):
        self.monto = sum((d.precio for d in self.detalles_activos), start=0)

    def __repr__(self):
        return f"<Venta {self.id_venta} viaje={self.id_viaje}>"
