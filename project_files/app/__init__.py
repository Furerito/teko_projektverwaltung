# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from configparser import ConfigParser
import os
from flask_migrate import Migrate  # hinzugefügt

from app.basic_routes import init_basic_routes

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '../config.ini')
config = ConfigParser()
config.read(config_path)

app = Flask(__name__, static_folder=config['flask']['static_folder'])
app.config['SECRET_KEY'] = config['flask']['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}/{config['database']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app, db)  # Flask-Migrate aktivieren

init_basic_routes(app, db)

from app.schemas.users_schema import *

# Hier erst nach DB-Definition importieren, um Zirkularimport zu verhindern!
from app.routes.kontakte_routes import init_kontakte_routes
from app.routes.projekte_routes import init_projekte_routes

# Initialisierung der Routen
init_kontakte_routes(app)
init_projekte_routes(app)

with app.app_context():
    db.create_all()
