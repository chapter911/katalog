from flask import Blueprint, render_template, request, redirect, url_for, session, abort, flash
from db import query_db
from auth_helpers import login_required

katalog_bp = Blueprint('katalog', __name__)

@katalog_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('katalog.list_katalog'))
    return redirect(url_for('auth.login'))

@katalog_bp.route('/katalog')
@login_required
def list_katalog():
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        param = f"%{search_query}%"
        sql = """
            SELECT k.id, k.judul, k.deskripsi, k.created_at,
                   COALESCE(thumb.file_path, first_img.file_path) AS thumbnail_path,
                   (SELECT COUNT(*) FROM katalog_gambar WHERE katalog_id = k.id) AS image_count
            FROM katalog k
            LEFT JOIN katalog_gambar thumb ON thumb.katalog_id = k.id AND thumb.is_thumbnail = 1
            LEFT JOIN (
                SELECT kg1.katalog_id, kg1.file_path
                FROM katalog_gambar kg1
                INNER JOIN (
                    SELECT katalog_id, MIN(id) as min_id
                    FROM katalog_gambar
                    GROUP BY katalog_id
                ) kg2 ON kg1.id = kg2.min_id
            ) first_img ON first_img.katalog_id = k.id
            WHERE k.judul LIKE %s OR k.deskripsi LIKE %s
            ORDER BY k.id DESC
        """
        items = query_db(sql, (param, param))
    else:
        sql = """
            SELECT k.id, k.judul, k.deskripsi, k.created_at,
                   COALESCE(thumb.file_path, first_img.file_path) AS thumbnail_path,
                   (SELECT COUNT(*) FROM katalog_gambar WHERE katalog_id = k.id) AS image_count
            FROM katalog k
            LEFT JOIN katalog_gambar thumb ON thumb.katalog_id = k.id AND thumb.is_thumbnail = 1
            LEFT JOIN (
                SELECT kg1.katalog_id, kg1.file_path
                FROM katalog_gambar kg1
                INNER JOIN (
                    SELECT katalog_id, MIN(id) as min_id
                    FROM katalog_gambar
                    GROUP BY katalog_id
                ) kg2 ON kg1.id = kg2.min_id
            ) first_img ON first_img.katalog_id = k.id
            ORDER BY k.id DESC
        """
        items = query_db(sql)

    return render_template('katalog/list.html', items=items, search_query=search_query)

@katalog_bp.route('/katalog/<int:id>')
@login_required
def detail_katalog(id):
    item = query_db(
        """
        SELECT k.*, u.nama as creator_name, u.role as creator_role
        FROM katalog k
        LEFT JOIN users u ON k.created_by = u.id
        WHERE k.id = %s
        """,
        (id,),
        one=True
    )
    
    if not item:
        flash('Item katalog tidak ditemukan.', 'danger')
        return redirect(url_for('katalog.list_katalog'))

    images = query_db(
        """
        SELECT id, katalog_id, file_path, is_thumbnail
        FROM katalog_gambar
        WHERE katalog_id = %s
        ORDER BY is_thumbnail DESC, id ASC
        """,
        (id,)
    )

    return render_template('katalog/detail.html', item=item, images=images)
