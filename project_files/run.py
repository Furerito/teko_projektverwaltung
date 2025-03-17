from configparser import ConfigParser
import os
from app import app

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, 'config.ini')  # ggf. Pfad anpassen
config = ConfigParser()
config.read(config_path)

PORT = int(config['flask'].get('port', 3355))  # Fallback auf 5000 falls nicht gesetzt

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Document Root: {os.getcwd()}")
print('run.py')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3355, debug=True)
