import sys
import os

# 1. Pastikan direktori kerja adalah root aplikasi
APP_PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_PATH)
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

# 2. Tambahkan site-packages virtualenv ke sys.path secara aman
home_dir = os.path.expanduser("~")
venv_base = os.path.join(home_dir, "virtualenv", "public_html", "diagnostik.agungj.com", "3.10", "lib")
if os.path.exists(venv_base):
    for folder in os.listdir(venv_base):
        sp = os.path.join(venv_base, folder, "site-packages")
        if os.path.exists(sp) and sp not in sys.path:
            sys.path.insert(0, sp)

# 3. Import aplikasi Flask sebagai 'application' (standar WSGI Passenger cPanel)
from app import app as application



