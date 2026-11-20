import os
from flask import Flask
from flask_socketio import SocketIO
from models.database import db
from controllers import routes, chat

app = Flask(__name__, template_folder="views")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Conexão com o banco rede_social criado no MySQL / HeidiSQL
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:@localhost:3306/rede_social"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Sessão e upload de imagens
app.config["SECRET_KEY"] = "chave_secreta_cozy_club"
app.config["PERMANENT_SESSION_LIFETIME"] = 3600
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static/uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

db.init_app(app)
routes.init_app(app)
chat.init_app(socketio)

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)