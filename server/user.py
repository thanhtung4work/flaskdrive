import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from transformers import pipeline

from server.auth import login_required


bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/', methods=['GET'])
@login_required
def index():
    if request.method == 'GET':
        print(*g.get('user'))
        return render_template('user/index.html', data=g.get('user'))