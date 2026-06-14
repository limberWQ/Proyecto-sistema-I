from datetime import date
from flask import Blueprint, render_template
from app.utils.auth import login_required
from app.models.viaje import Viaje
from app.models.venta import Venta
from app.models.bus import Bus
from app.models.chofer import Chofer
from app.models.pasajero import Pasajero
from app.services import caja_service

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    viajes_hoy = Viaje.query.filter_by(fecha_viaje=date.today()).order_by(Viaje.hora_salida).all()

    total_ventas_activas = Venta.query.filter(Venta.estado != "anulada").count()
    total_buses = Bus.query.count()
    total_choferes = Chofer.query.count()
    total_pasajeros = Pasajero.query.count()

    balance = caja_service.calcular_balance()

    ultimas_ventas = Venta.query.order_by(Venta.id_venta.desc()).limit(5).all()

    return render_template(
        "dashboard/index.html",
        viajes_hoy=viajes_hoy,
        total_ventas_activas=total_ventas_activas,
        total_buses=total_buses,
        total_choferes=total_choferes,
        total_pasajeros=total_pasajeros,
        balance=balance,
        ultimas_ventas=ultimas_ventas,
    )
