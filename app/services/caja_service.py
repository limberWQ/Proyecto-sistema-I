from decimal import Decimal
from app import db
from app.models.movimiento_caja import MovimientoCaja


def listar_movimientos():
    return MovimientoCaja.query.order_by(MovimientoCaja.id_movimiento.desc()).all()


def registrar_movimiento(tipo, concepto, monto, id_usuario):
    if tipo not in ("ingreso", "egreso"):
        raise ValueError("Tipo de movimiento inválido.")
    monto = Decimal(str(monto))
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0.")

    movimiento = MovimientoCaja(
        tipo=tipo,
        concepto=concepto.strip(),
        monto=monto,
        id_usuario=id_usuario,
    )
    db.session.add(movimiento)
    db.session.commit()
    return movimiento


def calcular_balance():
    movimientos = listar_movimientos()
    total_ingresos = sum((Decimal(str(m.monto)) for m in movimientos if m.tipo == "ingreso"), start=Decimal("0"))
    total_egresos = sum((Decimal(str(m.monto)) for m in movimientos if m.tipo == "egreso"), start=Decimal("0"))
    return {
        "ingresos": total_ingresos,
        "egresos": total_egresos,
        "saldo": total_ingresos - total_egresos,
    }
