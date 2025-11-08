from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Product, Category
from sqlalchemy import or_
import unicodedata

from flask import Blueprint, render_template ,redirect, url_for, flash, request
from flask_login import login_required,current_user
from app.models import Product,CartItem, Order, OrderItem

from app import db


bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template("index.html", products = products, categories=categories)


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
        item.quantity += quantity
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

#NÚT CHỈNH SỬA TRONG GIỎ HÀNG
@bp.route('/update-cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    new_quantity = int(request.form.get('quantity', 1))
    
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if item:
        if new_quantity > 0:
            item.quantity = new_quantity
            db.session.commit()
            flash('Đã cập nhật số lượng sản phẩm.', 'success')
        elif new_quantity == 0:
            #số lượng là 0 coi như xóa
            db.session.delete(item)
            db.session.commit()
            flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
            
    return redirect(url_for('main.cart'))



#BẤM NÚT CHECKOUT-THANH TOÁN
@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    #Lấy giỏ hàng
    cart_items = current_user.cart_items.all()
    
    if not cart_items:
        flash('Giỏ hàng của bạn đang trống. Hãy thêm sản phẩm trước!', 'info')
        return redirect(url_for('main.index'))

    #tổng tiền 
    total_price = 0
    for item in cart_items:
        total_price += item.product.price * item.quantity

    #BẤM THÊM XÁC NHẬN ĐỂ ĐẶT HÀNG
    if request.method == 'POST':
        try:
            new_order = Order(
                customer=current_user,
                total_amount=total_price
             
            )
            db.session.add(new_order)
            
            #Chuyển các sản phẩm từ giỏ hàng sang chi tiết đơn hàng
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
            return redirect(url_for('main.my_orders')) #chuyển đến trang lịch sử đơn hàng
            
        except Exception as e:
            # rollback nếu lỗi
            db.session.rollback()
            flash(f'Đã có lỗi xảy ra khi đặt hàng: {str(e)}', 'danger')

    return render_template('checkout.html', cart_items=cart_items, total=total_price)



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

# Tim san pham
@bp.route('/search', methods=['GET'])
def search_product():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.index'))
    
    normal_query = remove_accents(query)

    all_products = Product.query.all()
    products = [
        p for p in all_products 
        if normal_query in remove_accents(p.name.lower())
        or normal_query in remove_accents((p.description or '').lower())
    ]
    categories = Category.query.all()

    return render_template('index.html', products=products, query=query, categories=categories)

# Loc san pham
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
    return render_template('index.html', products=products, categories=categories)