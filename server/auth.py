import functools
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from server.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    
    username = data.get('username', None)
    password = data.get('password', None)
    db = get_db()

    if not username:
        error = 'username is required'
        return {
            'message': error
        }, 500
    if not password:
        error = 'password is required'
        return {
            'message': error
        }, 500
    
    try:
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        db.commit()
        user_folder = os.path.join('server', 'static', current_app.config['ROOT_DIR'], username)
        os.mkdir(user_folder)
    except Exception as er:
        error = f"User {username} is already registered."
        print(er)
        print(os.path.abspath(os.path.curdir))
        return {
            'message': error
        }, 500

    return {
        'message': 'registeration successfull'
    }


@bp.route('login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    
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
        return {'message': 'login successful'}, 200
    
    return {'message': error}, 500


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
            return {'message': 'login required'}
        return view(**kwargs)
    return wrapped_view


@bp.route('logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return {'message': 'logout'}, 200