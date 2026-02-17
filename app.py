from flask import Flask
from models import db
from routes import api_routes
from auth_routes import auth_bp, blacklist
from dashboard_routes import dashboard_bp, auth_pages_bp
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

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
app.register_blueprint(auth_bp)
app.register_blueprint(api_routes)

# Frontend routes
app.register_blueprint(auth_pages_bp)
app.register_blueprint(dashboard_bp)


with app.app_context():
    db.create_all()


# RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
