"""
Logging & Auditing Module — Comprehensive event logging for security analysis.
"""

from datetime import datetime, timezone
from models import db, AuditLog


class AuditLogger:
    """Handles all transaction and event logging."""

    EVENT_TYPES = [
        'LOGIN', 'LOGOUT', 'LOGIN_FAILED',
        'ENCRYPT', 'DECRYPT', 'ENCRYPT_FAIL', 'DECRYPT_FAIL',
        'KEY_GENERATE', 'KEY_ROTATE', 'KEY_DELETE', 'KEY_DEACTIVATE',
        'GATEWAY_START', 'GATEWAY_STOP',
        'SETTING_CHANGE', 'CONFIG_UPDATE',
        'ACCESS_DENIED', 'SYSTEM_ERROR', 'SYSTEM_INFO'
    ]

    @staticmethod
    def log(event_type, message='', source_ip=None, dest_ip=None, status='SUCCESS', user_id=None):
        """
        Log an audit event to the database.

        Args:
            event_type: type of event (see EVENT_TYPES)
            message: human-readable description
            source_ip: source IP address
            dest_ip: destination IP address
            status: SUCCESS, FAILURE, or WARNING
            user_id: ID of user who triggered the event
        """
        try:
            entry = AuditLog(
                timestamp=datetime.now(timezone.utc),
                event_type=event_type,
                source_ip=source_ip,
                dest_ip=dest_ip,
                status=status,
                message=message,
                user_id=user_id
            )
            db.session.add(entry)
            db.session.commit()
            return entry
        except Exception as e:
            db.session.rollback()
            print(f'[AuditLogger] Error logging event: {e}')
            return None

    @staticmethod
    def get_logs(page=1, per_page=50, event_type=None, status=None, search=None):
        """
        Get paginated and filtered audit logs.

        Returns:
            dict with 'logs', 'total', 'page', 'pages'
        """
        query = AuditLog.query.order_by(AuditLog.timestamp.desc())

        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if status:
            query = query.filter(AuditLog.status == status)
        if search:
            query = query.filter(AuditLog.message.contains(search))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'logs': [log.to_dict() for log in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @staticmethod
    def get_stats():
        """Get aggregated log statistics for the dashboard."""
        total = AuditLog.query.count()
        success = AuditLog.query.filter_by(status='SUCCESS').count()
        failure = AuditLog.query.filter_by(status='FAILURE').count()
        warning = AuditLog.query.filter_by(status='WARNING').count()

        # Recent activity counts by event type
        encryptions = AuditLog.query.filter_by(event_type='ENCRYPT').count()
        decryptions = AuditLog.query.filter_by(event_type='DECRYPT').count()
        logins = AuditLog.query.filter_by(event_type='LOGIN').count()
        key_ops = AuditLog.query.filter(
            AuditLog.event_type.in_(['KEY_GENERATE', 'KEY_ROTATE', 'KEY_DELETE'])
        ).count()

        # Last 10 events for recent activity
        recent = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

        return {
            'total_events': total,
            'success_count': success,
            'failure_count': failure,
            'warning_count': warning,
            'encryption_count': encryptions,
            'decryption_count': decryptions,
            'login_count': logins,
            'key_operations': key_ops,
            'recent_events': [r.to_dict() for r in recent]
        }

    @staticmethod
    def get_event_types():
        """Return all supported event types."""
        return AuditLogger.EVENT_TYPES

    @staticmethod
    def export_logs_csv(event_type=None, status=None):
        """Export logs as CSV string."""
        query = AuditLog.query.order_by(AuditLog.timestamp.desc())
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if status:
            query = query.filter(AuditLog.status == status)

        logs = query.all()
        lines = ['ID,Timestamp,EventType,SourceIP,DestIP,Status,Message,UserID']
        for log in logs:
            lines.append(
                f'{log.id},{log.timestamp},{log.event_type},'
                f'{log.source_ip or ""},{log.dest_ip or ""},{log.status},'
                f'"{(log.message or "").replace(chr(34), chr(39))}",{log.user_id or ""}'
            )
        return '\n'.join(lines)
