"""
Dashboard Routes — System overview statistics and status.
"""

from flask import Blueprint, jsonify
from routes.auth import login_required
from core.audit_logger import AuditLogger
from core.key_manager import KeyManager
from core.gateway import gateway
from models import GatewaySession

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_stats():
    log_stats = AuditLogger.get_stats()
    key_stats = KeyManager.get_key_stats()
    gw_status = gateway.get_status()

    total_sessions = GatewaySession.query.count()
    active_sessions = GatewaySession.query.filter_by(status='ACTIVE').count()

    return jsonify({
        'logs': log_stats,
        'keys': key_stats,
        'gateway': gw_status,
        'sessions': {
            'total': total_sessions,
            'active': active_sessions
        }
    })
