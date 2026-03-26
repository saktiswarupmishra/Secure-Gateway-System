"""
Auth Routes — Login, logout, session management with role-based access.
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from functools import wraps
from models import db, User
from core.audit_logger import AuditLogger

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator: require authenticated session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: require specific role(s)."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            if session.get('role') not in roles:
                username = session.get('username')
                AuditLogger.log(
                    'ACCESS_DENIED',
                    f'User {username} attempted to access restricted resource',
                    source_ip=request.remote_addr,
                    status='FAILURE',
                    user_id=session.get('user_id')
                )
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user and user.is_active and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session.permanent = True

        AuditLogger.log(
            'LOGIN',
            f'User {user.username} logged in successfully',
            source_ip=request.remote_addr,
            user_id=user.id
        )

        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    else:
        AuditLogger.log(
            'LOGIN_FAILED',
            f'Failed login attempt for username: {data.get("username")}',
            source_ip=request.remote_addr,
            status='FAILURE'
        )
        return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    username = session.get('username')
    user_id = session.get('user_id')
    AuditLogger.log(
        'LOGOUT',
        f'User {username} logged out',
        source_ip=request.remote_addr,
        user_id=user_id
    )
    session.clear()
    return jsonify({'success': True})


@auth_bp.route('/api/me', methods=['GET'])
@login_required
def me():
    user = User.query.get(session['user_id'])
    if user:
        return jsonify({'user': user.to_dict()})
    session.clear()
    return jsonify({'error': 'User not found'}), 404
