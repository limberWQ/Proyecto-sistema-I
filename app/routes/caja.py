from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth import login_required
from app.services import caja_service
from app.utils.helpers import to_float

caja_bp = Blueprint("caja", __name__, url_prefix="/caja")


@caja_bp.route("/")
@login_required
def listar():
    movimientos = caja_service.listar_movimientos()
    balance = caja_service.calcular_balance()
    return render_template("caja/listar.html", movimientos=movimientos, balance=balance)


@caja_bp.route("/registrar", methods=["GET", "POST"])
@login_required
def registrar():
    if request.method == "POST":
        try:
            tipo = request.form["tipo"]
            concepto = request.form["concepto"]
            monto = to_float(request.form["monto"])

            if not concepto.strip():
                raise ValueError("El concepto es obligatorio.")
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a 0.")

            caja_service.registrar_movimiento(tipo, concepto, monto, session["id_usuario"])
            flash("Movimiento registrado correctamente.", "success")
            return redirect(url_for("caja.listar"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("caja/registrar.html")
