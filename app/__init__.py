from flask import Flask
from flask_login import LoginManager
from config import Config

# LoginManager mengurus sesi login user
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='../static')
    app.config.from_object(Config)

    # Kalau user belum login terus akses halaman protected, redirect ke sini
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.init_app(app)

    app.jinja_env.globals['enumerate'] = enumerate

    # Daftarkan blueprint (auth & main dipisah biar rapi)
    from app.auth import auth_bp
    from app.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
