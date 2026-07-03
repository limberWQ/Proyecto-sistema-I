from flask import Blueprint, render_template, request
from app.utils.auth import staff_required
from app.services import reporte_service

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


def _params(default_periodo="mes"):
    periodo = request.args.get("periodo", default_periodo)
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    return periodo, fecha_desde, fecha_hasta


@reportes_bp.route("/")
@staff_required
def index():
    return render_template("reportes/index.html")


@reportes_bp.route("/ventas")
@staff_required
def ventas():
    periodo, fd, fh = _params()
    datos = reporte_service.reporte_ventas(periodo, fd, fh)
    return render_template("reportes/ventas.html", **datos)


@reportes_bp.route("/viajes")
@staff_required
def viajes():
    periodo, fd, fh = _params()
    datos = reporte_service.reporte_viajes(periodo, fd, fh)
    return render_template("reportes/viajes.html", **datos)


@reportes_bp.route("/caja")
@staff_required
def caja():
    periodo, fd, fh = _params()
    datos = reporte_service.reporte_caja(periodo, fd, fh)
    return render_template("reportes/caja.html", **datos)


@reportes_bp.route("/pasajeros")
@staff_required
def pasajeros():
    # Es un reporte centrado en el pasajero (no en una fecha puntual), así
    # que por defecto se muestra todo el historial; el usuario puede acotarlo
    # a un período si lo necesita.
    periodo, fd, fh = _params(default_periodo="todo")
    datos = reporte_service.reporte_pasajeros(periodo, fd, fh)
    return render_template("reportes/pasajeros.html", **datos)