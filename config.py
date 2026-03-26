import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secure-gateway-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'gateway.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Gateway defaults
    GATEWAY_LISTEN_PORT = 9000
    GATEWAY_FORWARD_HOST = '127.0.0.1'
    GATEWAY_FORWARD_PORT = 9001

    # Key rotation interval in days
    KEY_ROTATION_DAYS = 30

    # Log retention in days
    LOG_RETENTION_DAYS = 90

    # Default encryption algorithm
    ENCRYPTION_ALGORITHM = 'AES-128-CBC (Fernet)'
