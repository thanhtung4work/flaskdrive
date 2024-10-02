import io
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory, send_file
)
from minio import Minio
from pypdf import PdfReader
from transformers import pipeline

from server.auth import login_required


bp = Blueprint('files', __name__, url_prefix='/files')
summarizer = pipeline('summarization', model="Falconsai/text_summarization")
client = Minio("172.16.87.78:9000", "BSEPODhrOEBLStG0ayH3", "VGK8itE1lrN4AB6IDRyYNwnzxWd75dPToRzyfEn1", secure=False)


@login_required
def get_user_folder(include_app=True):
    if not include_app:
        return os.path.join('static', current_app.config['ROOT_DIR'], g.user['username'])
    return os.path.join('server', 'static', current_app.config['ROOT_DIR'], g.user['username'])

@bp.route('/')
@login_required
def index():
    # files = os.listdir(get_user_folder())
    files = client.list_objects(g.user['username'])
    return render_template('files/index.html', data=[file.object_name for file in files])

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file-upload']
    # user_dir = get_user_folder()
    # if os.path.exists(user_dir):
    #     file.save(os.path.join(user_dir, file.filename))
    #     return redirect(url_for('files.index'))
    
    try:
        size = os.fstat(file.fileno()).st_size
        client.put_object(g.user['username'], file.filename, file, size)
    except:
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
    # if os.path.exists(
    #     os.path.join(get_user_folder(), filename)
    # ):
    #     text = ""
    #     reader = PdfReader(os.path.join('server', 'static', current_app.config['ROOT_DIR'], g.user['username'], filename))
    #     for page in reader.pages:
    #         text += page.extract_text().lower()
    #         break
        
    #     summarized_text = summarizer(text, max_length=264, min_length=30, do_sample=False)[0]['summary_text']
    #     flash(f'{filename} summary: {summarized_text}', 'info')
    #     return redirect(url_for('files.index'))
    try:
        response = client.get_object(g.user['username'], filename)
        
        text=""
        reader = PdfReader(io.BytesIO(response.data))
        for page in reader.pages:
            text += page.extract_text().lower()
            break
        
        summarized_text = summarizer(text, max_length=264, min_length=30, do_sample=False)[0]['summary_text']
        flash(f'{filename} summary: {summarized_text}', 'info')
    except Exception as err:
        flash('cannot summary', 'error')
        print(err)
    return redirect(url_for('files.index'))


@bp.route('/search', methods=['POST'])
@login_required
def search():
    data = request.form

    results = []
    # for file in os.listdir(get_user_folder()):
    #     if data['query'] in file:
    #         results.append(file)

    files = client.list_objects(g.user['username'])
    for file in files:
        if data['query'] in file.object_name:
            results.append(file.object_name)
    
    return render_template("files/index.html", data=results)

@bp.route('/rename/<filename>', methods=['POST'])
@login_required
def rename(filename):
    data = request.form

    user_dir = get_user_folder()
    ext = os.path.splitext(filename)[-1]
    try:
        os.rename(
            src=os.path.join(user_dir, filename),
            dst=os.path.join(user_dir, data['newname'] + ext),
        )
    except Exception as err:
        flash(err, 'error')
    
    return redirect(url_for('.index'))


@bp.route('/download/<filename>', methods=['GET'])
@login_required
def download(filename):
    user_dir = get_user_folder(include_app=False)
    print(user_dir, filename)
    return send_from_directory(user_dir, filename, as_attachment=True)