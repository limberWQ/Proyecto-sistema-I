from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import login_required
from app.services import pasajero_service

pasajeros_bp = Blueprint("pasajeros", __name__, url_prefix="/pasajeros")


@pasajeros_bp.route("/")
@login_required
def listar():
    pasajeros = pasajero_service.listar_pasajeros()
    return render_template("pasajeros/listar.html", pasajeros=pasajeros)


@pasajeros_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        try:
            ci = request.form["ci"]
            nombres = request.form["nombres"]
            apellidos = request.form["apellidos"]
            telefono = request.form.get("telefono", "")

            if not ci.strip() or not nombres.strip() or not apellidos.strip():
                raise ValueError("CI, nombres y apellidos son obligatorios.")

            pasajero_service.crear_pasajero(ci, nombres, apellidos, telefono)
            flash("Pasajero registrado correctamente.", "success")
            return redirect(url_for("pasajeros.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("El CI ya existe o los datos son inválidos.", "danger")

    return render_template("pasajeros/crear.html")


@pasajeros_bp.route("/editar/<int:id_pasajero>", methods=["GET", "POST"])
@login_required
def editar(id_pasajero):
    pasajero = pasajero_service.obtener_pasajero(id_pasajero)

    if request.method == "POST":
        try:
            ci = request.form["ci"]
            nombres = request.form["nombres"]
            apellidos = request.form["apellidos"]
            telefono = request.form.get("telefono", "")

            if not ci.strip() or not nombres.strip() or not apellidos.strip():
                raise ValueError("CI, nombres y apellidos son obligatorios.")

            pasajero_service.actualizar_pasajero(id_pasajero, ci, nombres, apellidos, telefono)
            flash("Pasajero actualizado correctamente.", "success")
            return redirect(url_for("pasajeros.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("El CI ya existe o los datos son inválidos.", "danger")

    return render_template("pasajeros/editar.html", pasajero=pasajero)


@pasajeros_bp.route("/eliminar/<int:id_pasajero>", methods=["POST"])
@login_required
def eliminar(id_pasajero):
    try:
        pasajero_service.eliminar_pasajero(id_pasajero)
        flash("Pasajero eliminado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("pasajeros.listar"))
