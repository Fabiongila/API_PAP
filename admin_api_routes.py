from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from models import db, User, Fazenda, Sensor, Log, DadosIoT
from auth_routes import add_log

admin_api_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")


# ─────────────────────────────────────────────
# DECORADOR: exige superadmin ou admin
# ─────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def wrapper(*args, **kwargs):
        u = User.query.get(int(get_jwt_identity()))
        if not u or u.role not in ("superadmin", "admin"):
            return jsonify({"erro": "Acesso negado. Apenas administradores."}), 403
        return f(*args, **kwargs)
    return wrapper


def superadmin_required(f):
    @wraps(f)
    @jwt_required()
    def wrapper(*args, **kwargs):
        u = User.query.get(int(get_jwt_identity()))
        if not u or u.role != "superadmin":
            return jsonify({"erro": "Acesso negado. Apenas super administradores."}), 403
        return f(*args, **kwargs)
    return wrapper


def get_current_user():
    return User.query.get(int(get_jwt_identity()))


# ─────────────────────────────────────────────
# STATS — GET /api/admin/stats
# ─────────────────────────────────────────────
@admin_api_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    total_users     = User.query.count()
    total_fazendas  = Fazenda.query.count()
    total_sensores  = Sensor.query.count()
    total_logs      = Log.query.count()
    total_dados_iot = DadosIoT.query.count()
    admins          = User.query.filter(User.role.in_(["admin", "superadmin"])).count()
    agricultores    = User.query.filter_by(role="agricultor").count()
    sensores_online = Sensor.query.filter_by(status="online").count()
    sensores_off    = Sensor.query.filter_by(status="offline").count()

    return jsonify({
        "utilizadores": {"total": total_users, "admins": admins, "agricultores": agricultores},
        "fazendas":     {"total": total_fazendas},
        "sensores":     {"total": total_sensores, "online": sensores_online, "offline": sensores_off},
        "logs":         {"total": total_logs},
        "dados_iot":    {"total": total_dados_iot},
    }), 200


# ─────────────────────────────────────────────
# UTILIZADORES — CRUD
# ─────────────────────────────────────────────
@admin_api_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_api_bp.route("/users", methods=["POST"])
@superadmin_required
def create_user():
    d     = request.get_json(silent=True) or {}
    nome  = (d.get("nome") or "").strip()
    email = (d.get("email") or "").strip().lower()
    pw    = d.get("password") or ""
    role  = d.get("role", "agricultor")

    if not nome or not email or not pw:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
    if len(pw) < 6:
        return jsonify({"erro": "A senha deve ter pelo menos 6 caracteres"}), 400
    if role not in ("superadmin", "admin", "agricultor"):
        return jsonify({"erro": "Perfil inválido"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"erro": "Email já registado"}), 409

    u = User(nome=nome, email=email, role=role)
    u.set_password(pw)
    db.session.add(u)
    db.session.commit()

    actor = get_current_user()
    add_log("Utilizador criado", f'Admin criou conta "{nome}" ({role})', actor.nome)
    return jsonify(u.to_dict()), 201


@admin_api_bp.route("/users/<int:uid>", methods=["PUT"])
@superadmin_required
def update_user(uid):
    u = User.query.get(uid)
    if not u:
        return jsonify({"erro": "Utilizador não encontrado"}), 404

    d = request.get_json(silent=True) or {}
    if "nome" in d and d["nome"].strip():
        u.nome = d["nome"].strip()
    if "email" in d and d["email"].strip():
        new_email = d["email"].strip().lower()
        if new_email != u.email and User.query.filter_by(email=new_email).first():
            return jsonify({"erro": "Email já em uso"}), 409
        u.email = new_email
    if "role" in d:
        if d["role"] not in ("superadmin", "admin", "agricultor"):
            return jsonify({"erro": "Perfil inválido"}), 400
        u.role = d["role"]
    if "is_active" in d:
        u.is_active = bool(d["is_active"])
    if "password" in d and d["password"]:
        if len(d["password"]) < 6:
            return jsonify({"erro": "A senha deve ter pelo menos 6 caracteres"}), 400
        u.set_password(d["password"])

    db.session.commit()
    actor = get_current_user()
    add_log("Utilizador atualizado", f'Admin atualizou conta de "{u.nome}"', actor.nome)
    return jsonify(u.to_dict()), 200


@admin_api_bp.route("/users/<int:uid>", methods=["DELETE"])
@superadmin_required
def delete_user(uid):
    actor = get_current_user()
    if actor.id == uid:
        return jsonify({"erro": "Não pode eliminar a sua própria conta aqui"}), 400
    u = User.query.get(uid)
    if not u:
        return jsonify({"erro": "Utilizador não encontrado"}), 404
    nome = u.nome
    db.session.delete(u)
    db.session.commit()
    add_log("Utilizador eliminado", f'Admin eliminou conta de "{nome}"', actor.nome)
    return jsonify({"msg": f'Utilizador "{nome}" eliminado'}), 200


# ─────────────────────────────────────────────
# FAZENDAS — CRUD
# ─────────────────────────────────────────────
@admin_api_bp.route("/fazendas", methods=["GET"])
@admin_required
def list_fazendas():
    fazendas = Fazenda.query.order_by(Fazenda.created_at.desc()).all()
    return jsonify([f.to_dict() for f in fazendas]), 200


