from flask import session
from flask_socketio import emit


def init_app(socketio):
    @socketio.on("join")
    def handle_join(data=None):
        nome = session.get("usuario_nome", "Usuário")
        emit(
            "showmsg",
            {"usuario": "Sistema", "mensagem": f"{nome} entrou no chat."},
            broadcast=True,
        )

    @socketio.on("msg")
    def handle_msg(data):
        nome = session.get("usuario_nome", "Usuário")
        texto = (data or {}).get("mensagem", "").strip()
        if texto:
            emit(
                "showmsg",
                {"usuario": nome, "mensagem": texto},
                broadcast=True,
            )