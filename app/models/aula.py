from . import db
from .disciplina import Disciplina
from .presenca import Presenca
from sqlalchemy import event
from sqlalchemy.orm import relationship

import random
import string
from datetime import datetime


class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String, nullable=True)
    aberta = db.Column(db.Boolean, nullable=True, default=False)
    data = db.Column(db.DateTime, nullable=True, default=datetime.now())
    data_fechamento = db.Column(db.DateTime, nullable=True, default=datetime.now())
    disciplina_id = db.Column(
        db.Integer, db.ForeignKey("disciplina.id"), nullable=False
    )

    presencas = db.relationship("Presenca", cascade="all, delete-orphan")
    disciplina = db.relationship("Disciplina", back_populates="aulas")

    def __repr__(self):
        return f"Aula {self.nome}"

    @staticmethod
    def generate_code():
        characters = string.ascii_letters + string.digits
        return "".join(random.choices(characters, k=6))

    @staticmethod
    def on_before_insert(mapper, connection, target):
        target.codigo = Aula.generate_code()
        target.data = datetime.now()


class LocalizacaoAula(db.Model):
    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False
    )
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    aula_id = db.Column(
        db.Integer,
        db.ForeignKey("aula.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    aula = db.relationship(
        "Aula", backref=db.backref("localizacao", uselist=False), cascade="all, delete"
    )


# EVENTOS LISTENER -> EVENTOS DISPARADOS ANTES DE SALVAR OU NA HORA DE ATUALIZAR
event.listen(Aula, "before_insert", Aula.on_before_insert, propagate=True)
event.listen(Disciplina, "before_insert", Disciplina.on_before_insert, propagate=True)


@event.listens_for(Aula.aberta, "set")
def aula_aberta_listener(target, value, oldvalue, initiator):
    if oldvalue == True and value == False:
        target.data_fechamento = datetime.now()


@event.listens_for(Presenca.presente, "set")
def marcar_presenca_listener(target, value, oldvalue, initiator):
    if oldvalue == False and value == True:
        target.data = datetime.now()
