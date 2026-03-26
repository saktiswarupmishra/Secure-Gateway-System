"""
Secure Gateway System — Flask Application Entry Point
"""

from flask import Flask, redirect, url_for, session, render_template
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from models import db, User, SystemSetting
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.keys import keys_bp
    from routes.logs import logs_bp
    from routes.gateway_api import gateway_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(keys_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(gateway_bp)
    app.register_blueprint(settings_bp)

    # Create tables on first request
    with app.app_context():
        db.create_all()

        # Seed defaults if empty
        if not User.query.first():
            users = [
                User(username='admin', password_hash=generate_password_hash('admin123'),
                     role='admin', created_at=datetime.now(timezone.utc)),
                User(username='analyst', password_hash=generate_password_hash('analyst123'),
                     role='analyst', created_at=datetime.now(timezone.utc)),
                User(username='operator', password_hash=generate_password_hash('operator123'),
                     role='operator', created_at=datetime.now(timezone.utc)),
            ]
            db.session.add_all(users)

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
                db.session.add(SystemSetting(key=key, value=value))

            db.session.commit()

            # Generate initial key
            from core.key_manager import KeyManager
            admin = User.query.filter_by(username='admin').first()
            KeyManager.generate_key('initial-default-key', created_by=admin.id)

    # Page routes
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return redirect(url_for('dashboard_page'))

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('dashboard.html')

    @app.route('/keys')
    def keys_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('keys.html')

    @app.route('/logs')
    def logs_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('logs.html')

    @app.route('/settings')
    def settings_page():
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('settings.html')

    return app


if __name__ == '__main__':
    app = create_app()
    print('=' * 60)
    print('  SECURE GATEWAY SYSTEM')
    print('  Running on http://localhost:5000')
    print('  Default login: admin / admin123')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
