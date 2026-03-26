"""
Gateway API Routes — Start/stop/status/test for the TCP gateway.
"""

from flask import Blueprint, request, jsonify, session
from routes.auth import login_required, role_required
from core.gateway import gateway
from core.key_manager import KeyManager
from core.audit_logger import AuditLogger

gateway_bp = Blueprint('gateway_api', __name__)


@gateway_bp.route('/api/gateway/status', methods=['GET'])
@login_required
def status():
    return jsonify(gateway.get_status())


@gateway_bp.route('/api/gateway/start', methods=['POST'])
@login_required
@role_required('admin', 'operator')
def start():
    # Load the active encryption key
    active_key = KeyManager.get_active_key()
    if active_key:
        gateway.encryption_key = active_key.key_value

    data = request.get_json(silent=True) or {}
    gateway.configure(
        listen_port=data.get('listen_port'),
        forward_host=data.get('forward_host'),
        forward_port=data.get('forward_port')
    )

    result = gateway.start()

    username = session.get('username')
    AuditLogger.log(
        'GATEWAY_START',
        f'Gateway started on port {gateway.listen_port} by {username}',
        source_ip=request.remote_addr,
        status='SUCCESS' if result['success'] else 'FAILURE',
        user_id=session.get('user_id')
    )

    return jsonify(result)


@gateway_bp.route('/api/gateway/stop', methods=['POST'])
@login_required
@role_required('admin', 'operator')
def stop():
    result = gateway.stop()

    username = session.get('username')
    AuditLogger.log(
        'GATEWAY_STOP',
        f'Gateway stopped by {username}',
        source_ip=request.remote_addr,
        status='SUCCESS' if result['success'] else 'FAILURE',
        user_id=session.get('user_id')
    )

    return jsonify(result)


@gateway_bp.route('/api/gateway/test', methods=['POST'])
@login_required
def test():
    data = request.get_json(silent=True)
    if not data or not data.get('data'):
        return jsonify({'error': 'Test data required'}), 400

    # Use the active key if gateway doesn't have one
    if not gateway.encryption_key:
        active_key = KeyManager.get_active_key()
        if active_key:
            gateway.encryption_key = active_key.key_value
        else:
            return jsonify({'error': 'No encryption key available'}), 400

    result = gateway.test_encrypt_decrypt(data['data'])

    event_type = 'ENCRYPT' if result['success'] else 'ENCRYPT_FAIL'
    AuditLogger.log(
        event_type,
        f'Gateway test: {"passed" if result.get("integrity_check") else "failed"}',
        source_ip=request.remote_addr,
        status='SUCCESS' if result['success'] else 'FAILURE',
        user_id=session.get('user_id')
    )

    return jsonify(result)
