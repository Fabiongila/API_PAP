<<<<<<< HEAD
from flask import Flask
from models import db
from routes import api_routes
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Importar blueprints
try:
    from auth_routes import auth_bp, blacklist
except Exception as e:
    print(f"Error importing auth_routes: {e}")
    auth_bp = None
    blacklist = set()

try:
    from dashboard_routes import dashboard_bp, auth_pages_bp
except Exception as e:
    print(f"Error importing dashboard_routes: {e}")
    dashboard_bp = None
    auth_pages_bp = None

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# INIT DB
db.init_app(app)

# JWT
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    return jti in blacklist

# BLUEPRINTS
# API routes
if auth_bp:
    app.register_blueprint(auth_bp)
app.register_blueprint(api_routes)

# Frontend routes
if auth_pages_bp:
    app.register_blueprint(auth_pages_bp)
if dashboard_bp:
    app.register_blueprint(dashboard_bp)

# Debug: Print all registered routes
print("\n=== REGISTERED ROUTES ===")
for rule in app.url_map.iter_rules():
    print(f"{rule.rule} -> {rule.endpoint}")
print("=== END ROUTES ===\n")

with app.app_context():
    db.create_all()


# RUN
if __name__ == "__main__":
    port = int(os.environ   .get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
=======
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
>>>>>>> 955b517415ac3a61e71d7f17f5e1d348940e4c1e
