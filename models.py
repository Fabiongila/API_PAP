from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

# =====================================================
# USER (AUTENTICAÇÃO)
# =====================================================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ---------- PASSWORD ----------
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

# =====================================================
# DADOS IOT
# =====================================================
class DadosIoT(db.Model):
    __tablename__ = "dados_iot"

    id = db.Column(db.Integer, primary_key=True)

    # Identificação
    device_id = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # GPS
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    localizacao = db.Column(db.String(100))
    
    # BME280
    temperatura_ar = db.Column(db.Float)
    humidade_ar = db.Column(db.Float)
    pressao_ar = db.Column(db.Float)

    # Solo
    humidade_solo = db.Column(db.Float)

    # Vibração
    vibracao = db.Column(db.Boolean)

    # Visão computacional
    detecao_praga = db.Column(db.Boolean)
    tipo_praga = db.Column(db.String(50))
    confianca = db.Column(db.Float)

    def __repr__(self):
        return f"<DadosIoT {self.device_id} {self.timestamp}>"


# =====================================================
# PREVISÕES ML
# =====================================================
class Previsao(db.Model):
    __tablename__ = "previsoes"

    id = db.Column(db.Integer, primary_key=True)
    
    # Link ao dado original
    dados_iot_id = db.Column(db.Integer, db.ForeignKey('dados_iot.id'), nullable=False)
    
    # Previsão de Pragas
    praga_detectada = db.Column(db.Boolean, default=False)
    tipo_praga = db.Column(db.String(100))
    confianca_praga = db.Column(db.Float)  # 0 a 1
    
    # Previsão de Condições Futuras (24h)
    temperatura_prevista = db.Column(db.Float)
    humidade_prevista = db.Column(db.Float)
    
    # Metadata
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<Previsao {self.id} - Praga: {self.praga_detectada}>"
