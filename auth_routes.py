from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

auth_bp = Blueprint("auth", __name__)

# Simples blacklist em memória
blacklist = set()

# ===============================
# REGISTER
# ===============================
@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    nome = data.get("nome")
    email = data.get("email")
    password = data.get("password")

    if not nome or not email or not password:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"erro": "Email já registado"}), 409

    user = User(nome=nome, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Conta criada com sucesso"}), 201


# ===============================
# LOGIN
# ===============================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"erro": "Credenciais inválidas"}), 401

    # GERAR TOKEN
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email
        }
    }), 200


# ===============================
# LOGOUT
# ===============================
@auth_bp.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)

    return jsonify({"msg": "Logout feito com sucesso"}), 200


# ===============================
# DELETE ACCOUNT
# ===============================
@auth_bp.route("/api/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "Conta deletada com sucesso"}), 200
    