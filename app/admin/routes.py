from flask import render_template, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from app.admin import bp
from functools import wraps
from app.models import db, Order, Product, Category, OrderStatus
from sqlalchemy import func, extract
from datetime import datetime, timedelta

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

@bp.route('/products')
@admin_required
@login_required
def products(): 
    products = Product.query.order_by(Product.id.desc()).all()  
    return render_template('admin/products.html', products=products)

@bp.route('/product_form/<int:product_id>')
@admin_required
@login_required
def product_form(product_id):
    if product_id == 0:
        # Trả về form rỗng cho thêm mới
        return render_template('admin/product_form.html', product=None, categories=Category.query.all())
    product = Product.query.get_or_404(product_id)
    return render_template('admin/product_form.html', product=product, categories=Category.query.all())

