import os
import uuid
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from models.database import Post, Usuario, db

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "gif"}


def extensao_valida(nome_arquivo):
    return (
        "." in nome_arquivo
        and nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS
    )


def init_app(app):
    @app.before_request
    def exigir_login():
        rotas_protegidas = {
            "feed",
            "nova_postagem",
            "upload",
            "chat",
            "perfil",
            "atualizar_foto_perfil",
        }
        if request.endpoint in rotas_protegidas and "user_id" not in session:
            flash("Faça login para acessar o cozy club.", "warning")
            return redirect(url_for("login"))

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("feed"))
        return redirect(url_for("login"))

    @app.route("/cadastro", methods=["GET", "POST"])
    def cadastro():
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip().lower()
            senha = request.form.get("senha", "")

            if not nome or not email or not senha:
                flash("Preencha nome, e-mail e senha.", "danger")
                return redirect(url_for("cadastro"))

            if Usuario.query.filter_by(email=email).first():
                flash("Esse e-mail já está cadastrado.", "warning")
                return redirect(url_for("cadastro"))

            novo_usuario = Usuario(
                nome=nome,
                email=email,
                senha=generate_password_hash(senha, method="scrypt"),
            )
            db.session.add(novo_usuario)
            db.session.commit()

            flash("Cadastro concluído! Faça seu login.", "success")
            return redirect(url_for("login"))

        return render_template("cadastro.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            senha = request.form.get("senha", "")

            usuario = Usuario.query.filter_by(email=email).first()
            if usuario and check_password_hash(usuario.senha, senha):
                session["user_id"] = usuario.id
                session["usuario_nome"] = usuario.nome
                session["usuario_email"] = usuario.email
                flash(f"Olá, {usuario.nome}!", "success")
                return redirect(url_for("feed"))

            flash("E-mail ou senha inválidos.", "danger")
            return redirect(url_for("login"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Você saiu da sua conta.", "info")
        return redirect(url_for("login"))

    @app.route("/feed")
    def feed():
        posts = Post.query.order_by(Post.data_criacao.desc()).all()
        usuario_atual = db.session.get(Usuario, session["user_id"])
        return render_template(
            "feed.html",
            posts=posts,
            usuario=usuario_atual,
            usuario_nome=session.get("usuario_nome"),
        )

    @app.route("/nova-postagem")
    def nova_postagem():
        usuario_atual = db.session.get(Usuario, session["user_id"])
        return render_template(
            "nova_postagem.html",
            usuario=usuario_atual,
            usuario_nome=session.get("usuario_nome"),
        )

    @app.route("/upload", methods=["POST"])
    def upload():
        if "file" not in request.files:
            flash("Selecione uma imagem para publicar.", "danger")
            return redirect(url_for("nova_postagem"))

        arquivo = request.files["file"]
        hobby = request.form.get("hobby", "").strip()
        legenda = request.form.get("legenda", "").strip()

        if arquivo.filename == "" or not extensao_valida(arquivo.filename):
            flash("Formato inválido. Use apenas png, jpg, jpeg ou gif.", "danger")
            return redirect(url_for("nova_postagem"))

        extensao = arquivo.filename.rsplit(".", 1)[1].lower()
        nome_unico = f"{uuid.uuid4()}.{extensao}"
        caminho_destino = os.path.join(current_app.config["UPLOAD_FOLDER"], nome_unico)
        arquivo.save(caminho_destino)

        novo_post = Post(
            imagem=nome_unico,
            hobby=hobby if hobby else None,
            legenda=legenda if legenda else None,
            usuario_id=session["user_id"],
        )
        db.session.add(novo_post)
        db.session.commit()

        flash("Seu hobby foi publicado no feed!", "success")
        return redirect(url_for("feed"))

    @app.route("/chat")
    def chat():
        usuario_atual = db.session.get(Usuario, session["user_id"])
        return render_template(
            "chat.html",
            usuario=usuario_atual,
            usuario_nome=session.get("usuario_nome"),
        )

    @app.route("/perfil")
    def perfil():
        usuario = db.session.get(Usuario, session["user_id"])
        if not usuario:
            session.clear()
            return redirect(url_for("login"))

        minhas_postagens = (
            Post.query.filter_by(usuario_id=session["user_id"])
            .order_by(Post.data_criacao.desc())
            .all()
        )
        return render_template(
            "perfil.html",
            usuario=usuario,
            usuario_nome=usuario.nome,
            usuario_email=usuario.email,
            posts=minhas_postagens,
        )

    @app.route("/perfil/foto", methods=["POST"])
    def atualizar_foto_perfil():
        if "foto_perfil" not in request.files:
            flash("Selecione uma imagem para o perfil.", "danger")
            return redirect(url_for("perfil"))

        arquivo = request.files["foto_perfil"]
        if arquivo.filename == "" or not extensao_valida(arquivo.filename):
            flash("Envie uma imagem válida (png, jpg, jpeg ou gif).", "danger")
            return redirect(url_for("perfil"))

        usuario = db.session.get(Usuario, session["user_id"])
        if not usuario:
            session.clear()
            return redirect(url_for("login"))

        if usuario.foto_perfil:
            caminho_antigo = os.path.join(
                current_app.config["UPLOAD_FOLDER"], usuario.foto_perfil
            )
            if os.path.exists(caminho_antigo):
                os.remove(caminho_antigo)

        extensao = arquivo.filename.rsplit(".", 1)[1].lower()
        nome_unico = f"{uuid.uuid4()}.{extensao}"
        caminho_novo = os.path.join(current_app.config["UPLOAD_FOLDER"], nome_unico)
        arquivo.save(caminho_novo)

        usuario.foto_perfil = nome_unico
        db.session.commit()

        flash("Foto de perfil atualizada!", "success")
        return redirect(url_for("perfil"))