@admin_api_bp.route("/fazendas", methods=["POST"])
@admin_required
def create_fazenda():
    d = request.get_json(silent=True) or {}
    nome = (d.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "Nome da fazenda é obrigatório"}), 400

    f = Fazenda(
        nome=nome,
        proprietario=d.get("proprietario", "").strip(),
        localizacao=d.get("localizacao", "").strip(),
        hectares=d.get("hectares"),
        cultura=d.get("cultura", "").strip(),
        status=d.get("status", "active"),
    )
    db.session.add(f)
    db.session.commit()

    actor = get_current_user()
    add_log("Fazenda criada", f'Fazenda "{nome}" adicionada', actor.nome)
    return jsonify(f.to_dict()), 201


@admin_api_bp.route("/fazendas/<int:fid>", methods=["PUT"])
@admin_required
def update_fazenda(fid):
    f = Fazenda.query.get(fid)
    if not f:
        return jsonify({"erro": "Fazenda não encontrada"}), 404

    d = request.get_json(silent=True) or {}
    if "nome"         in d and d["nome"].strip(): f.nome         = d["nome"].strip()
    if "proprietario" in d: f.proprietario = d["proprietario"]
    if "localizacao"  in d: f.localizacao  = d["localizacao"]
    if "hectares"     in d: f.hectares     = d["hectares"]
    if "cultura"      in d: f.cultura      = d["cultura"]
    if "status"       in d: f.status       = d["status"]

    db.session.commit()
    actor = get_current_user()
    add_log("Fazenda atualizada", f'Fazenda "{f.nome}" atualizada', actor.nome)
    return jsonify(f.to_dict()), 200


@admin_api_bp.route("/fazendas/<int:fid>", methods=["DELETE"])
@admin_required
def delete_fazenda(fid):
    f = Fazenda.query.get(fid)
    if not f:
        return jsonify({"erro": "Fazenda não encontrada"}), 404
    nome = f.nome
    db.session.delete(f)
    db.session.commit()
    actor = get_current_user()
    add_log("Fazenda eliminada", f'Fazenda "{nome}" eliminada', actor.nome)
    return jsonify({"msg": f'Fazenda "{nome}" eliminada'}), 200


# ─────────────────────────────────────────────
# SENSORES — CRUD
# ─────────────────────────────────────────────
@admin_api_bp.route("/sensores", methods=["GET"])
@admin_required
def list_sensores():
    sensores = Sensor.query.order_by(Sensor.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sensores]), 200


@admin_api_bp.route("/sensores", methods=["POST"])
@admin_required
def create_sensor():
    d    = request.get_json(silent=True) or {}
    nome = (d.get("nome") or "").strip()
    tipo = (d.get("tipo") or "").strip()
    if not nome or not tipo:
        return jsonify({"erro": "Nome e tipo do sensor são obrigatórios"}), 400
    if tipo not in ("Clima", "Solo", "GPS", "Câmara"):
        return jsonify({"erro": "Tipo inválido. Use: Clima, Solo, GPS ou Câmara"}), 400

    s = Sensor(
        nome=nome,
        tipo=tipo,
        fazenda_id=d.get("fazenda_id"),
        status=d.get("status", "online"),
        bateria=d.get("bateria", 100),
    )
    db.session.add(s)
    db.session.commit()

    actor = get_current_user()
    add_log("Sensor criado", f'Sensor "{nome}" ({tipo}) adicionado', actor.nome)
    return jsonify(s.to_dict()), 201


@admin_api_bp.route("/sensores/<int:sid>", methods=["PUT"])
@admin_required
def update_sensor(sid):
    s = Sensor.query.get(sid)
    if not s:
        return jsonify({"erro": "Sensor não encontrado"}), 404

    d = request.get_json(silent=True) or {}
    if "nome"      in d and d["nome"].strip(): s.nome      = d["nome"].strip()
    if "tipo"      in d:
        if d["tipo"] not in ("Clima", "Solo", "GPS", "Câmara"):
            return jsonify({"erro": "Tipo inválido"}), 400
        s.tipo = d["tipo"]
    if "fazenda_id" in d: s.fazenda_id = d["fazenda_id"]
    if "status"     in d: s.status     = d["status"]
    if "bateria"    in d: s.bateria    = d["bateria"]

    db.session.commit()
    actor = get_current_user()
    add_log("Sensor atualizado", f'Sensor "{s.nome}" atualizado', actor.nome)
    return jsonify(s.to_dict()), 200


@admin_api_bp.route("/sensores/<int:sid>", methods=["DELETE"])
@admin_required
def delete_sensor(sid):
    s = Sensor.query.get(sid)
    if not s:
        return jsonify({"erro": "Sensor não encontrado"}), 404
    nome = s.nome
    db.session.delete(s)
    db.session.commit()
    actor = get_current_user()
    add_log("Sensor eliminado", f'Sensor "{nome}" eliminado', actor.nome)
    return jsonify({"msg": f'Sensor "{nome}" eliminado'}), 200


# ─────────────────────────────────────────────
# LOGS — GET /api/admin/logs
# ─────────────────────────────────────────────
@admin_api_bp.route("/logs", methods=["GET"])
@admin_required
def list_logs():
    limit  = min(int(request.args.get("limit", 200)), 1000)
    offset = int(request.args.get("offset", 0))
    logs   = Log.query.order_by(Log.created_at.desc()).offset(offset).limit(limit).all()
    return jsonify([l.to_dict() for l in logs]), 200
