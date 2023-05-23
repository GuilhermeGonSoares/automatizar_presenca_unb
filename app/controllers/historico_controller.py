from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from ..models import Disciplina, Presenca, Aula, Horario
from sqlalchemy import desc, cast, Date
from ..utils.professor_required_decorator import professor_required
from app.webapp import db
from ..services.presenca_service import dados_disciplina
from datetime import datetime

bp_name = "historico"
bp = Blueprint(bp_name, __name__)


@bp.route("/<int:disciplina_id>", methods=["GET"])
@bp.route("/", methods=["GET"])  # Rota adicional sem o disciplina_id
@login_required
def show(disciplina_id=None):
    semana = [
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sabado",
        "Domingo",
    ]
    # Obtém a data atual
    data_atual = datetime.now().date()
    hora_atual = datetime.now().hour
    min_atual = datetime.now().minute
    # Obtém o dia da semana como um número (segunda-feira = 0, domingo = 6)
    dia_semana = semana[data_atual.weekday()]

    materias_de_hoje = (
        db.session.query(Disciplina)
        .join(Horario)
        .filter(Horario.dia_semana == dia_semana)
        .filter(Disciplina.alunos.contains(current_user))
        .order_by(Disciplina.hora_inicio)
        .all()
    )

    disciplinas = current_user.disciplinas_matriculadas

    disciplina_do_dia = {}

    for materia in materias_de_hoje:
        disciplina_do_dia[materia] = None
        if materia.aulas:
            aula_filtrada = list(
                filter(lambda aula: aula.data.date() == data_atual, materia.aulas)
            )
            presenca = next(
                filter(
                    lambda presenca: presenca.user_matricula == current_user.matricula,
                    aula_filtrada[0].presencas,
                )
            )

            disciplina_do_dia[materia] = (aula_filtrada[0], presenca.presente)

    if not disciplina_id:
        return render_template(
            "pages/materias.html",
            disciplina_do_dia=disciplina_do_dia,
            disciplinas=disciplinas,
            materias="active",
        )

    historico_presencas = (
        db.session.query(Presenca)
        .join(Aula)
        .filter(Aula.disciplina_id == disciplina_id)
        .filter(Presenca.user_matricula == current_user.matricula)
        .all()
    )
    return render_template(
        "pages/materias.html",
        disciplina_do_dia=disciplina_do_dia,
        disciplinas=disciplinas,
        historico_presencas=historico_presencas,
        disciplina_id=disciplina_id,
        materias="active",
    )
