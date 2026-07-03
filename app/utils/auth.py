from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(view_func):
    """Exige solamente una sesión activa (cualquier rol)."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "id_usuario" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Exige sesión activa con rol administrativo (admin o encargado)."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "id_usuario" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("rol") not in ("admin", "encargado"):
            flash("No tienes permisos para acceder a esta sección.", "danger")
            return redirect(url_for("dashboard.index"))
        return view_func(*args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Exige sesión activa exclusivamente con rol administrador."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "id_usuario" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("rol") != "admin":
            flash("No tienes permisos para acceder a esta sección.", "danger")
            return redirect(url_for("dashboard.index"))
        return view_func(*args, **kwargs)
    return wrapper