import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from db import query_db, execute_db, get_db
from auth_helpers import admin_required
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage):
    """Saves a file storage object and returns the filename."""
    original_name = secure_filename(file_storage.filename)
    unique_prefix = uuid.uuid4().hex[:10]
    filename = f"{unique_prefix}_{original_name}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file_storage.save(filepath)
    return filename

def remove_file_from_disk(filename):
    """Safely removes an image file from the upload directory."""
    if not filename:
        return
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass

# ==========================================
# ADMIN DASHBOARD & KATALOG MANAGEMENT
# ==========================================

@admin_bp.route('')
@admin_bp.route('/')
@admin_required
def admin_dashboard():
    return redirect(url_for('admin.list_mahasiswa'))

@admin_bp.route('/katalog/create', methods=['GET', 'POST'])
@admin_required
def create_katalog():
    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        thumbnail_index = request.form.get('thumbnail_index', '0')

        try:
            thumbnail_index = int(thumbnail_index)
        except ValueError:
            thumbnail_index = 0

        files = request.files.getlist('images')
        valid_files = [f for f in files if f and f.filename and allowed_file(f.filename)]

        # Validations
        errors = []
        if not judul:
            errors.append('Judul katalog wajib diisi.')
        if not deskripsi:
            errors.append('Deskripsi katalog wajib diisi.')
        if len(valid_files) < Config.MIN_IMAGES:
            errors.append(f'Harap unggah minimal {Config.MIN_IMAGES} gambar.')
        if len(valid_files) > Config.MAX_IMAGES:
            errors.append(f'Maksimal {Config.MAX_IMAGES} gambar yang dapat diunggah.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('admin/katalog_form.html', judul=judul, deskripsi=deskripsi, mode='create')

        # Make sure thumbnail index is within range
        if thumbnail_index < 0 or thumbnail_index >= len(valid_files):
            thumbnail_index = 0

        # Save to database
        user_id = session.get('user_id')
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO katalog (judul, deskripsi, created_by) VALUES (%s, %s, %s)",
                    (judul, deskripsi, user_id)
                )
                katalog_id = cursor.lastrowid

                # Save and insert images
                for idx, file_obj in enumerate(valid_files):
                    saved_filename = save_uploaded_file(file_obj)
                    is_thumb = 1 if idx == thumbnail_index else 0
                    cursor.execute(
                        "INSERT INTO katalog_gambar (katalog_id, file_path, is_thumbnail) VALUES (%s, %s, %s)",
                        (katalog_id, saved_filename, is_thumb)
                    )

        flash('Item katalog berhasil ditambahkan!', 'success')
        return redirect(url_for('katalog.detail_katalog', id=katalog_id))

    return render_template('admin/katalog_form.html', mode='create')

