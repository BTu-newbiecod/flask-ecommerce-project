
from flask import Blueprint, render_template


bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    return "<h1>BTL_PyPy</h1>"