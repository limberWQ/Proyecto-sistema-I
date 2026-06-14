from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import login_required
from app.services import viaje_service, bus_service, chofer_service
from app.utils.helpers import to_float

viajes_bp = Blueprint("viajes", __name__, url_prefix="/viajes")


@viajes_bp.route("/")
@login_required
def listar():
    viajes = viaje_service.listar_viajes()
    return render_template("viajes/listar.html", viajes=viajes)


@viajes_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    buses = [b for b in bus_service.listar_buses() if b.activo]
    choferes = [c for c in chofer_service.listar_choferes() if c.activo]

    if request.method == "POST":
        try:
            origen = request.form["origen"]
            destino = request.form["destino"]
            fecha_viaje = request.form["fecha_viaje"]
            hora_salida = request.form["hora_salida"]
            precio = to_float(request.form["precio"])
            id_bus = int(request.form["id_bus"])
            id_chofer = int(request.form["id_chofer"])

            if not origen.strip() or not destino.strip():
                raise ValueError("Origen y destino son obligatorios.")
            if precio <= 0:
                raise ValueError("El precio debe ser mayor a 0.")

            viaje_service.crear_viaje(origen, destino, fecha_viaje, hora_salida, precio, id_bus, id_chofer)
            flash("Viaje registrado correctamente.", "success")
            return redirect(url_for("viajes.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("Datos inválidos. Verifica el formulario.", "danger")

    return render_template("viajes/crear.html", buses=buses, choferes=choferes)


@viajes_bp.route("/editar/<int:id_viaje>", methods=["GET", "POST"])
@login_required
def editar(id_viaje):
    viaje = viaje_service.obtener_viaje(id_viaje)
    buses = bus_service.listar_buses()
    choferes = chofer_service.listar_choferes()

    if viaje.tiene_ventas:
        flash("Este viaje ya tiene ventas registradas y no puede ser editado. Solo se permiten rebajas.", "warning")
        return redirect(url_for("viajes.listar"))

    if request.method == "POST":
        try:
            origen = request.form["origen"]
            destino = request.form["destino"]
            fecha_viaje = request.form["fecha_viaje"]
            hora_salida = request.form["hora_salida"]
            precio = to_float(request.form["precio"])
            id_bus = int(request.form["id_bus"])
            id_chofer = int(request.form["id_chofer"])
            estado = request.form["estado"]

            if not origen.strip() or not destino.strip():
                raise ValueError("Origen y destino son obligatorios.")
            if precio <= 0:
                raise ValueError("El precio debe ser mayor a 0.")

            viaje_service.actualizar_viaje(id_viaje, origen, destino, fecha_viaje, hora_salida, precio, id_bus, id_chofer, estado)
            flash("Viaje actualizado correctamente.", "success")
            return redirect(url_for("viajes.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("Datos inválidos. Verifica el formulario.", "danger")

    return render_template("viajes/editar.html", viaje=viaje, buses=buses, choferes=choferes)


@viajes_bp.route("/eliminar/<int:id_viaje>", methods=["POST"])
@login_required
def eliminar(id_viaje):
    try:
        viaje_service.eliminar_viaje(id_viaje)
        flash("Viaje eliminado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("viajes.listar"))
