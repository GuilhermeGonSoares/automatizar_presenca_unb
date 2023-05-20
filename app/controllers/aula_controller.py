from flask import Blueprint, request, redirect, flash, url_for
from flask_login import login_required
from ..models import Disciplina, Presenca, Aula, User
from sqlalchemy import desc
from ..utils.professor_required_decorator import professor_required
from app.webapp import db

bp_name = "aula"
bp = Blueprint(bp_name, __name__)


@bp.route("/<int:disciplina_id>", methods=["POST"])
@login_required
@professor_required
def create(disciplina_id):
    nome_aula = request.form["aula"]
    nova_aula = Aula(nome=nome_aula, aberta=True, disciplina_id=disciplina_id)

    alunos = Disciplina.query.join(User).filter_by(id=disciplina_id).first().alunos
    for aluno in alunos:
        nova_aula.presencas.append(Presenca(presente=0, user=aluno))

    db.session.add(nova_aula)
    db.session.commit()
    return redirect(url_for("disciplina.show", disciplina_id=disciplina_id))


@bp.route("/<int:aula_id>/disciplina/<int:disciplina_id>", methods=["GET"])
@login_required
@professor_required
def deletar_aula(aula_id, disciplina_id):
    print("aula", aula_id)
    aula = Aula.query.get(aula_id)
    if not aula:
        flash("Id da aula inválido!", "danger")
        return redirect(url_for("disciplina.list"))

    db.session.delete(aula)
    db.session.commit()
    flash("Aula excluída com sucesso!", "success")
    return redirect(url_for("disciplina.show", disciplina_id=disciplina_id))
