from flask import Blueprint, request, redirect, flash, url_for
from flask_login import login_required, current_user
from ..models import Disciplina, Presenca, Aula
from sqlalchemy import desc
from ..utils.professor_required_decorator import professor_required
from app.webapp import db
import datetime


bp_name = "presenca"
bp = Blueprint(bp_name, __name__)


@bp.route("/<int:disciplina_id>", methods=["POST"])
@login_required
def marcar_presenca(disciplina_id):
    aula_id = request.form["aula_id"]
    codigo = request.form["codigo"]
    data = datetime.now()  # Data atual na hora de marcar presenca

    aula = Aula.query.filter_by(id=aula_id).first()
    data_aula = aula.data

    intervalo_inicio_chamada_marcar_presenca = (data - data_aula).seconds // 60

    if aula.codigo != codigo:
        flash("Código incorreto, tente novamente.", "danger")
        return redirect(url_for("disciplina.show", disciplina_id=disciplina_id))

    if intervalo_inicio_chamada_marcar_presenca > 20:
        flash(
            f"Já passou o tempo de 20 minutos para marcar presença. Tempo atual: {intervalo_inicio_chamada_marcar_presenca} minutos",
            "danger",
        )
        return redirect(url_for("disciplina.show", disciplina_id=disciplina_id))

    presenca = Presenca.query.filter_by(user=current_user, aula=aula).first()
    presenca.presente = True

    db.session.commit()
    flash("Presença confirmada com sucesso!", "success")
    return redirect(url_for("disciplina.show", disciplina_id=disciplina_id))


@bp.route("/aula/<int:aula_id>/disciplina/<int:disciplina_id>", methods=["GET"])
@login_required
@professor_required
def fechar_presenca(aula_id, disciplina_id):
    aula = Aula.query.get(aula_id)
    if not aula:
        flash("Id da aula inválido!", "danger")
        return redirect(url_for("disciplina.list"))

    aula.aberta = False

    db.session.commit()
    flash("Presença fechada com sucesso", "success")
    return redirect(url_for("disciplina.show", disciplina_id=disciplina_id))
