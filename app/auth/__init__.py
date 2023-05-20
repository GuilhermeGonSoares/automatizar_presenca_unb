from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from .session_controller import bp as sessionbp

auth_bp.register_blueprint(sessionbp)

__all__ = [auth_bp]
