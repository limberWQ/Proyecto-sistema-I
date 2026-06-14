from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import login_required
from app.services import chofer_service

choferes_bp = Blueprint("choferes", __name__, url_prefix="/choferes")


@choferes_bp.route("/")
@login_required
def listar():
    choferes = chofer_service.listar_choferes()
    return render_template("choferes/listar.html", choferes=choferes)


@choferes_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        try:
            ci = request.form["ci"]
            nombres = request.form["nombres"]
            apellidos = request.form["apellidos"]
            licencia = request.form["licencia"]
            telefono = request.form.get("telefono", "")

            if not ci.strip() or not nombres.strip() or not apellidos.strip() or not licencia.strip():
                raise ValueError("CI, nombres, apellidos y licencia son obligatorios.")

            chofer_service.crear_chofer(ci, nombres, apellidos, licencia, telefono)
            flash("Chofer registrado correctamente.", "success")
            return redirect(url_for("choferes.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("El CI ya existe o los datos son inválidos.", "danger")

    return render_template("choferes/crear.html")


@choferes_bp.route("/editar/<int:id_chofer>", methods=["GET", "POST"])
@login_required
def editar(id_chofer):
    chofer = chofer_service.obtener_chofer(id_chofer)

    if request.method == "POST":
        try:
            ci = request.form["ci"]
            nombres = request.form["nombres"]
            apellidos = request.form["apellidos"]
            licencia = request.form["licencia"]
            telefono = request.form.get("telefono", "")
            activo = request.form.get("activo") == "on"

            if not ci.strip() or not nombres.strip() or not apellidos.strip() or not licencia.strip():
                raise ValueError("CI, nombres, apellidos y licencia son obligatorios.")

            chofer_service.actualizar_chofer(id_chofer, ci, nombres, apellidos, licencia, telefono, activo)
            flash("Chofer actualizado correctamente.", "success")
            return redirect(url_for("choferes.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("El CI ya existe o los datos son inválidos.", "danger")

    return render_template("choferes/editar.html", chofer=chofer)


@choferes_bp.route("/eliminar/<int:id_chofer>", methods=["POST"])
@login_required
def eliminar(id_chofer):
    try:
        chofer_service.eliminar_chofer(id_chofer)
        flash("Chofer eliminado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("choferes.listar"))
