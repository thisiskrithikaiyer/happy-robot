import os

from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import api

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["X-API-Key", "Content-Type"])
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(api, url_prefix='/api')

with app.app_context():
    db.create_all()
    from models import Load
    if Load.query.count() == 0:
        from create_sample_data import create_sample_loads
        create_sample_loads()

if __name__ == '__main__':
    app.run(debug=True)