import functools
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from minio import Minio
from werkzeug.security import check_password_hash, generate_password_hash

from server.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")

# client = Minio("172.16.87.78:9000", "iPdKcoWd5HxqQbi3oXgR", "Ckvx23r2hgYlSclNysgXT3W1IuACeT62qM1nETM6", secure=False)
client = Minio(MINIO_ENDPOINT, ACCESS_KEY, SECRET_KEY, secure=False)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    data = request.form
    
    username = data.get('username', None)
    password = data.get('password', None)
    db = get_db()

    error = None

    if not username:
        error = 'username is required'
    if not password:
        error = 'password is required'
    
    if error is None:
        try:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            user_folder = os.path.join('server', 'static', current_app.config['ROOT_DIR'], username)
            
            # os.mkdir(user_folder)
            client.make_bucket(username)


        except Exception as er:
            error = f'User {username} is already registered.'
        else:
            return redirect(url_for("auth.login"))
    
    flash(error, 'error')
    return render_template('auth/register.html')


@bp.route('login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': 
        return render_template('auth/login.html')
    
    data = request.form
    
    username = data.get('username', None)
    password = data.get('password', None)
    db = get_db()
    
    error = None
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username, )
    ).fetchone()

    if user is None:
        error = 'Incorrect username'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password'
    
    if error is None:
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('files.index'))
    
    flash(error, 'error')
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@bp.route('logout', methods=['POST', 'GET'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))