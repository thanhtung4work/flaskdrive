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
    return {"files": os.listdir(get_user_folder())}

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    user_dir = get_user_folder()
    if os.path.exists(user_dir):
        file.save(os.path.join(user_dir, file.filename))
        return {'message': "file uploaded"}, 200
    return {'message': 'upload failed'}, 500


@bp.route('/delete/<filename>', methods=['POST'])
@login_required
def delete(filename):
    if os.path.exists(
        os.path.join(get_user_folder(), filename)
    ):
        os.remove(os.path.join(get_user_folder(), filename))
        return {'message': 'file deleted'}, 200
    return {'message': 'file not found'}, 404


@bp.route('/search/<query>', methods=['POST'])
@login_required
def search(query):
    results = []
    for file in os.listdir(get_user_folder()):
        if query in file:
            results.append(file)
    
    return {"files": results}, 200