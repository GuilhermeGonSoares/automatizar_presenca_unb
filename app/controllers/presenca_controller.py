from flask import Blueprint, request, redirect, flash, url_for, make_response
from flask_login import login_required, current_user
from ..models import Disciplina, Presenca, Aula
from sqlalchemy import desc
from ..utils.professor_required_decorator import professor_required
from app.webapp import db
import datetime

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


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


@bp.route("/relatorio/<int:aula_id>", methods=["GET"])
@login_required
@professor_required
def relatorio(aula_id):
    presencas = (
        Presenca.query.filter_by(aula_id=aula_id)
        .order_by(Presenca.user_matricula)
        .all()
    )
    if len(presencas) == 0:
        flash("Nenhum aluno cadastrado na disciplina!", "warning")
        return redirect(url_for("disciplina.list"))

    aula = presencas[0].aula
    # Cria o documento PDF
    buff = BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=landscape(letter))
    style = getSampleStyleSheet()
    data = [["Matrícula", "Aluno", "Data da presença", "Presente?"]]
    for presenca in presencas:
        aluno = presenca.user
        data_hora = presenca.data

        presente = "Presente" if presenca.presente else "Faltou"
        data_formatada = (
            data_hora.strftime("%H:%M %d/%m/%Y") if presenca.presente else "----"
        )

        data.append([presenca.user_matricula, aluno.nome, data_formatada, presente])
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("ALIGN", (0, 1), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ]
        )
    )
    elements = []
    elements.append(table)
    doc.build(elements)

    # Envia a resposta com o arquivo PDF
    response = make_response(buff.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename=relatorio_presencas_{aula.nome}.pdf"
    return response
