from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Product, Category
import unicodedata

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required,current_user
from app.models import Product, CartItem, Order, OrderItem

from app import db


bp = Blueprint('main', __name__)

# 🏠 Trang chủ mới (index)
@bp.route('/')
@bp.route('/index')
def index():
    # Trang này có thể chỉ hiển thị banner, giới thiệu, nút đến sản phẩm, v.v.
    print("ttgeg")
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


#KHI BẤM NÚT THÊM VÀO GIỎ HÀNG 
@bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    #mặc định là 1 nếu không có từ form
    quantity = int(request.form.get('quantity', 1))
    
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if item:
        item.quantity = min(item.quantity + quantity, item.product.stock)
    else:
        #nếu chưa có, tạo mới
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    
    db.session.commit()
    flash('Đã thêm sản phẩm vào giỏ hàng!', 'success')
    
    # Quay lại trang mà người dùng vừa xem
    return redirect(request.referrer or url_for('main.index'))

#KHI BẤM NÚT GIỎ HÀNG Ở TRANG CHỦ
@bp.route('/cart')
@login_required
def cart():
    cart_items = current_user.cart_items.all()
    
    #tổng tiền
    total_price = 0
    for item in cart_items:
        # Gán một thuộc tính 'subtotal' tạm thời để template dễ truy cập
        item.subtotal = item.product.price * item.quantity
        total_price += item.subtotal

    return render_template('cart.html', cart_items=cart_items, total=total_price)

#NÚT XÓA KHỎI GIỎ HÀNG
@bp.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
    
    return redirect(url_for('main.cart'))

#NÚT XÓA NHIỀU KHỎI GIỎ HÀNG
@bp.route('/remove-selected', methods=['POST'])
@login_required
def remove_selected_from_cart():
    ids = request.form.getlist('selected_items')
    for product_id in ids:
        item = CartItem.query.filter_by(user_id=current_user.id, product_id=int(product_id)).first()
        if item:
            db.session.delete(item)
    db.session.commit()
    flash('Đã xóa các sản phẩm đã chọn.', 'info')
    return redirect(url_for('main.cart'))

#NÚT CHỈNH SỬA TRONG GIỎ HÀNG
@bp.route('/update-cart/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart(cart_item_id):
    try:
        new_quantity = int(request.form.get('quantity', 1))
    except ValueError:
        new_quantity = 1

    # Lấy đúng cart_item theo id và user
    item = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({"success": False, "message": "Sản phẩm không tồn tại"}), 404

    # Kiểm tra số lượng hợp lệ
    message = ""
    if new_quantity >= item.product.stock:
        item.quantity = item.product.stock
        message = "Bạn đã chọn tối đa số lượng!"
    elif new_quantity > 0:
        item.quantity = new_quantity
        message = ""
    else:
        item.quantity = 1
        message = "Vui lòng chọn số lượng ≥ 1!"

    db.session.commit()

    new_total = item.quantity * item.product.price

    return jsonify({
        "success": True,
        "message": message,
        "new_total": new_total
    })




#BẤM NÚT CHECKOUT-THANH TOÁN
@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'GET':
        # Lấy danh sách selected_items từ query params
        selected_ids = request.args.getlist("selected_items") 
        selected_ids = list(map(int, selected_ids))
        
        cart_items = CartItem.query.filter(CartItem.id.in_(selected_ids)).all()
        
        if not cart_items:
            flash('Giỏ hàng của bạn đang trống. Hãy thêm sản phẩm trước!', 'info')
            return redirect(url_for('main.index'))
        
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render_template('checkout.html', cart_items=cart_items, total=total_price)
    
    # POST: Xác nhận đặt hàng
    selected_ids = request.form.getlist("selected_items") 
    selected_ids = list(map(int, selected_ids))
    cart_items = CartItem.query.filter(CartItem.id.in_(selected_ids)).all()
    
    if not cart_items:
        flash('Giỏ hàng của bạn đang trống. Hãy thêm sản phẩm trước!', 'info')
        return redirect(url_for('main.index'))

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    try:
        new_order = Order(customer=current_user, total_amount=total_price)
        db.session.add(new_order)
        
        for item in cart_items:
            order_item = OrderItem(
                order=new_order,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_item=item.product.price
            )
            db.session.add(order_item)
            db.session.delete(item)
        
        db.session.commit()
        flash('Đặt hàng thành công! Cảm ơn bạn đã mua hàng.', 'success')
        return redirect(url_for('main.my_orders'))  # chuyển đến lịch sử đơn hàng
    except Exception as e:
        db.session.rollback()
        flash(f'Đã có lỗi xảy ra khi đặt hàng: {str(e)}', 'danger')
        return redirect(url_for('main.cart'))  # quay lại giỏ hàng nếu lỗi




#BẤM NÚT LỊCH SỬ ĐƠN HÀNG
@bp.route('/my-orders')
@login_required
def my_orders():
    #sắp xếp mới nhất lên đầu trước
    orders = current_user.orders.order_by(Order.order_date.desc()).all()
    return render_template('order_history.html', orders=orders)
    return render_template('product_detail.html', product=product)

# Bo dau khi search
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