@admin_bp.route('/katalog/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_katalog(id):
    item = query_db("SELECT * FROM katalog WHERE id = %s", (id,), one=True)
    if not item:
        flash('Item katalog tidak ditemukan.', 'danger')
        return redirect(url_for('katalog.list_katalog'))

    existing_images = query_db(
        "SELECT id, katalog_id, file_path, is_thumbnail FROM katalog_gambar WHERE katalog_id = %s ORDER BY id ASC",
        (id,)
    )

    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        
        # Images marked for deletion
        delete_image_ids = request.form.getlist('delete_image_ids')
        delete_image_ids = [int(img_id) for img_id in delete_image_ids if img_id.isdigit()]
        
        # New uploaded images
        new_files = request.files.getlist('new_images')
        valid_new_files = [f for f in new_files if f and f.filename and allowed_file(f.filename)]
        
        # Selected thumbnail target: format can be "existing_{id}" or "new_{index}"
        chosen_thumb = request.form.get('chosen_thumbnail', '')

        # Calculate remaining existing images
        kept_existing = [img for img in existing_images if img['id'] not in delete_image_ids]
        total_resulting_images = len(kept_existing) + len(valid_new_files)

        errors = []
        if not judul:
            errors.append('Judul katalog wajib diisi.')
        if not deskripsi:
            errors.append('Deskripsi katalog wajib diisi.')
        if total_resulting_images < Config.MIN_IMAGES:
            errors.append(f'Total gambar tidak boleh kurang dari {Config.MIN_IMAGES}. Anda menyisakan {total_resulting_images} gambar.')
        if total_resulting_images > Config.MAX_IMAGES:
            errors.append(f'Total gambar melebihi batas maksimal {Config.MAX_IMAGES}.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('admin/katalog_form.html', item=item, existing_images=existing_images, mode='edit')

        with get_db() as conn:
            with conn.cursor() as cursor:
                # 1. Update title and description
                cursor.execute(
                    "UPDATE katalog SET judul = %s, deskripsi = %s WHERE id = %s",
                    (judul, deskripsi, id)
                )

                # 2. Delete selected images
                if delete_image_ids:
                    # Find filenames to remove from disk
                    format_strings = ','.join(['%s'] * len(delete_image_ids))
                    cursor.execute(
                        f"SELECT file_path FROM katalog_gambar WHERE id IN ({format_strings}) AND katalog_id = %s",
                        tuple(delete_image_ids) + (id,)
                    )
                    to_remove = cursor.fetchall()
                    for row in to_remove:
                        remove_file_from_disk(row['file_path'])

                    cursor.execute(
                        f"DELETE FROM katalog_gambar WHERE id IN ({format_strings}) AND katalog_id = %s",
                        tuple(delete_image_ids) + (id,)
                    )

                # 3. Insert newly uploaded images
                newly_inserted_ids = []
                for idx, file_obj in enumerate(valid_new_files):
                    saved_filename = save_uploaded_file(file_obj)
                    cursor.execute(
                        "INSERT INTO katalog_gambar (katalog_id, file_path, is_thumbnail) VALUES (%s, %s, 0)",
                        (id, saved_filename)
                    )
                    newly_inserted_ids.append((idx, cursor.lastrowid))

                # 4. Set thumbnail flag
                # Reset all to 0 first
                cursor.execute("UPDATE katalog_gambar SET is_thumbnail = 0 WHERE katalog_id = %s", (id,))

                thumbnail_set = False
                if chosen_thumb.startswith('existing_'):
                    thumb_img_id = chosen_thumb.replace('existing_', '')
                    if thumb_img_id.isdigit() and int(thumb_img_id) not in delete_image_ids:
                        cursor.execute(
                            "UPDATE katalog_gambar SET is_thumbnail = 1 WHERE id = %s AND katalog_id = %s",
                            (int(thumb_img_id), id)
                        )
                        thumbnail_set = True
                elif chosen_thumb.startswith('new_'):
                    new_idx = chosen_thumb.replace('new_', '')
                    if new_idx.isdigit():
                        new_idx = int(new_idx)
                        for n_idx, n_id in newly_inserted_ids:
                            if n_idx == new_idx:
                                cursor.execute(
                                    "UPDATE katalog_gambar SET is_thumbnail = 1 WHERE id = %s AND katalog_id = %s",
                                    (n_id, id)
                                )
                                thumbnail_set = True
                                break

                # Fallback: if no thumbnail was explicitly set, set the first image as thumbnail
                if not thumbnail_set:
                    cursor.execute(
                        """
                        UPDATE katalog_gambar SET is_thumbnail = 1 
                        WHERE katalog_id = %s 
                        ORDER BY id ASC LIMIT 1
                        """,
                        (id,)
                    )

        flash('Item katalog berhasil diperbarui!', 'success')
        return redirect(url_for('katalog.detail_katalog', id=id))

    return render_template('admin/katalog_form.html', item=item, existing_images=existing_images, mode='edit')

@admin_bp.route('/katalog/<int:id>/delete', methods=['POST'])
@admin_required
def delete_katalog(id):
    # Fetch all images to clean from disk
    images = query_db("SELECT file_path FROM katalog_gambar WHERE katalog_id = %s", (id,))
    for img in images:
        remove_file_from_disk(img['file_path'])

    # Delete catalog record (cascading deletes katalog_gambar)
    execute_db("DELETE FROM katalog WHERE id = %s", (id,))
    flash('Item katalog beserta gambarnya berhasil dihapus.', 'info')
    return redirect(url_for('katalog.list_katalog'))


# ==========================================
# MAHASISWA MANAGEMENT (Admin only)
# ==========================================

@admin_bp.route('/mahasiswa')
@admin_required
def list_mahasiswa():
    search_query = request.args.get('q', '').strip()
    if search_query:
        param = f"%{search_query}%"
        sql = """
            SELECT m.id, m.user_id, m.nim, m.nama, m.jurusan, m.angkatan, m.email, m.created_at
            FROM mahasiswa m
            WHERE m.nim LIKE %s OR m.nama LIKE %s OR m.jurusan LIKE %s
            ORDER BY m.id DESC
        """
        students = query_db(sql, (param, param, param))
    else:
        sql = """
            SELECT m.id, m.user_id, m.nim, m.nama, m.jurusan, m.angkatan, m.email, m.created_at
            FROM mahasiswa m
            ORDER BY m.id DESC
        """
        students = query_db(sql)

    return render_template('admin/mahasiswa_list.html', students=students, search_query=search_query)

@admin_bp.route('/mahasiswa/create', methods=['GET', 'POST'])
@admin_required
def create_mahasiswa():
    if request.method == 'POST':
        nim = request.form.get('nim', '').strip()
        nama = request.form.get('nama', '').strip()
        jurusan = request.form.get('jurusan', '').strip()
        angkatan = request.form.get('angkatan', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '')

        # Validations
        errors = []
        if not nim:
            errors.append('NIM wajib diisi.')
        if not nama:
            errors.append('Nama lengkap wajib diisi.')
        if not jurusan:
            errors.append('Jurusan wajib diisi.')
        if not angkatan:
            errors.append('Angkatan wajib diisi.')
        if not password:
            errors.append('Password untuk login mahasiswa wajib diisi.')

        # Check existing NIM
        existing_user = query_db("SELECT id FROM users WHERE nim = %s", (nim,), one=True)
        if existing_user:
            errors.append(f"NIM {nim} sudah terdaftar dalam sistem.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('admin/mahasiswa_form.html', mode='create', 
                                   student={'nim': nim, 'nama': nama, 'jurusan': jurusan, 'angkatan': angkatan, 'email': email})

        # Create user and mahasiswa
        password_hash = generate_password_hash(password)
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (username, nim, nama, password_hash, role)
                    VALUES (NULL, %s, %s, %s, 'mahasiswa')
                    """,
                    (nim, nama, password_hash)
                )
                user_id = cursor.lastrowid
                cursor.execute(
                    """
                    INSERT INTO mahasiswa (user_id, nim, nama, jurusan, angkatan, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, nim, nama, jurusan, angkatan, email)
                )

        flash(f'Data mahasiswa {nama} (NIM: {nim}) berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.list_mahasiswa'))

    return render_template('admin/mahasiswa_form.html', mode='create', student={})

