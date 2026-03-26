"""
Key Management System — Generate, store, rotate, and manage encryption keys.
"""

from datetime import datetime, timedelta, timezone
from models import db, EncryptionKey
from core.encryption_engine import EncryptionEngine


class KeyManager:
    """Manages cryptographic key lifecycle."""

    @staticmethod
    def generate_key(name, created_by=None, expires_in_days=30):
        """
        Generate a new encryption key and store it in the database.

        Args:
            name: human-readable key name
            created_by: user ID who created the key
            expires_in_days: days until key expires

        Returns:
            EncryptionKey model instance
        """
        key_value = EncryptionEngine.generate_key()
        now = datetime.now(timezone.utc)

        new_key = EncryptionKey(
            key_name=name,
            key_value=key_value,
            algorithm='AES-128-CBC (Fernet)',
            created_at=now,
            expires_at=now + timedelta(days=expires_in_days) if expires_in_days else None,
            is_active=True,
            created_by=created_by
        )
        db.session.add(new_key)
        db.session.commit()
        return new_key

    @staticmethod
    def get_active_key():
        """Get the most recently created active key."""
        return EncryptionKey.query.filter_by(is_active=True).order_by(
            EncryptionKey.created_at.desc()
        ).first()

    @staticmethod
    def get_all_keys():
        """Get all keys ordered by creation date."""
        return EncryptionKey.query.order_by(EncryptionKey.created_at.desc()).all()

    @staticmethod
    def get_key_by_id(key_id):
        """Get a specific key by ID."""
        return EncryptionKey.query.get(key_id)

    @staticmethod
    def deactivate_key(key_id):
        """Deactivate a key (soft delete)."""
        key = EncryptionKey.query.get(key_id)
        if key:
            key.is_active = False
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_key(key_id):
        """Permanently delete a key."""
        key = EncryptionKey.query.get(key_id)
        if key:
            db.session.delete(key)
            db.session.commit()
            return True
        return False

    @staticmethod
    def rotate_key(created_by=None):
        """
        Rotate keys: deactivate all current keys and generate a new one.

        Returns:
            The newly created EncryptionKey
        """
        # Deactivate all current active keys
        active_keys = EncryptionKey.query.filter_by(is_active=True).all()
        for k in active_keys:
            k.is_active = False

        # Generate new key
        new_key = KeyManager.generate_key(
            name=f'rotated-key-{datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")}',
            created_by=created_by
        )
        return new_key

    @staticmethod
    def check_expired_keys():
        """Check and deactivate any expired keys."""
        now = datetime.now(timezone.utc)
        expired = EncryptionKey.query.filter(
            EncryptionKey.is_active == True,
            EncryptionKey.expires_at != None,
            EncryptionKey.expires_at < now
        ).all()
        for k in expired:
            k.is_active = False
        if expired:
            db.session.commit()
        return len(expired)

    @staticmethod
    def get_key_stats():
        """Get key statistics for the dashboard."""
        total = EncryptionKey.query.count()
        active = EncryptionKey.query.filter_by(is_active=True).count()
        now = datetime.now(timezone.utc)
        expiring_soon = EncryptionKey.query.filter(
            EncryptionKey.is_active == True,
            EncryptionKey.expires_at != None,
            EncryptionKey.expires_at < now + timedelta(days=7)
        ).count()
        return {
            'total_keys': total,
            'active_keys': active,
            'inactive_keys': total - active,
            'expiring_soon': expiring_soon
        }
