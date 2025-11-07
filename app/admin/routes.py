from app.forms import ProductForm
from flask import render_template, redirect, url_for, request, flash
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

# Trang doanh thu
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

@bp.route('/product_form/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def product_form(id):
    product = Product.query.get(id) if id != 0 else None 
    form = ProductForm(obj=product)
    print('OK')

    if form.validate_on_submit():
        if product: 
            product.name = form.name.data 
            product.description = form.description.data 
            product.price = form.price.data 
            product.stock = form.stock.data 
            product.img_file = form.img_file.data or 'default.png'
            flash('Cập nhật sản phẩm thành công', 'success')

        else:
            new_product = Product(
                name = form.name.data,
                description = form.description.data,
                price = form.price.data,
                stock = form.stock.data,
                img_file = form.img_file.data or 'default.png'
            )
            db.session.add(new_product)
            flash('Thêm sản phẩm thành công', 'success')
        
        db.session.commit()
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', form=form, product=product)

# Xoa san pham
@bp.route('/delete_product/<int:id>', methods=['POST'])
@admin_required
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return ('', 204)

