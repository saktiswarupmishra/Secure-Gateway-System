"""
Log Routes — Paginated audit log retrieval and CSV export.
"""

from flask import Blueprint, request, jsonify, Response
from routes.auth import login_required
from core.audit_logger import AuditLogger

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    event_type = request.args.get('event_type', None)
    status = request.args.get('status', None)
    search = request.args.get('search', None)

    result = AuditLogger.get_logs(
        page=page,
        per_page=per_page,
        event_type=event_type,
        status=status,
        search=search
    )
    return jsonify(result)


@logs_bp.route('/api/logs/stats', methods=['GET'])
@login_required
def log_stats():
    stats = AuditLogger.get_stats()
    return jsonify(stats)


@logs_bp.route('/api/logs/event-types', methods=['GET'])
@login_required
def event_types():
    return jsonify({'event_types': AuditLogger.get_event_types()})


@logs_bp.route('/api/logs/export', methods=['GET'])
@login_required
def export_logs():
    event_type = request.args.get('event_type', None)
    status = request.args.get('status', None)

    csv_data = AuditLogger.export_logs_csv(event_type=event_type, status=status)

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=audit_logs.csv'}
    )
