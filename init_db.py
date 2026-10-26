import os
import pymysql
from werkzeug.security import generate_password_hash
from config import Config

def init_database():
    print(f"Connecting to MySQL server at {Config.DB_HOST}:{Config.DB_PORT} as {Config.DB_USER}...")
    
    conn = None
    try:
        # Connect directly specifying database (cPanel shared hosting standard)
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4'
        )
        print(f"Connected to database `{Config.DB_NAME}` successfully.")
    except pymysql.err.OperationalError as e:
        # If database unknown (error 1049, e.g. local development), attempt to create it
        if e.args[0] == 1049:
            print(f"Database `{Config.DB_NAME}` not found. Attempting to create (local dev)...")
            temp_conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                charset='utf8mb4'
            )
            with temp_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            temp_conn.commit()
            temp_conn.close()
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset='utf8mb4'
            )
        else:
            raise
    
    try:
        with conn.cursor() as cursor:
            # Execute schema.sql
            schema_path = os.path.join(Config.BASE_DIR, 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Split and execute statements, ignoring any CREATE DATABASE or USE
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                for stmt in statements:
                    cleaned_stmt = stmt.strip()
                    upper_stmt = cleaned_stmt.upper()
                    if upper_stmt.startswith('CREATE DATABASE') or upper_stmt.startswith('USE '):
                        continue
                    cursor.execute(cleaned_stmt)
                print("Database schema successfully applied.")
            
            # Check or Seed Default Admin
            cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
            admin_row = cursor.fetchone()
            if not admin_row:
                admin_pass = generate_password_hash('admin123')
                cursor.execute(
                    """
                    INSERT INTO users (username, nim, nama, password_hash, role)
                    VALUES (%s, NULL, %s, %s, %s)
                    """,
                    ('admin', 'Administrator Sistem', admin_pass, 'admin')
                )
                admin_id = cursor.lastrowid
                print(f"Default admin created (Username: admin | Password: admin123 | ID: {admin_id})")
            else:
                admin_id = admin_row[0]

            # Check or Seed Mahasiswa 1
            cursor.execute("SELECT id FROM users WHERE nim = %s", ('2024001',))
            mhs1_user = cursor.fetchone()
            if not mhs1_user:
                mhs1_pass = generate_password_hash('mhs123')
                cursor.execute(
                    """
                    INSERT INTO users (username, nim, nama, password_hash, role)
                    VALUES (NULL, %s, %s, %s, %s)
                    """,
                    ('2024001', 'Ahmad Fauzi', mhs1_pass, 'mahasiswa')
                )
                mhs1_user_id = cursor.lastrowid
                cursor.execute(
                    """
                    INSERT INTO mahasiswa (user_id, nim, nama, jurusan, angkatan, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (mhs1_user_id, '2024001', 'Ahmad Fauzi', 'Teknik Informatika', '2024', 'ahmad.fauzi@kampus.ac.id')
                )
                print("Sample Mahasiswa 1 created (NIM: 2024001 | Password: mhs123)")

            # Check or Seed Mahasiswa 2
            cursor.execute("SELECT id FROM users WHERE nim = %s", ('2024002',))
            mhs2_user = cursor.fetchone()
            if not mhs2_user:
                mhs2_pass = generate_password_hash('mhs123')
                cursor.execute(
                    """
                    INSERT INTO users (username, nim, nama, password_hash, role)
                    VALUES (NULL, %s, %s, %s, %s)
                    """,
                    ('2024002', 'Siti Nurhaliza', mhs2_pass, 'mahasiswa')
                )
                mhs2_user_id = cursor.lastrowid
                cursor.execute(
                    """
                    INSERT INTO mahasiswa (user_id, nim, nama, jurusan, angkatan, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (mhs2_user_id, '2024002', 'Siti Nurhaliza', 'Sistem Informasi', '2024', 'siti.nur@kampus.ac.id')
                )
                print("Sample Mahasiswa 2 created (NIM: 2024002 | Password: mhs123)")

            # Ensure upload folder exists with .gitkeep
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            gitkeep_path = os.path.join(Config.UPLOAD_FOLDER, '.gitkeep')
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    pass

            print("Katalog initialized clean: 0 items (ready for admin input).")
        conn.commit()
        print("Database initialization completed successfully!")
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
