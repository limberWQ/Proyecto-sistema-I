from flask import Blueprint, render_template
from app.utils.auth import login_required
from app.services import factura_service

facturas_bp = Blueprint("facturas", __name__, url_prefix="/facturas")


@facturas_bp.route("/")
@login_required
def listar():
    facturas = factura_service.listar_facturas()
    return render_template("facturas/listar.html", facturas=facturas)


@facturas_bp.route("/<int:id_factura>")
@login_required
def detalle(id_factura):
    factura = factura_service.obtener_factura(id_factura)
    return render_template("facturas/detalle.html", factura=factura, venta=factura.venta)
