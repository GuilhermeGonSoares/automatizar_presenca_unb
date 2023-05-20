from ..webapp import login_manager
from ..models import User
from flask import redirect, url_for


@login_manager.user_loader
def load_user(matricula):
    return User.query.get(matricula)


@login_manager.unauthorized_handler
def unauthorized():
    # Redireciona o usuário para a página de login
    return redirect(url_for("auth.session.login"))
