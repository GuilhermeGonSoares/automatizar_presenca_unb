from app import db, login_manager
from datetime import datetime
from app import bcrypt
from flask_login import UserMixin
import random
import string
from sqlalchemy import event
import pytz


fuso_horario = pytz.timezone('America/Sao_Paulo')

class MatriculaProfessor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(9), unique=True)

@login_manager.user_loader
def load_user(matricula):
    return User.query.get(matricula)

class User(db.Model, UserMixin):
    matricula = db.Column(db.String(9), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    senha_hash = db.Column(db.String(100), nullable=False)
    eh_professor = db.Column(db.Boolean, nullable=True, default=False)

    presenca_todas_aulas = db.relationship('Presenca')

    def __repr__(self):
        return f'User {self.nome}'
    
    def get_id(self):
        return str(self.matricula)
    
    @property
    def senha(self):
        return self.senha

    @senha.setter
    def senha(self, senha_text):
        self.senha_hash = bcrypt.generate_password_hash(senha_text).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.senha_hash, attempted_password)

class Presenca(db.Model):
    user_matricula = db.Column(db.String, db.ForeignKey('user.matricula'), primary_key=True)
    aula_id = db.Column(db.Integer, db.ForeignKey('aula.id'), primary_key=True)
    presente = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.DateTime, nullable=True, default=datetime.now(fuso_horario))

    user = db.relationship('User', back_populates='presenca_todas_aulas')
    aula = db.relationship('Aula', back_populates='presencas')


class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.Integer, nullable=True)
    aberta = db.Column(db.Boolean, nullable=True, default=False)
    data = db.Column(db.DateTime, nullable=True, default=datetime.now(fuso_horario))
    data_fechamento = db.Column(db.DateTime, nullable=True, default=datetime.now(fuso_horario))


    presencas = db.relationship('Presenca', cascade='all, delete-orphan')

    def __repr__(self):
        return f'Aula {self.nome}'
    
    @staticmethod
    def generate_code():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=6))

    @staticmethod
    def on_before_insert(mapper, connection, target):
        target.codigo = Aula.generate_code()
        target.data = datetime.now(fuso_horario)
    

#EVENTOS LISTENER -> EVENTOS DISPARADOS ANTES DE SALVAR OU NA HORA DE ATUALIZAR
event.listen(Aula, 'before_insert', Aula.on_before_insert, propagate=True)

@event.listens_for(Aula.aberta, 'set')
def aula_aberta_listener(target, value, oldvalue, initiator):
    if oldvalue == True and value == False:
        target.data_fechamento = datetime.now(fuso_horario)

@event.listens_for(Presenca.presente, 'set')
def marcar_presenca_listener(target, value, oldvalue, initiator):
    if oldvalue == False and value == True:
        target.data = datetime.now(fuso_horario)