import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)
from pypdf import PdfReader
from transformers import pipeline

from server.auth import login_required
from server.db import get_db


bp = Blueprint('files', __name__, url_prefix='/files')
summarizer = pipeline('summarization', model="Falconsai/text_summarization")


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
    flash('upload failed', 'error')
    return redirect(url_for('files.index'))


@bp.route('/delete/<filename>', methods=['POST', 'GET'])
@login_required
def delete(filename):
    if os.path.exists(
        os.path.join(get_user_folder(), filename)
    ):
        os.remove(os.path.join(get_user_folder(), filename))
        return redirect(url_for('files.index'))
    flash('cannot delete file, try later', 'error')
    return redirect(url_for('files.index'))


@bp.route('/summary/<filename>', methods=['GET', 'POST'])
@login_required
def summary(filename):
    if os.path.exists(
        os.path.join(get_user_folder(), filename)
    ):
        text = ""
        reader = PdfReader(os.path.join('server', 'static', current_app.config['ROOT_DIR'], g.user['username'], filename))
        for page in reader.pages:
            text += page.extract_text()
            break
        
        summarized_text = summarizer(text, max_length=264, min_length=30, do_sample=False)[0]['summary_text']
        flash(f'{filename} summary: {summarized_text}', 'info')
        return redirect(url_for('files.index'))
    flash('cannot summary', 'error')
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