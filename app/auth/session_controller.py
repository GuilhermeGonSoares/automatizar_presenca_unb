from ..webapp import db
from flask import render_template, redirect, url_for, flash, Blueprint, request
from .forms import RegisterForm, LoginForm
from ..models import User, MatriculaProfessor
from ..utils.professor_required_decorator import professor_required
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime

bp = Blueprint("session", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = User.query.filter_by(matricula=form.matricula.data).first()
            if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.senha.data
            ):
                login_user(attempted_user)
                flash(
                    f"Sucesso! Seja bem-vindo {attempted_user.nome} - {attempted_user.matricula}",
                    category="success",
                )

                return redirect(url_for("disciplina.list"))

            else:
                flash(
                    "Matrícula e senha não batem! Por favor, tente novamente",
                    category="danger",
                )
    return render_template("pages/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            matricula = form.matricula.data
            matricula_professor = MatriculaProfessor.query.filter_by(
                matricula=matricula
            ).first()
            user = User(
                matricula=matricula,
                email=form.email.data,
                nome=form.nome.data,
                senha=form.senha.data,
            )

            user.eh_professor = True if matricula_professor else False

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("auth.session.login"))

        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f"There was an error with creating a user: {err_msg}",
                    category="danger",
                )
    return render_template("pages/register.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.session.login"))
