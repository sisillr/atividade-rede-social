from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255), nullable=True)

    posts = db.relationship("Post", backref="autor", lazy=True)


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(255), nullable=False)
    hobby = db.Column(db.String(60), nullable=True)
    legenda = db.Column(db.String(255), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now, nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)