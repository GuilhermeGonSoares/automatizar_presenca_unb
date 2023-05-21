from app.webapp import db
from app.models import Aula, Disciplina, Presenca, User
from math import ceil


def dados_disciplina(user, disciplina_id):
    total_aulas = Aula.query.filter_by(disciplina_id=disciplina_id).count()

    total_presencas = (
        db.session.query(Presenca)
        .join(Aula)
        .filter(Aula.disciplina_id == disciplina_id)
        .filter(Presenca.user_matricula == user.matricula)
        .filter(Presenca.presente == True)
        .count()
    )

    total_faltas = total_aulas - total_presencas
    aproveitamento = 0
    if total_aulas > 0:
        aproveitamento = ceil((total_presencas * 100) / total_aulas)

    return {
        "total_aulas": total_aulas,
        "total_presencas": total_presencas,
        "total_faltas": total_faltas,
        "aproveitamento": aproveitamento,
    }
