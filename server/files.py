import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)

from server.auth import login_required
from server.db import get_db

bp = Blueprint('files', __name__, url_prefix='/files')


@login_required
def get_user_folder():
    return os.path.join('server', 'static', current_app.config['ROOT_DIR'], g.user['username'])

@bp.route('/')
@login_required
def index():
    files = os.listdir(get_user_folder())
    return render_template('files/index.html', data=files)

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file-upload']
    user_dir = get_user_folder()
    if os.path.exists(user_dir):
        file.save(os.path.join(user_dir, file.filename))
        return redirect(url_for('files.index'))
    flash('upload failed')
    return redirect(url_for('files.index'))


@bp.route('/delete/<filename>', methods=['POST', 'GET'])
@login_required
def delete(filename):
    if os.path.exists(
        os.path.join(get_user_folder(), filename)
    ):
        os.remove(os.path.join(get_user_folder(), filename))
        return redirect(url_for('files.index'))
    flash('cannot delete file, try later')
    return redirect(url_for('files.index'))


@bp.route('/summary/<filename>', methods=['GET', 'POST'])
@login_required
def summary(filename):
    if os.path.exists(
        os.path.join(get_user_folder(), filename)
    ):
        flash('summary content go here')
        return redirect(url_for('files.index'))
    flash('cannot summary')
    return redirect(url_for('files.index'))


@bp.route('/search', methods=['POST'])
@login_required
def search():
    data = request.form

    results = []
    for file in os.listdir(get_user_folder()):
        if data['query'] in file:
            results.append(file)
    
    return render_template("files/index.html", data=results)