import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # CORS Configuration
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Firebase Configuration
    FIREBASE_BUCKET = os.getenv('FIREBASE_BUCKET', 'adobe-gensolve.appspot.com')
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', './privateKey.json')
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your-app-password')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'csv'}
    
    # Processing Configuration
    DEFAULT_CANVAS_SIZE = (512, 512)
    MAX_PROCESSING_TIME = 300  # 5 minutes
    
    # Database Configuration (if needed later)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Security Configuration
    CORS_ORIGINS = [
        FRONTEND_URL,
        "http://localhost:3000",
        "https://adobe-gensolve.vercel.app"
    ] 