@admin_bp.route('/mahasiswa/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_mahasiswa(id):
    student = query_db("SELECT * FROM mahasiswa WHERE id = %s", (id,), one=True)
    if not student:
        flash('Data mahasiswa tidak ditemukan.', 'danger')
        return redirect(url_for('admin.list_mahasiswa'))

    if request.method == 'POST':
        nim = request.form.get('nim', '').strip()
        nama = request.form.get('nama', '').strip()
        jurusan = request.form.get('jurusan', '').strip()
        angkatan = request.form.get('angkatan', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '').strip()

        errors = []
        if not nim:
            errors.append('NIM wajib diisi.')
        if not nama:
            errors.append('Nama lengkap wajib diisi.')
        if not jurusan:
            errors.append('Jurusan wajib diisi.')
        if not angkatan:
            errors.append('Angkatan wajib diisi.')

        # If NIM changed, check duplicate
        if nim != student['nim']:
            existing = query_db("SELECT id FROM users WHERE nim = %s AND id != %s", (nim, student['user_id']), one=True)
            if existing:
                errors.append(f"NIM {nim} sudah digunakan oleh pengguna lain.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('admin/mahasiswa_form.html', mode='edit', 
                                   student={'id': id, 'user_id': student['user_id'], 'nim': nim, 'nama': nama, 'jurusan': jurusan, 'angkatan': angkatan, 'email': email})

        with get_db() as conn:
            with conn.cursor() as cursor:
                # Update mahasiswa table
                cursor.execute(
                    """
                    UPDATE mahasiswa 
                    SET nim = %s, nama = %s, jurusan = %s, angkatan = %s, email = %s
                    WHERE id = %s
                    """,
                    (nim, nama, jurusan, angkatan, email, id)
                )

                # Update users table
                if password:
                    pass_hash = generate_password_hash(password)
                    cursor.execute(
                        "UPDATE users SET nim = %s, nama = %s, password_hash = %s WHERE id = %s",
                        (nim, nama, pass_hash, student['user_id'])
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET nim = %s, nama = %s WHERE id = %s",
                        (nim, nama, student['user_id'])
                    )

        flash(f'Data mahasiswa {nama} berhasil diperbarui.', 'success')
        return redirect(url_for('admin.list_mahasiswa'))

    return render_template('admin/mahasiswa_form.html', mode='edit', student=student)

@admin_bp.route('/mahasiswa/<int:id>/delete', methods=['POST'])
@admin_required
def delete_mahasiswa(id):
    student = query_db("SELECT user_id, nama FROM mahasiswa WHERE id = %s", (id,), one=True)
    if student:
        # Deleting user will cascade delete mahasiswa
        execute_db("DELETE FROM users WHERE id = %s", (student['user_id'],))
        flash(f'Data mahasiswa {student["nama"]} berhasil dihapus.', 'info')
    else:
        flash('Data mahasiswa tidak ditemukan.', 'danger')
        
    return redirect(url_for('admin.list_mahasiswa'))
