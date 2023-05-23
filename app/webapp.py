import os
from dotenv import load_dotenv

load_dotenv()

from os import path
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from flask_migrate import Migrate

db: SQLAlchemy = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f'sqlite:///{path.join(path.abspath(path.dirname(__file__)), "database.db")}'
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["MAIL_SERVER"] = "smtp.googlemail.com"
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD")

    from .models.aula import fechar_aulas

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=fechar_aulas, trigger="interval", seconds=1800
    )  # Executa a função a cada minuto
    scheduler.start()

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # register flask blueprints
    from .auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix=f"/{auth_bp.name}")

    from .controllers import blueprints

    for bp in blueprints():
        app.register_blueprint(bp, url_prefix=f"/{bp.name}")

    from .auth.loaders import load_user

    return app


app = create_app()


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("auth.session.login"))
