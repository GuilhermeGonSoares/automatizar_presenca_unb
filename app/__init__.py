import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# Internal
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://controle_frequencia_user:a0hkpvsHOpBSoeXXaFjjHs04SGvsdpMa@dpg-cgrcrcrk9u56e3lod2l0-a/controle_frequencia'
# External
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://controle_frequencia_user:a0hkpvsHOpBSoeXXaFjjHs04SGvsdpMa@dpg-cgrcrcrk9u56e3lod2l0-a.oregon-postgres.render.com/controle_frequencia'
print('URL DATABASE', os.environ.get("DATABASE_URL"))
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
from app import routes

def create_app():
    return app