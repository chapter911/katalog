import sys
import os

# Menambahkan direktori aplikasi ke dalam sys.path
APP_PATH = os.path.dirname(os.path.abspath(__file__))
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

# Mengimpor instance aplikasi Flask sebagai 'application' (standar WSGI Passenger cPanel)
from app import app as application
