from flask import Flask
from models import db
from routes import api_routes
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

from auth_routes import auth_bp, blacklist
from dashboard_routes import dashboard_bp, auth_pages_bp
from admin_api_routes import admin_api_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload.get("jti") in blacklist

# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_routes)
app.register_blueprint(auth_pages_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_api_bp)

with app.app_context():
    db.create_all()

    # ── Migração: adicionar colunas novas à tabela mensagens se não existirem ──
    from sqlalchemy import text, inspect as sa_inspect
    try:
        inspector = sa_inspect(db.engine)
        if inspector.has_table('mensagens'):
            existing_cols = [c['name'] for c in inspector.get_columns('mensagens')]
            migrations = [
                ("origem",         "VARCHAR(30) DEFAULT 'dashboard'"),
                ("telefone",       "VARCHAR(30)"),
                ("nome_contacto",  "VARCHAR(150)"),
                ("email_contacto", "VARCHAR(200)"),
            ]
            for col_name, col_def in migrations:
                if col_name not in existing_cols:
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text(f"ALTER TABLE mensagens ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                        print(f"[Migration] Coluna '{col_name}' adicionada a mensagens.")
                    except Exception as e:
                        print(f"[Migration] Aviso ao adicionar coluna {col_name}: {e}")
    except Exception as e:
        print(f"[Migration] Erro na verificacao de colunas: {e}")

    # Garantir que existe sempre pelo menos um superadmin
    from models import User
    if not User.query.filter_by(email="admin@agrocaua.com").first():
        u = User(nome="Administrador", email="admin@agrocaua.com", role="superadmin")
        u.set_password("admin123")
        db.session.add(u)
        db.session.commit()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
