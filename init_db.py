"""
Database initialization script — Creates tables and seeds default data.
"""

from app import create_app
from models import db, User, SystemSetting, EncryptionKey
from core.key_manager import KeyManager
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone


def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Seed default admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.session.add(admin)

        # Seed analyst user
        if not User.query.filter_by(username='analyst').first():
            analyst = User(
                username='analyst',
                password_hash=generate_password_hash('analyst123'),
                role='analyst',
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.session.add(analyst)

        # Seed operator user
        if not User.query.filter_by(username='operator').first():
            operator = User(
                username='operator',
                password_hash=generate_password_hash('operator123'),
                role='operator',
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.session.add(operator)

        # Seed default system settings
        defaults = {
            'encryption_algorithm': 'AES-128-CBC (Fernet)',
            'gateway_listen_port': '9000',
            'gateway_forward_host': '127.0.0.1',
            'gateway_forward_port': '9001',
            'key_rotation_days': '30',
            'log_retention_days': '90',
            'log_level': 'INFO'
        }
        for key, value in defaults.items():
            if not SystemSetting.query.filter_by(key=key).first():
                db.session.add(SystemSetting(key=key, value=value))

        db.session.commit()

        # Generate initial encryption key
        if not EncryptionKey.query.first():
            admin_user = User.query.filter_by(username='admin').first()
            KeyManager.generate_key(
                name='initial-default-key',
                created_by=admin_user.id if admin_user else None,
                expires_in_days=30
            )

        print('[✓] Database initialized successfully')
        print('[✓] Default users: admin/admin123, analyst/analyst123, operator/operator123')
        print('[✓] Default encryption key generated')


if __name__ == '__main__':
    init_database()
