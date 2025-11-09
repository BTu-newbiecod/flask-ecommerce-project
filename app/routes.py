from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Product, Category
import unicodedata

bp = Blueprint('main', __name__)

# 🏠 Trang chủ mới (index)
@bp.route('/')
@bp.route('/index')
def index():
    # Trang này có thể chỉ hiển thị banner, giới thiệu, nút đến sản phẩm, v.v.
    return render_template("index.html")


# 🛒 Trang danh sách sản phẩm (được tách riêng)
@bp.route('/product_list')
def product_list():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template("product_list.html", products=products, categories=categories)


# 📄 Chi tiết sản phẩm
@bp.route('/product-<int:id>-<string:slug>')
def product_detail(id, slug):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)


# ✂️ Bỏ dấu tiếng Việt khi tìm kiếm
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


# 🔍 Tìm kiếm sản phẩm
@bp.route('/search', methods=['GET'])
def search_product():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.product_list'))
    
    normal_query = remove_accents(query)

    all_products = Product.query.all()
    products = [
        p for p in all_products 
        if normal_query in remove_accents(p.name.lower())
        or normal_query in remove_accents((p.description or '').lower())
    ]
    categories = Category.query.all()

    return render_template('product_list.html', products=products, query=query, categories=categories)


# 🧭 Lọc sản phẩm theo danh mục / giá
@bp.route('/filter', methods=['GET'])
def filter_product():
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    query = Product.query
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    products = query.all()
    categories = Category.query.all()
    return render_template('product_list.html', products=products, categories=categories)
