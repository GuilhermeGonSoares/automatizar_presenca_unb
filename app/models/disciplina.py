from . import db

import random
import string
from datetime import datetime
from sqlalchemy.orm import validates


alunos_disciplinas = db.Table(
    "alunos_disciplinas",
    db.Column("user_matricula", db.String(9), db.ForeignKey("user.matricula")),
    db.Column("disciplina_id", db.Integer, db.ForeignKey("disciplina.id")),
)


class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    professor_matricula = db.Column(
        db.String, db.ForeignKey("user.matricula"), nullable=True
    )
    codigo = db.Column(db.String, nullable=True, unique=True)
    quantidade_total_aulas = db.Column(db.Integer, default=0)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)

    professor = db.relationship(
        "User", backref="disciplinas_ministradas", foreign_keys=[professor_matricula]
    )
    alunos = db.relationship(
        "User", secondary=alunos_disciplinas, backref="disciplinas_matriculadas"
    )
    aulas = db.relationship("Aula", cascade="all, delete-orphan")

    horarios = db.relationship(
        "Horario", backref="disciplina", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"{self.nome}"

    @staticmethod
    def generate_code():
        characters = string.ascii_letters + string.digits
        while True:
            code = "".join(random.choices(characters, k=6))
            if not Disciplina.query.filter_by(codigo=code).first():
                return code

    @staticmethod
    def on_before_insert(mapper, connection, target):
        target.codigo = Disciplina.generate_code()
        target.data = datetime.now()


class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disciplina_id = db.Column(
        db.Integer, db.ForeignKey("disciplina.id"), nullable=False
    )
    dia_semana = db.Column(db.String(20), nullable=False)

    @validates("dia_semana")
    def validate_dia_semana(self, key, value):
        valid_options = [
            "Segunda-feira",
            "Terça-feira",
            "Quarta-feira",
            "Quinta-feira",
            "Sexta-feira",
            "Sabado",
            "Domingo",
        ]
        if value not in valid_options:
            raise ValueError(
                f"Dia da semana inválido. Opções válidas: {', '.join(valid_options)}"
            )
        return value
