from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')  # admin, analyst, operator
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }


class EncryptionKey(db.Model):
    __tablename__ = 'encryption_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(120), nullable=False)
    key_value = db.Column(db.Text, nullable=False)  # Fernet key (base64)
    algorithm = db.Column(db.String(50), default='AES-128-CBC (Fernet)')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'key_name': self.key_name,
            'key_preview': self.key_value[:12] + '...' if self.key_value else '',
            'algorithm': self.algorithm,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'created_by': self.created_by
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    event_type = db.Column(db.String(50), nullable=False)  # ENCRYPT, DECRYPT, KEY_GEN, LOGIN, etc.
    source_ip = db.Column(db.String(45), nullable=True)
    dest_ip = db.Column(db.String(45), nullable=True)
    status = db.Column(db.String(20), default='SUCCESS')  # SUCCESS, FAILURE, WARNING
    message = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'source_ip': self.source_ip,
            'dest_ip': self.dest_ip,
            'status': self.status,
            'message': self.message,
            'user_id': self.user_id
        }


class GatewaySession(db.Model):
    __tablename__ = 'gateway_sessions'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = db.Column(db.DateTime, nullable=True)
    bytes_transferred = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, CLOSED, ERROR

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'destination': self.destination,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'bytes_transferred': self.bytes_transferred,
            'status': self.status
        }


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }
