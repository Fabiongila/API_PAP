from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DadosIoT(db.Model):
    __tablename__ = "dados_iot"

    id = db.Column(db.Integer, primary_key=True)

    # Identificação
    device_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)

    # GPS (NEO-6M)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # BME280
    temperatura_ar = db.Column(db.Float)
    humidade_ar = db.Column(db.Float)
    pressao_ar = db.Column(db.Float)

    # Solo
    humidade_solo = db.Column(db.Float)

    # Vibração (SW-420)
    vibracao = db.Column(db.Boolean)

    # Visão computacional (ESP32-CAM)
    detecao_praga = db.Column(db.Boolean)
    tipo_praga = db.Column(db.String(50))
    confianca = db.Column(db.Float)