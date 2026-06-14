from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.utils.auth import login_required
from app.services import venta_service, viaje_service
from app.models.viaje import Viaje
from app.models.viaje_asiento import ViajeAsiento
from app.utils.helpers import to_float

ventas_bp = Blueprint("ventas", __name__, url_prefix="/ventas")


@ventas_bp.route("/")
@login_required
def listar():
    ventas = venta_service.listar_ventas()
    return render_template("ventas/listar.html", ventas=ventas)


@ventas_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    viajes = [v for v in viaje_service.listar_viajes() if v.estado == "programado"]

    if request.method == "POST":
        try:
            id_viaje = int(request.form["id_viaje"])
            ids_asiento = request.form.getlist("asientos")
            ids_asiento = [int(a) for a in ids_asiento]

            ci = request.form["ci"]
            nombres = request.form["nombres"]
            apellidos = request.form["apellidos"]
            telefono = request.form.get("telefono", "")
            monto_pagado = to_float(request.form["monto_pagado"])

            if not ci.strip() or not nombres.strip() or not apellidos.strip():
                raise ValueError("CI, nombres y apellidos del pasajero son obligatorios.")

            datos_pasajero = {"ci": ci, "nombres": nombres, "apellidos": apellidos, "telefono": telefono}

            venta = venta_service.registrar_venta(
                id_viaje, ids_asiento, datos_pasajero, monto_pagado, session["id_usuario"]
            )
            flash(
                f"Venta registrada correctamente. Total: Bs {venta.monto} | "
                f"Pagado: Bs {venta.monto_pagado} | Cambio: Bs {venta.cambio}",
                "success",
            )
            return redirect(url_for("ventas.detalle", id_venta=venta.id_venta))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("Ocurrió un error al registrar la venta. Verifica los datos.", "danger")

    return render_template("ventas/crear.html", viajes=viajes)


@ventas_bp.route("/asientos/<int:id_viaje>")
@login_required
def asientos_disponibles(id_viaje):
    """Devuelve en JSON los asientos del viaje (disponibles/ocupados) y el precio."""
    viaje = Viaje.query.get_or_404(id_viaje)
    asientos = (
        ViajeAsiento.query.filter_by(id_viaje=id_viaje)
        .order_by(ViajeAsiento.numero)
        .all()
    )
    data = [{"id_viaje_asiento": va.id_viaje_asiento, "numero": va.numero, "ocupado": va.ocupado} for va in asientos]
    return jsonify({"precio": float(viaje.precio), "asientos": data})


@ventas_bp.route("/<int:id_venta>")
@login_required
def detalle(id_venta):
    venta = venta_service.obtener_venta(id_venta)
    return render_template("ventas/detalle.html", venta=venta)


@ventas_bp.route("/<int:id_venta>/rebajar/<int:id_venta_detalle>", methods=["POST"])
@login_required
def rebajar(id_venta, id_venta_detalle):
    motivo = request.form.get("motivo", "Rebaja de asiento").strip() or "Rebaja de asiento"
    try:
        venta_service.rebajar_asiento(id_venta, id_venta_detalle, session["id_usuario"], motivo)
        flash("Asiento rebajado correctamente. Se registró el egreso en caja.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("ventas.detalle", id_venta=id_venta))


@ventas_bp.route("/<int:id_venta>/anular", methods=["POST"])
@login_required
def anular(id_venta):
    motivo = request.form.get("motivo", "Anulación de venta").strip() or "Anulación de venta"
    try:
        venta_service.anular_venta(id_venta, session["id_usuario"], motivo)
        flash("Venta anulada correctamente. Se liberaron los asientos y se registró el egreso en caja.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("ventas.detalle", id_venta=id_venta))
