import sys
import os

# 1. Pastikan Passenger menggunakan interpreter Python 3.10 dari virtualenv
home_dir = os.path.expanduser("~")
INTERP = os.path.join(home_dir, "virtualenv", "public_html", "diagnostik.agungj.com", "3.10", "bin", "python3")
if not os.path.exists(INTERP):
    INTERP = os.path.join(home_dir, "virtualenv", "public_html", "diagnostik.agungj.com", "3.10", "bin", "python")

if os.path.exists(INTERP) and sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# 2. Pastikan direktori kerja adalah root aplikasi
APP_PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_PATH)
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

# 3. Import aplikasi Flask dengan perlindungan error handler
try:
    from app import app as application
except Exception:
    import traceback
    err_text = traceback.format_exc()
    
    # Catat ke file log
    with open(os.path.join(APP_PATH, "passenger_startup_error.log"), "w", encoding="utf-8") as f:
        f.write(err_text)
        
    def application(environ, start_response):
        status = '500 Internal Server Error'
        error_html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Startup Error</title>"
            "<style>body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; "
            "background: #0f172a; color: #f1f5f9; padding: 30px; }"
            ".card { background: #1e293b; border-radius: 8px; padding: 24px; border: 1px solid #ef4444; max-width: 900px; margin: 0 auto; }"
            "h1 { color: #ef4444; font-size: 20px; margin-top: 0; }"
            "pre { background: #090d16; padding: 16px; border-radius: 6px; overflow-x: auto; color: #fca5a5; font-size: 13px; line-height: 1.5; }"
            "</style></head><body><div class='card'>"
            "<h1>Terjadi Kesalahan saat Memulai Aplikasi (Startup Error)</h1>"
            "<p>Berikut rincian pesan error dari Python:</p>"
            "<pre>" + err_text + "</pre></div></body></html>"
        )
        response_body = error_html.encode('utf-8')
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]


