from ..webapp import db, login_manager, bcrypt

from .user import User, MatriculaProfessor
from .disciplina import Disciplina, Horario
from .aula import Aula, LocalizacaoAula
from .presenca import Presenca


__all__ = [
    User,
    Disciplina,
    Aula,
    Presenca,
    LocalizacaoAula,
    MatriculaProfessor,
    Horario,
]
