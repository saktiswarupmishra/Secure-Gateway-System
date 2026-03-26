"""
Gateway Controller — TCP proxy that encrypts outgoing and decrypts incoming traffic.
Runs in a background thread and can be started/stopped via API.
"""

import socket
import threading
import time
from datetime import datetime, timezone
from core.encryption_engine import EncryptionEngine


class GatewayController:
    """TCP proxy gateway with encryption/decryption pipeline."""

    def __init__(self, app=None):
        self.app = app
        self.is_running = False
        self.server_socket = None
        self.thread = None
        self.listen_port = 9000
        self.forward_host = '127.0.0.1'
        self.forward_port = 9001
        self.active_connections = 0
        self.total_sessions = 0
        self.total_bytes = 0
        self.started_at = None
        self.encryption_key = None
        self._stop_event = threading.Event()

    def configure(self, listen_port=None, forward_host=None, forward_port=None, encryption_key=None):
        """Update gateway configuration."""
        if listen_port:
            self.listen_port = int(listen_port)
        if forward_host:
            self.forward_host = forward_host
        if forward_port:
            self.forward_port = int(forward_port)
        if encryption_key:
            self.encryption_key = encryption_key

    def start(self):
        """Start the gateway in a background thread."""
        if self.is_running:
            return {'success': False, 'error': 'Gateway is already running'}

        self._stop_event.clear()
        self.is_running = True
        self.started_at = datetime.now(timezone.utc)
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        return {'success': True, 'message': f'Gateway started on port {self.listen_port}'}

    def stop(self):
        """Stop the gateway."""
        if not self.is_running:
            return {'success': False, 'error': 'Gateway is not running'}

        self._stop_event.set()
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        self.started_at = None
        return {'success': True, 'message': 'Gateway stopped'}

    def get_status(self):
        """Get current gateway status."""
        uptime = None
        if self.started_at:
            delta = datetime.now(timezone.utc) - self.started_at
            uptime = str(delta).split('.')[0]

        return {
            'is_running': self.is_running,
            'listen_port': self.listen_port,
            'forward_host': self.forward_host,
            'forward_port': self.forward_port,
            'active_connections': self.active_connections,
            'total_sessions': self.total_sessions,
            'total_bytes_transferred': self.total_bytes,
            'uptime': uptime,
            'has_encryption_key': self.encryption_key is not None
        }

    def test_encrypt_decrypt(self, data):
        """Test round-trip encryption-decryption with sample data."""
        if not self.encryption_key:
            return {'success': False, 'error': 'No encryption key configured'}

        encrypted = EncryptionEngine.encrypt(data, self.encryption_key)
        if not encrypted['success']:
            return encrypted

        decrypted = EncryptionEngine.decrypt(encrypted['ciphertext'], self.encryption_key)
        if not decrypted['success']:
            return decrypted

        return {
            'success': True,
            'original': data,
            'encrypted': encrypted['ciphertext'],
            'decrypted': decrypted['plaintext'],
            'original_size': encrypted['original_size'],
            'encrypted_size': encrypted['encrypted_size'],
            'integrity_check': data == decrypted['plaintext']
        }

    def _run_server(self):
        """Internal: run the TCP server loop."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)
            self.server_socket.bind(('0.0.0.0', self.listen_port))
            self.server_socket.listen(5)

            while not self._stop_event.is_set():
                try:
                    client_sock, addr = self.server_socket.accept()
                    self.total_sessions += 1
                    self.active_connections += 1
                    handler = threading.Thread(
                        target=self._handle_client,
                        args=(client_sock, addr),
                        daemon=True
                    )
                    handler.start()
                except socket.timeout:
                    continue
                except OSError:
                    break
        except Exception:
            pass
        finally:
            self.is_running = False

    def _handle_client(self, client_sock, addr):
        """Internal: handle a single client connection with encryption pipeline."""
        forward_sock = None
        try:
            forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_sock.connect((self.forward_host, self.forward_port))

            client_sock.settimeout(0.5)
            forward_sock.settimeout(0.5)

            while not self._stop_event.is_set():
                # Client → Encrypt → Forward
                try:
                    data = client_sock.recv(4096)
                    if not data:
                        break
                    self.total_bytes += len(data)
                    if self.encryption_key:
                        encrypted = EncryptionEngine.encrypt_bytes(data, self.encryption_key)
                        if encrypted:
                            forward_sock.sendall(encrypted)
                    else:
                        forward_sock.sendall(data)
                except socket.timeout:
                    pass

                # Forward → Decrypt → Client
                try:
                    data = forward_sock.recv(4096)
                    if not data:
                        break
                    self.total_bytes += len(data)
                    if self.encryption_key:
                        decrypted = EncryptionEngine.decrypt_bytes(data, self.encryption_key)
                        if decrypted:
                            client_sock.sendall(decrypted)
                    else:
                        client_sock.sendall(data)
                except socket.timeout:
                    pass
        except Exception:
            pass
        finally:
            self.active_connections -= 1
            try:
                client_sock.close()
            except Exception:
                pass
            if forward_sock:
                try:
                    forward_sock.close()
                except Exception:
                    pass


# Singleton instance
gateway = GatewayController()
