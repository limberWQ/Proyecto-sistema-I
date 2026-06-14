from app import db
from app.models.factura import Factura
from app.utils.helpers import generar_nro_factura


def listar_facturas():
    return Factura.query.order_by(Factura.id_factura.desc()).all()


def obtener_factura(id_factura):
    return Factura.query.get_or_404(id_factura)


def obtener_factura_por_venta(id_venta):
    return Factura.query.filter_by(id_venta=id_venta).first()


def generar_factura(venta):
    """Crea la factura asociada a una venta recién registrada."""
    factura = Factura(
        nro_factura=generar_nro_factura(),
        total=venta.monto,
        id_venta=venta.id_venta,
    )
    db.session.add(factura)
    return factura
