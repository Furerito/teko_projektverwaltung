import os
from configparser import ConfigParser
from datetime import timedelta  # <-- wichtig!

print('config.py')

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '../config.ini')

config = ConfigParser()
config.read(config_path)

class Config:
    SECRET_KEY = config['flask']['secret_key']
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(config['flask']['session_timeout']))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_CONFIG = {
        'host': config['database']['host'],
        'database': config['database']['database'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'port': config['database']['port']
    }
    ISSUER_NAME = config['flask']['issuer_name']
    APP_LOGO = config['app']['logo']
    PORT = int(config['flask']['port'])
    STATIC_FOLDER = config['flask']['static_folder']
