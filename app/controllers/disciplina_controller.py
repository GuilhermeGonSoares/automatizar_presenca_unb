from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from ..models import Disciplina, Presenca, Aula
from sqlalchemy import desc
from ..utils.professor_required_decorator import professor_required
from app.webapp import db

bp_name = "disciplina"
bp = Blueprint(bp_name, __name__)


@bp.route("/")
@login_required
def list():
    """
    Retorna a lista de disciplina
    de acordo com o tipo de usuário
    professor x aluno
    """
    if current_user.eh_professor:
        disciplinas = Disciplina.query.filter_by(professor=current_user).all()
        return render_template(
            "pages/professor-disciplina.html", disciplinas=disciplinas
        )

    disciplinas_matriculadas = current_user.disciplinas_matriculadas
    presencas = current_user.presenca_todas_aulas.order_by(desc(Presenca.data))
    return render_template(
        "pages/aluno-disciplina.html",
        disciplinas_matriculadas=disciplinas_matriculadas,
        presencas=presencas,
    )


@bp.route("/<int:disciplina_id>", methods=["GET"])
@login_required
def show(disciplina_id):
    """
    Mostrar disciplina de acordo com o tipo de usuário
    professor x aluno
    """

    if current_user.eh_professor:
        disciplinas = Disciplina.query.filter_by(professor=current_user).all()
        disciplina = next(filter(lambda disc: disc.id == disciplina_id, disciplinas))
        return render_template(
            "pages/professor.html",
            disciplina=disciplina,
            disciplinas=disciplinas,
            aulas=disciplina.aulas,
        )

    disciplinas_matriculadas = current_user.disciplinas_matriculadas
    disciplina = list(
        filter(lambda d: d.id == disciplina_id, disciplinas_matriculadas)
    )[0]
    presencas = (
        Presenca.query.join(Aula)
        .filter(Aula.disciplina_id == disciplina_id)
        .filter_by(user=current_user)
        .all()
    )

    return render_template(
        "pages/aluno.html",
        disciplina=disciplina,
        disciplinas=disciplinas_matriculadas,
        presencas=presencas,
    )


@bp.route("/", methods=["POST"])
@login_required
@professor_required
def create():
    """
    Professor criando disciplina
    """
    user = current_user
    nome_disciplina = request.form["disciplina"]
    nova_disciplina = Disciplina(nome=nome_disciplina, professor=user)

    db.session.add(nova_disciplina)
    db.session.commit()
    return redirect(url_for("disciplina.show", disciplina_id=nova_disciplina.id))


@bp.route("/cadastrar", methods=["POST"])
@login_required
def cadastrar_disciplina():
    """
    Aluno cadastrando a disciplina de acordo com o código fornecido
    """
    codigo = request.form["disciplina_codigo"]

    disciplina = Disciplina.query.filter_by(codigo=codigo).first()
    if not disciplina:
        flash(f"Código da disciplina inválido", category="danger")
        return redirect(url_for("disciplina.list"))

    disciplina.alunos.append(current_user)

    aulas = disciplina.aulas

    for aula in aulas:
        aula.presencas.append(Presenca(presente=0, user=current_user))

    db.session.commit()
    flash(f"Disciplina cadastrada", category="success")
    return redirect(url_for("disciplina.list"))


@bp.route("/<int:disciplina_id>/delete")
@login_required
@professor_required
def delete(disciplina_id):
    """
    Professor pode deletar a disciplina
    """

    disciplina = Disciplina.query.get(disciplina_id)
    if not disciplina:
        flash("Id da aula inválido!", "danger")
        return redirect(url_for("disciplina.list"))

    db.session.delete(disciplina)
    db.session.commit()
    flash("Disciplina excluída com sucesso!", "success")
    return redirect(url_for("disciplina.list"))
