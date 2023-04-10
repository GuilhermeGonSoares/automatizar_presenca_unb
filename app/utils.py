from functools import wraps
from flask import abort, current_app
from flask_login import current_user

def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.eh_professor:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
