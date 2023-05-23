from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp
from app.models import User


class RegisterForm(FlaskForm):
    def validate_email(self, email_to_check):
        user = User.query.filter_by(email=email_to_check.data).first()

        if user:
            raise ValidationError("Email já cadastrado")

    def validate_matricula(self, matricula_to_check):
        user = User.query.filter_by(matricula=matricula_to_check.data).first()

        if user:
            raise ValidationError("Matricula já cadastrado")

    matricula = StringField(
        label="Matrícula",
        validators=[
            DataRequired(),
            Length(min=9, max=9, message="A matrícula deve ter 9 caracteres."),
        ],
    )
    email = StringField(
        label="Email",
        validators=[
            DataRequired(),
            Regexp(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                message="Email inválido",
            ),
        ],
    )
    nome = StringField(label="Nome", validators=[DataRequired(), Length(min=2, max=50)])
    senha = PasswordField(
        label="Senha",
        validators=[
            DataRequired(),
            Length(min=4, message="A senha tem que ter no mínimo 4 caracteres"),
        ],
    )
    funcao = RadioField(
        label="Você é?",
        choices=[("aluno", "Aluno"), ("professor", "Professor")],
        default="aluno",
    )
    submit = SubmitField(label="Fazer Cadastro")


class LoginForm(FlaskForm):
    matricula = StringField(
        label="Matrícula",
        validators=[
            DataRequired(),
            Length(min=9, max=9, message="A matrícula deve ter 9 caracteres."),
        ],
    )
    senha = PasswordField(
        label="Senha",
        validators=[
            DataRequired(),
            Length(min=4, message="A senha tem que ter no mínimo 4 caracteres"),
        ],
    )
    submit = SubmitField(label="Login")
