from flask import Flask
from models import db
from routes import api_routes
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(api_routes) 




if __name__ == '__main__':
   port= int(os.environ.get("PORT", 5000))
   app.run(host="0.0.0.0", port=port)