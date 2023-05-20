from . import db, bcrypt
from flask_login import UserMixin


class MatriculaProfessor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(9), unique=True)


class User(db.Model, UserMixin):
    matricula = db.Column(db.String(9), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    senha_hash = db.Column(db.String(100), nullable=False)
    eh_professor = db.Column(db.Boolean, nullable=True, default=False)

    # Relacionamentos
    presenca_todas_aulas = db.relationship("Presenca")

    def __repr__(self):
        return f"User {self.nome}"

    def get_id(self):
        return str(self.matricula)

    @property
    def senha(self):
        return self.senha

    @senha.setter
    def senha(self, senha_text):
        self.senha_hash = bcrypt.generate_password_hash(senha_text).decode("utf-8")

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.senha_hash, attempted_password)
