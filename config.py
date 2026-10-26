import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load .env file from BASE_DIR explicitly for WSGI/cPanel
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()


class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-dev-2026')
    
    # Database MySQL Configuration (phpMyAdmin)
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'db_katalog')
    
    # Upload Settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'katalog')
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB max file request
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # Catalog Image Rules
    MIN_IMAGES = 1
    MAX_IMAGES = 5
