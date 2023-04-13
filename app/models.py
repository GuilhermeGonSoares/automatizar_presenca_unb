from app import db, login_manager
from datetime import datetime
from app import bcrypt
from flask_login import UserMixin
import random
import string
from sqlalchemy import event
import pytz
from .routes import redirect, url_for

fuso_horario = pytz.timezone('America/Sao_Paulo')

class MatriculaProfessor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(9), unique=True)
class MatriculaAluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(9), unique=True)

@login_manager.user_loader
def load_user(matricula):
    return User.query.get(matricula)

@login_manager.unauthorized_handler
def unauthorized():
    # Redireciona o usuário para a página de login
    return redirect(url_for('login_page'))

class User(db.Model, UserMixin):
    matricula = db.Column(db.String(9), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    senha_hash = db.Column(db.String(100), nullable=False)
    eh_professor = db.Column(db.Boolean, nullable=True, default=False)

    #Relacionamentos    
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


alunos_disciplinas = db.Table('alunos_disciplinas',
    db.Column('user_matricula', db.String(9), db.ForeignKey('user.matricula')),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('disciplina.id'))
)
class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    professor_matricula = db.Column(db.String, db.ForeignKey('user.matricula'), nullable=True)
    codigo = db.Column(db.String, nullable=True, unique=True)
    
    professor = db.relationship('User', backref='disciplinas_ministradas', foreign_keys=[professor_matricula])
    alunos = db.relationship('User', secondary=alunos_disciplinas, backref='disciplinas_matriculadas')
    aulas = db.relationship('Aula', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_code():
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(characters, k=6))
            if not Disciplina.query.filter_by(codigo=code).first():
                return code

    @staticmethod
    def on_before_insert(mapper, connection, target):
        target.codigo = Disciplina.generate_code()
        target.data = datetime.now()

class Presenca(db.Model):
    user_matricula = db.Column(db.String, db.ForeignKey('user.matricula'), primary_key=True)
    aula_id = db.Column(db.Integer, db.ForeignKey('aula.id'), primary_key=True)
    presente = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.DateTime, nullable=True, default=datetime.now())

    user = db.relationship('User', back_populates='presenca_todas_aulas')
    aula = db.relationship('Aula', back_populates='presencas')


class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String, nullable=True)
    aberta = db.Column(db.Boolean, nullable=True, default=False)
    data = db.Column(db.DateTime, nullable=True, default=datetime.now())
    data_fechamento = db.Column(db.DateTime, nullable=True, default=datetime.now())
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)

    presencas = db.relationship('Presenca', cascade='all, delete-orphan')
    disciplina = db.relationship('Disciplina', back_populates='aulas')

    def __repr__(self):
        return f'Aula {self.nome}'
    
    @staticmethod
    def generate_code():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=6))

    @staticmethod
    def on_before_insert(mapper, connection, target):
        target.codigo = Aula.generate_code()
        target.data = datetime.now()
    

#EVENTOS LISTENER -> EVENTOS DISPARADOS ANTES DE SALVAR OU NA HORA DE ATUALIZAR
event.listen(Aula, 'before_insert', Aula.on_before_insert, propagate=True)
event.listen(Disciplina, 'before_insert', Disciplina.on_before_insert, propagate=True)

@event.listens_for(Aula.aberta, 'set')
def aula_aberta_listener(target, value, oldvalue, initiator):
    if oldvalue == True and value == False:
        target.data_fechamento = datetime.now()

@event.listens_for(Presenca.presente, 'set')
def marcar_presenca_listener(target, value, oldvalue, initiator):
    if oldvalue == False and value == True:
        target.data = datetime.now()