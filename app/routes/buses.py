from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import login_required
from app.services import bus_service

buses_bp = Blueprint("buses", __name__, url_prefix="/buses")


@buses_bp.route("/")
@login_required
def listar():
    buses = bus_service.listar_buses()
    return render_template("buses/listar.html", buses=buses)


@buses_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        try:
            placa = request.form["placa"]
            modelo = request.form["modelo"]
            capacidad = request.form["capacidad"]

            if not placa.strip() or not modelo.strip():
                raise ValueError("Placa y modelo son obligatorios.")
            if int(capacidad) <= 0:
                raise ValueError("La capacidad debe ser mayor a 0.")

            bus_service.crear_bus(placa, modelo, capacidad)
            flash("Bus registrado correctamente.", "success")
            return redirect(url_for("buses.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("La placa ya existe o los datos son inválidos.", "danger")

    return render_template("buses/crear.html")


@buses_bp.route("/editar/<int:id_bus>", methods=["GET", "POST"])
@login_required
def editar(id_bus):
    bus = bus_service.obtener_bus(id_bus)

    if request.method == "POST":
        try:
            placa = request.form["placa"]
            modelo = request.form["modelo"]
            capacidad = request.form["capacidad"]
            activo = request.form.get("activo") == "on"

            if not placa.strip() or not modelo.strip():
                raise ValueError("Placa y modelo son obligatorios.")
            if int(capacidad) <= 0:
                raise ValueError("La capacidad debe ser mayor a 0.")

            bus_service.actualizar_bus(id_bus, placa, modelo, capacidad, activo)
            flash("Bus actualizado correctamente.", "success")
            return redirect(url_for("buses.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("La placa ya existe o los datos son inválidos.", "danger")

    return render_template("buses/editar.html", bus=bus)


@buses_bp.route("/eliminar/<int:id_bus>", methods=["POST"])
@login_required
def eliminar(id_bus):
    try:
        bus_service.eliminar_bus(id_bus)
        flash("Bus eliminado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("buses.listar"))
