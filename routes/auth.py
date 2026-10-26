from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from db import query_db, execute_db
from auth_helpers import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('katalog.list_katalog'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash('Harap masukkan Username/NIM dan Password.', 'warning')
            return render_template('login.html', identifier=identifier)

        # Lookup by username (for admin) or nim (for mahasiswa)
        user = query_db(
            "SELECT id, username, nim, nama, password_hash, role FROM users WHERE username = %s OR nim = %s",
            (identifier, identifier),
            one=True
        )

        if user and check_password_hash(user['password_hash'], password):
            # Session assignment
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['user_name'] = user['nama']
            session['identifier'] = user['username'] if user['role'] == 'admin' else user['nim']
            
            flash(f"Selamat datang, {user['nama']}! Anda masuk sebagai {user['role'].title()}.", 'success')
            
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('katalog.list_katalog'))
        else:
            flash('Username/NIM atau password yang Anda masukkan salah.', 'danger')
            return render_template('login.html', identifier=identifier)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil keluar dari sistem.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/update-password', methods=['GET', 'POST'])
@login_required
def update_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not current_password:
            errors.append('Password saat ini wajib diisi.')
        if not new_password:
            errors.append('Password baru wajib diisi.')
        elif len(new_password) < 6:
            errors.append('Password baru minimal harus terdiri dari 6 karakter.')
        if new_password != confirm_password:
            errors.append('Konfirmasi password baru tidak cocok.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('update_password.html')

        user_id = session.get('user_id')
        user = query_db("SELECT password_hash FROM users WHERE id = %s", (user_id,), one=True)

        if not user or not check_password_hash(user['password_hash'], current_password):
            flash('Password saat ini yang Anda masukkan salah.', 'danger')
            return render_template('update_password.html')

        # Update password hash
        new_hash = generate_password_hash(new_password)
        execute_db("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))

        flash('Password Anda berhasil diperbarui! Silakan gunakan password baru ini pada sesi berikutnya.', 'success')
        return redirect(url_for('katalog.list_katalog'))

    return render_template('update_password.html')
