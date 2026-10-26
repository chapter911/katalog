import os
from flask import Flask, render_template
from config import Config
from auth_helpers import get_current_user

# Import Blueprints
from routes.auth import auth_bp
from routes.katalog import katalog_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.url_map.strict_slashes = False

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(katalog_bp)
    app.register_blueprint(admin_bp)

    # Context Processor for Global Variables in Templates
    @app.context_processor
    def inject_globals():
        return {
            'current_user': get_current_user(),
            'app_name': 'Laboratorium Peralatan Diagnostik'
        }

    # Favicon handler to avoid 404 noise
    @app.route('/favicon.ico')
    def favicon():
        return ('', 204)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_code=404, error_message='Halaman yang Anda tuju tidak ditemukan.'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('base.html', error_code=413, error_message='Ukuran berkas unggahan melebihi batas maksimal (20MB).'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_code=500, error_message='Terjadi kendala pada server. Silakan coba sesaat lagi.'), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
