import os

# Carrega variáveis do ficheiro .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass  # python-dotenv não instalado — usa variáveis de ambiente do sistema

class Config:
    SECRET_KEY     = os.environ.get("SECRET_KEY",     "muda-esta-chave-secreta-para-producao")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "muda-esta-chave-jwt-para-producao")

    SQLALCHEMY_DATABASE_URI    = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
