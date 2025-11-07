from flask import render_template, redirect, url_for, Blueprint, request, current_app
from flask_login import login_required, current_user
from app.admin import bp
from functools import wraps
from app.models import db, Order, Product, Category, OrderStatus
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.email == "admin@shop.com"):
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    now = datetime.now()

    # Doanh thu tháng hiện tại
    revenue_current_month = db.session.query(func.sum(Order.total_amount)) \
    .filter(
        extract('year', Order.order_date) == now.year,
        extract('month', Order.order_date) == now.month,
        Order.status == OrderStatus.COMPLETED  # Chỉ tính đơn hàng Completed
    ) \
    .scalar() or 0

    # Đơn hàng Pending
    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).order_by(Order.order_date.desc()).all()

    # Đơn hàng Shipping
    shipping_orders = Order.query.filter_by(status=OrderStatus.SHIPPING).order_by(Order.order_date.desc()).all()

    # Số lượng sản phẩm theo danh mục
    product_counts = db.session.query(
        Category.name,
        func.sum(Product.stock)
    ).join(Product).group_by(Category.id).all()

    return render_template(
        'admin/admin_base.html',
        revenue_current_month=revenue_current_month,
        pending_orders=pending_orders,
        shipping_orders=shipping_orders,
        product_counts=product_counts
    )
#Xem danh sach
@bp.route('/products')
@admin_required
@login_required
def products(): 
    products = Product.query.order_by(Product.id.desc()).all()  
    return render_template('admin/products.html', products=products)

#Form chinh sua
@bp.route('/product_form/<int:product_id>')
@admin_required
@login_required
def product_form(product_id):
    if product_id == 0:
        # Trả về form rỗng cho thêm mới
        return render_template('admin/product_form.html', product=None, categories=Category.query.all())
    product = Product.query.get_or_404(product_id)
    return render_template('admin/product_form.html', product=product, categories=Category.query.all())

#Thao tac
@bp.route('/add_product', methods=['POST'])
@login_required
@admin_required
def add_product():
    # Lấy dữ liệu form, kèm fallback tránh lỗi None
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price_str = request.form.get('price')
    stock_str = request.form.get('stock')
    category_str = request.form.get('category')

    # Kiểm tra dữ liệu bắt buộc
    if not name or not price_str or not stock_str or not category_str:
        return "Thiếu dữ liệu bắt buộc", 400

    try:
        price = float(price_str)
        stock = int(stock_str)
        category_id = int(category_str)
    except ValueError:
        return "Giá trị không hợp lệ", 400

    # Lưu ảnh nếu có
    filename = None
    img_file = request.files.get('img_file')
    if img_file and img_file.filename:
        filename = secure_filename(img_file.filename)
        path = os.path.join(current_app.root_path, 'static/images/products', filename)
        img_file.save(path)

    # Thêm sản phẩm
    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category_id=category_id,
        img_file=filename
    )
    db.session.add(product)
    db.session.commit()
    print("Thêm sản phẩm thành công:", product.name)
    return '', 200


@bp.route('/update_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def update_product(product_id):
    print(f"🛠 [DEBUG] Cập nhật sản phẩm ID {product_id}")
    product = Product.query.get_or_404(product_id)

    # Lấy dữ liệu form an toàn
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price_str = request.form.get('price')
    stock_str = request.form.get('stock')
    category_str = request.form.get('category')

    if not name or not price_str or not stock_str or not category_str:
        return "Thiếu dữ liệu bắt buộc", 400

    try:
        product.price = float(price_str)
        product.stock = int(stock_str)
        product.category_id = int(category_str)
    except ValueError:
        return "Giá trị không hợp lệ", 400

    product.name = name
    product.description = description

    # Cập nhật ảnh
    img_file = request.files.get('img_file')
    if img_file and img_file.filename:
        filename = secure_filename(img_file.filename)
        path = os.path.join(current_app.root_path, 'static/images/products', filename)
        img_file.save(path)
        product.img_file = filename

    db.session.commit()
    print(f"Cập nhật sản phẩm '{product.name}' thành công")
    return '', 200

@bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        print(f"Không tìm thấy sản phẩm ID {product_id}")
        return "Sản phẩm không tồn tại", 404

    try:
        # Nếu sản phẩm có ảnh → xóa file ảnh trong thư mục static/images/products
        if product.img_file:
            img_path = os.path.join(current_app.root_path, 'static/images/products', product.img_file)
            if os.path.exists(img_path):
                os.remove(img_path)
                print(f"Đã xóa file ảnh: {img_path}")

        db.session.delete(product)
        db.session.commit()
        print(f"Đã xóa sản phẩm: {product.name}")
        return '', 200

    except Exception as e:
        print(f"Lỗi khi xóa sản phẩm: {e}")
        db.session.rollback()
        return "Lỗi khi xóa sản phẩm", 500