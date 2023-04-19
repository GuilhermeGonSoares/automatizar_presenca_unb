import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_SQLITE')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'

# Internal
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://controle_frequencia_user:a0hkpvsHOpBSoeXXaFjjHs04SGvsdpMa@dpg-cgrcrcrk9u56e3lod2l0-a/controle_frequencia'
# External
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://controle_frequencia_user:a0hkpvsHOpBSoeXXaFjjHs04SGvsdpMa@dpg-cgrcrcrk9u56e3lod2l0-a.oregon-postgres.render.com/controle_frequencia'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
from app import routes

def create_app():
    return app