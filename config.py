<<<<<<< HEAD
import os

class Config:
    SECRET_KEY = "super-secret-key"
    JWT_SECRET_KEY = "jwt-super-secret-key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
=======
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
>>>>>>> 955b517415ac3a61e71d7f17f5e1d348940e4c1e
