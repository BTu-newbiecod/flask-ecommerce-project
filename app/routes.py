
from flask import Blueprint, render_template
from app.models import Product

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    products = Product.query.all()
    return render_template("index.html", products = products)


@bp.route('/product-<int:id>-<string:slug>')
def product_detail(id, slug):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)