"""
Encryption Engine — AES-based symmetric encryption using Fernet.
Fernet uses AES-128-CBC with HMAC-SHA256 for authenticated encryption.
"""

from cryptography.fernet import Fernet, InvalidToken
import base64
import os


class EncryptionEngine:
    """Handles all encryption and decryption operations."""

    @staticmethod
    def generate_key():
        """Generate a new Fernet-compatible encryption key."""
        return Fernet.generate_key().decode('utf-8')

    @staticmethod
    def encrypt(plaintext, key):
        """
        Encrypt plaintext data using AES (Fernet).

        Args:
            plaintext: str or bytes to encrypt
            key: Fernet key string

        Returns:
            dict with 'ciphertext' (base64 string) and 'success' bool
        """
        try:
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
            if isinstance(key, str):
                key = key.encode('utf-8')

            f = Fernet(key)
            encrypted = f.encrypt(plaintext)
            return {
                'success': True,
                'ciphertext': encrypted.decode('utf-8'),
                'original_size': len(plaintext),
                'encrypted_size': len(encrypted)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def decrypt(ciphertext, key):
        """
        Decrypt ciphertext data using AES (Fernet).

        Args:
            ciphertext: encrypted string (base64)
            key: Fernet key string

        Returns:
            dict with 'plaintext' and 'success' bool
        """
        try:
            if isinstance(ciphertext, str):
                ciphertext = ciphertext.encode('utf-8')
            if isinstance(key, str):
                key = key.encode('utf-8')

            f = Fernet(key)
            decrypted = f.decrypt(ciphertext)
            return {
                'success': True,
                'plaintext': decrypted.decode('utf-8'),
                'encrypted_size': len(ciphertext),
                'decrypted_size': len(decrypted)
            }
        except InvalidToken:
            return {
                'success': False,
                'error': 'Invalid token — data may be corrupted or wrong key used'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def encrypt_bytes(data, key):
        """Encrypt raw bytes (for binary/stream data)."""
        try:
            if isinstance(key, str):
                key = key.encode('utf-8')
            f = Fernet(key)
            encrypted = f.encrypt(data)
            return encrypted
        except Exception:
            return None

    @staticmethod
    def decrypt_bytes(data, key):
        """Decrypt raw bytes back to original."""
        try:
            if isinstance(key, str):
                key = key.encode('utf-8')
            f = Fernet(key)
            decrypted = f.decrypt(data)
            return decrypted
        except Exception:
            return None

    @staticmethod
    def validate_key(key):
        """Check if a key is a valid Fernet key."""
        try:
            if isinstance(key, str):
                key = key.encode('utf-8')
            Fernet(key)
            return True
        except Exception:
            return False
