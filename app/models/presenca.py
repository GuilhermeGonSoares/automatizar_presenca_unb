from . import db

from sqlalchemy.orm import relationship

from datetime import datetime


class Presenca(db.Model):
    user_matricula = db.Column(
        db.String, db.ForeignKey("user.matricula"), primary_key=True
    )
    aula_id = db.Column(db.Integer, db.ForeignKey("aula.id"), primary_key=True)
    presente = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.DateTime, nullable=True, default=datetime.now())

    user = db.relationship("User", back_populates="presenca_todas_aulas")
    aula = db.relationship("Aula", back_populates="presencas")
