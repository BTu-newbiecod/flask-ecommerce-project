from flask import render_template, redirect, url_for, Blueprint, request, current_app
from flask_login import login_required, current_user
from app.admin import bp
from functools import wraps
from app.models import OrderItem, db, Order, Product, Category, OrderStatus
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
import uuid
import unicodedata


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

# Bo dau khi search
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Tim kiem san pham
@bp.route('/admin_search')
@admin_required
@login_required
def admin_search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('admin.products'))
    
    normal_query = remove_accents(query)

    all_products = Product.query.all()
    products = [
        p for p in all_products 
        if normal_query in remove_accents(p.name.lower())
        or normal_query in remove_accents((p.description or '').lower())
    ]
    return render_template('admin/products.html', products=products, query=query)

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

@bp.route('/add_product', methods=['POST'])
@login_required
@admin_required
def add_product():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    old_price_str = request.form.get('old-price')
    price_str = request.form.get('price')
    stock_str = request.form.get('stock')
    category_str = request.form.get('category')

    if not name or not price_str or not stock_str or not category_str:
        return "Thiếu dữ liệu bắt buộc", 400

    try:
        if old_price_str: old_price = float(old_price_str)
        else: old_price = 0
        price = float(price_str)
        stock = int(stock_str)
        category_id = int(category_str)
    except ValueError:
        return "Giá trị không hợp lệ", 400

    # Xử lý ảnh 
    filename = None
    img_file = request.files.get('img_file')
    if img_file and img_file.filename:
        original_name = secure_filename(img_file.filename)
        # thêm UUID để tránh trùng tên
        ext = os.path.splitext(original_name)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(current_app.root_path, 'static/assets/images/products', unique_name)
        img_file.save(save_path)
        filename = unique_name

    # Thêm sản phẩm 
    product = Product(
        name=name,
        description=description,
        old_price=old_price,
        price=price,
        stock=stock,
        category_id=category_id,
        img_file=filename or 'default.png'
    )
    db.session.add(product)
    db.session.commit()

    print("Thêm sản phẩm thành công:", product.name)
    return '', 200


@bp.route('/update_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def update_product(product_id):
    print(f"Cập nhật sản phẩm ID {product_id}")
    product = Product.query.get_or_404(product_id)

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    old_price_str = request.form.get('old-price')
    price_str = request.form.get('price')
    stock_str = request.form.get('stock')
    category_str = request.form.get('category')

    if not name or not price_str or not stock_str or not category_str:
        return "Thiếu dữ liệu bắt buộc", 400

    try:
        product.old_price = float(old_price_str)
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
        path = os.path.join(current_app.root_path, 'static/assets/images/products', filename)
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
    
    if db.session.query(OrderItem.id).filter_by(product_id=product_id).first():
        print('Check')
        return "Không thể xóa sản phẩm vì đã có trong đơn hàng!", 400

    try:
        if product.img_file:
            img_path = os.path.join(current_app.root_path, 'static/assets/images/products', product.img_file)
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

# Xem danh sách đơn hàng chờ xử lý
@bp.route('/pending_orders')
@login_required
@admin_required
def pending_orders():
    orders = Order.query.filter_by(status=OrderStatus.PENDING) \
        .order_by(Order.order_date.asc()).all()  # đơn sớm nhất lên đầu
    return render_template('admin/pending_orders.html', orders=orders)


# Xem danh sách đơn hàng đang giao
@bp.route('/delivery_orders')
@login_required
@admin_required
def delivery_orders():
    orders = Order.query.filter_by(status=OrderStatus.SHIPPING) \
        .order_by(Order.order_date.asc()).all()
    return render_template('admin/delivery_orders.html', orders=orders)


@bp.route('/order/<int:order_id>')
@login_required
def order_form(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = order.items
    # Lấy biến source từ query string ?source=pending hoặc ?source=delivering
    source = request.args.get('source', None)
    return render_template('admin/order_form.html', order=order, order_items=order_items, source=source)

@bp.route('/reports')
@login_required
@admin_required
def reports():
    now = datetime.now()
    
    monthly_data = db.session.query(
        extract('month', Order.order_date).label('month'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        extract('year', Order.order_date) == now.year,
        Order.status == OrderStatus.COMPLETED  
    ).group_by('month').order_by('month').all()

    monthly_revenue = {int(month): revenue for month, revenue in monthly_data}

    for m in range(1, 13):
        if m not in monthly_revenue:
            monthly_revenue[m] = 0

    monthly_revenue = dict(sorted(monthly_revenue.items()))

    monthly_order_data = db.session.query(
    extract('month', Order.order_date).label('month'),
    func.count(Order.id).label('order_count')
    ).filter(
        extract('year', Order.order_date) == now.year,
        Order.status == OrderStatus.COMPLETED
    ).group_by('month').order_by('month').all()

    monthly_order_counts = {int(month): count for month, count in monthly_order_data}
    for m in range(1, 13):
        if m not in monthly_order_counts:
            monthly_order_counts[m] = 0
    monthly_order_counts = dict(sorted(monthly_order_counts.items()))

    return render_template(
        'admin/reports.html',
        monthly_revenue=monthly_revenue,
        current_year=now.year,   
        monthly_order_counts=monthly_order_counts
    )

@bp.route('/completed_orders')
def completed_orders():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    orders = Order.query.filter(
        Order.status == OrderStatus.COMPLETED,
        extract('month', Order.order_date) == month,
        extract('year', Order.order_date) == year
    ).order_by(Order.order_date.desc()).all()

    return render_template('admin/completed_orders.html', orders=orders, month=month, year=year)

@bp.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    new_status = request.form.get('new_status')
    order = Order.query.get_or_404(order_id)
    
    # Map từ template sang Enum
    status_map = {
        'pending': OrderStatus.PENDING,
        'delivering': OrderStatus.SHIPPING,
        'completed': OrderStatus.COMPLETED,
        'cancelled': OrderStatus.CANCELED
    }

    if new_status in status_map:
        order.status = status_map[new_status]
        db.session.commit()

    return redirect(request.referrer or url_for('admin.dashboard'))

