"""
Settings Routes — Read and update system configuration.
"""

from flask import Blueprint, request, jsonify, session
from routes.auth import login_required, role_required
from models import db, SystemSetting
from core.audit_logger import AuditLogger

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    settings = SystemSetting.query.all()
    result = {s.key: s.value for s in settings}
    return jsonify(result)


@settings_bp.route('/api/settings', methods=['POST'])
@login_required
@role_required('admin')
def update_settings():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No settings provided'}), 400

    updated = []
    for key, value in data.items():
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            old_value = setting.value
            setting.value = str(value)
            updated.append(f'{key}: {old_value} → {value}')
        else:
            new_setting = SystemSetting(key=key, value=str(value))
            db.session.add(new_setting)
            updated.append(f'{key}: (new) {value}')

    db.session.commit()

    username = session.get('username')
    AuditLogger.log(
        'SETTING_CHANGE',
        f'Settings updated by {username}: {"; ".join(updated)}',
        source_ip=request.remote_addr,
        user_id=session.get('user_id')
    )

    return jsonify({'success': True, 'updated': updated})
