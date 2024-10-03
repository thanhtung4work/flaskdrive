import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from transformers import pipeline
from werkzeug.security import check_password_hash, generate_password_hash

from server.auth import login_required
from server.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/', methods=['GET'])
@login_required
def index():
    if request.method == 'GET':
        print(*g.get('user'))
        return render_template('user/index.html', data=g.get('user'))


@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.form

    error = None
    try:
        if not check_password_hash(g.user["password"], data.get("oldpassword")):
            error = "Old password not correct!"
        elif not data.get('newpassword') == data.get('repeatpassword'):
            error = "Repeat password not match!"
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET password = ? WHERE username = ?',
                (generate_password_hash(data.get('repeatpassword')), g.user["username"])
            )
            db.commit()
    except Exception as err:
        error = err


    if error:
        flash(error, 'error')
    else:
        flash("Yay", 'info')
    return redirect(url_for('user.index'))

    