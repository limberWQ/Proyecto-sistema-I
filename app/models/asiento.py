from app import db


class Asiento(db.Model):
    __tablename__ = "asiento"

    id_asiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.Integer, nullable=False)
    id_bus = db.Column(db.Integer, db.ForeignKey("bus.id_bus"), nullable=False)

    __table_args__ = (db.UniqueConstraint("id_bus", "numero", name="uq_asiento_bus_numero"),)

    def __repr__(self):
        return f"<Asiento {self.numero} (bus {self.id_bus})>"
