from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_object="config.Config"):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_object)

    db.init_app(app)

    # Importar todos los modelos para que SQLAlchemy los registre antes de create_all
    from app.models import (
        usuario, bus, chofer, asiento, viaje, viaje_asiento,
        pasajero, venta, venta_detalle, factura, movimiento_caja,
    )

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.buses import buses_bp
    from app.routes.choferes import choferes_bp
    from app.routes.viajes import viajes_bp
    from app.routes.pasajeros import pasajeros_bp
    from app.routes.ventas import ventas_bp
    from app.routes.facturas import facturas_bp
    from app.routes.caja import caja_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(buses_bp)
    app.register_blueprint(choferes_bp)
    app.register_blueprint(viajes_bp)
    app.register_blueprint(pasajeros_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(caja_bp)

    with app.app_context():
        db.create_all()
        from app.utils.seed import seed_admin
        seed_admin()

    return app
