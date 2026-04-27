import os
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).parent
CONFIG_PATH = os.environ.get('CONFIG_PATH', BASE_DIR / 'config.yaml')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

DATABASE_URL = (
    f"postgresql+asyncpg://{config['database']['username']}:{config['database']['password']}"
    f"@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}"
)
DATABASE_URL_SYNC = (
    f"postgresql://{config['database']['username']}:{config['database']['password']}"
    f"@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}"
)

SECRET_KEY = config['app']['secret_key']
JWT_SECRET = config['app']['jwt_secret']
JWT_ALGORITHM = config['app']['jwt_algorithm']
ACCESS_TOKEN_EXPIRE_MINUTES = config['app']['access_token_expire_minutes']

APP_HOST = config['app']['host']
APP_PORT = config['app']['port']