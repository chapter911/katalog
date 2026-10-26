from functools import wraps
from flask import session, redirect, url_for, flash, request, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path if request.method == 'GET' else None))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path if request.method == 'GET' else None))
        if session.get('user_role') != 'admin':
            flash('Akses ditolak. Halaman ini hanya dapat diakses oleh Administrator.', 'danger')
            return redirect(url_for('katalog.list_katalog'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' not in session:
        return None
    return {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'nama': session.get('user_name'),
        'identifier': session.get('identifier')
    }
