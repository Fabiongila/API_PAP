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
