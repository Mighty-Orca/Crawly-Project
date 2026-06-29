from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, UserMixin
from config import Config
from app import login_manager

auth_bp = Blueprint('auth', __name__)

# -------------------------------------------------------------------
# Model User — Flask-Login butuh class yang implement UserMixin
# Karena kita tidak pakai database, user dibuat manual dari config
# -------------------------------------------------------------------
class User(UserMixin):
    def __init__(self, username):
        self.id = username  # Flask-Login pakai .id sebagai identitas


@login_manager.user_loader
def load_user(user_id):
    """Dipanggil Flask-Login setiap request untuk load user dari session."""
    if user_id in Config.USERS:
        return User(user_id)
    return None


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Cek username & password ke config
        if username in Config.USERS and Config.USERS[username] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Username atau password salah.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
