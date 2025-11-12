from flask import render_template, request, redirect, url_for, flash, jsonify, current_app

import google.generativeai as genai

from app.models import Product, Category

import unicodedata

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify

from flask_login import login_required,current_user

from app.models import Product, CartItem, Order, OrderItem,Address

from app import db

from math import ceil           

from .forms import EditProfileForm, ChangePasswordForm,AddressForm
import re 

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
    # Lấy page hiện tại từ query string (mặc định 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # số sản phẩm mỗi trang

    # Lấy filter từ query string (nếu có)
    category_id = request.args.get('category', type=int)
    sort_type = request.args.get('sort_type', type=int)

    # Query cơ bản
    query = Product.query
    if category_id:
        query = query.filter(Product.category_id == category_id)

    if sort_type == 1:
        query = query.order_by(Product.price.asc())
    elif sort_type == -1:
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.id.asc())

    total_products = query.count()
    total_pages = ceil(total_products / per_page)

    products = query.offset((page - 1) * per_page).limit(per_page).all()
    categories = Category.query.all()

    return render_template('product_list.html', 
                           products=products, 
                           categories=categories, 
                           page=page, 
                           total_pages=total_pages,
                           category_id=category_id,
                           sort_type=sort_type)



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
        selected_ids = request.args.getlist("selected_items")
    else: 
        selected_ids = request.form.getlist("selected_items")
        
    if not selected_ids:
        flash('Giỏ hàng của bạn đang trống. Hãy thêm sản phẩm trước!', 'info')
        return redirect(url_for('main.cart')) 

    selected_ids = list(map(int, selected_ids))

    cart_items = CartItem.query.filter(CartItem.id.in_(selected_ids), CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        flash('Không tìm thấy sản phẩm đã chọn trong giỏ hàng.', 'warning')
        return redirect(url_for('main.cart'))

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    saved_addresses = current_user.addresses.order_by(Address.is_default.desc()).all()
    address_form = AddressForm()
    if request.method == 'POST':
        chosen_address_id = 0 
        address_choice = request.form.get('address_choice')

        try:
            if address_choice == 'new':
     
                if address_form.validate_on_submit():
                    # Xử lý logic "địa chỉ mặc định"
                    if address_form.is_default.data:
                        old_default = current_user.addresses.filter_by(is_default=True).first()
                        if old_default:
                            old_default.is_default = False
                            db.session.add(old_default)
                            
                    new_addr = Address(
                        recipient_name=address_form.recipient_name.data,
                        phone_number=address_form.phone_number.data,
                        street_address=address_form.street_address.data,
                        city=address_form.city.data,
                        is_default=address_form.is_default.data,
                        user_id=current_user.id
                    )
                    db.session.add(new_addr)
               
                    db.session.commit()
                    chosen_address_id = new_addr.id
                else:
                    flash('Vui lòng kiểm tra lại thông tin địa chỉ mới.', 'danger')
                    return render_template('checkout.html', 
                                           cart_items=cart_items, 
                                           total=total_price,
                                           saved_addresses=saved_addresses,
                                           address_form=address_form,
                                           selected_ids=selected_ids,                     
                                           show_new_address_form=True)
            elif address_choice and address_choice.isdigit():
                chosen_address_id = int(address_choice)
                addr_check = Address.query.filter_by(id=chosen_address_id, user_id=current_user.id).first()
                if not addr_check:
                    flash('Địa chỉ không hợp lệ!', 'danger')
                    return redirect(url_for('main.cart'))
            else:
                flash('Vui lòng chọn hoặc nhập địa chỉ giao hàng.', 'danger')
                return render_template('checkout.html', 
                                       cart_items=cart_items, 
                                       total=total_price,
                                       saved_addresses=saved_addresses,
                                       address_form=address_form,
                                       selected_ids=selected_ids,
                                       show_new_address_form=False)
            new_order = Order(
                customer=current_user, 
                total_amount=total_price,
                # *** DÒNG QUAN TRỌNG NHẤT ***
                shipping_address_id=chosen_address_id 
            )
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
            return redirect(url_for('main.my_orders'))

        except Exception as e:
            db.session.rollback()
            flash(f'Đã có lỗi xảy ra khi đặt hàng: {str(e)}', 'danger')
            return redirect(url_for('main.cart'))

    # --- XỬ LÝ KHI TẢI TRANG (GET) ---
    return render_template('checkout.html', 
                           title="Thanh Toán",
                           cart_items=cart_items, 
                           total=total_price,
                           saved_addresses=saved_addresses,
                           address_form=address_form,
                           selected_ids=selected_ids,
                           # Ban đầu, không hiện form thêm mới (trừ khi không có địa chỉ nào)
                           show_new_address_form=(not saved_addresses))


#BẤM NÚT LỊCH SỬ ĐƠN HÀNG
@bp.route('/my-orders')
@login_required
def my_orders():
    #sắp xếp mới nhất lên đầu trước
    orders = current_user.orders.order_by(Order.order_date.desc()).all()
    return render_template('order_history.html', orders=orders)
    return render_template('product_detail.html', product=product)

@bp.route('/my-order-form/<int:order_id>')
@login_required
def my_order_form(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = order.items
    return render_template('my_order_form.html', order=order, order_items=order_items)

# Bo dau khi search
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


# Tìm kiếm sản phẩm
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


# Lọc sản phẩm theo danh mục / giá
@bp.route("/filter")
def filter_product():
    category_id = request.args.get('category')
    if category_id:
        try:
            category_id = int(category_id)
        except ValueError:
            category_id = None
    else:
        category_id = None
    sort_type = int(request.args.get('sort_type', 0))

    # Lọc products theo category + sort_type
    products_query = Product.query
    if category_id:
        products_query = products_query.filter_by(category_id=category_id)
    
    if sort_type == 1:
        products_query = products_query.order_by(Product.price.asc())
    elif sort_type == -1:
        products_query = products_query.order_by(Product.price.desc())

    products_list = products_query.all()
    categories = Category.query.all()

    # Phân trang
    page = int(request.args.get('page', 1))
    per_page = 10
    total_pages = ceil(len(products_list) / per_page) or 1

    # Lấy đúng 10 sản phẩm của trang hiện tại
    start = (page - 1) * per_page
    end = start + per_page
    products = products_list[start:end]

    return render_template(
        "product_list.html",
        products=products,
        categories=categories,
        category_id=category_id,
        sort_type=sort_type,
        page=page,
        total_pages=total_pages,
        query=None
    )


#TRANG HỒ SƠ
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm(obj=current_user)
    
    # Lấy thêm danh sách địa chỉ
    addresses = current_user.addresses.order_by(Address.is_default.desc()).all()
    
    is_default_admin = (current_user.email == 'admin@shop.com')

    if form.validate_on_submit():
        if is_default_admin:
            flash('Tài khoản admin là mặc định không thể đổi', 'danger')
            return redirect(url_for('main.profile'))

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Đã cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', title='Hồ sơ cá nhân', 
                           form=form, 
                           addresses=addresses, # <-- Gửi thêm địa chỉ
                           is_default_admin=is_default_admin)

# TRANG ĐỔI MẬT KHẨU
@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
 
    is_default_admin = (current_user.email == 'admin@shop.com')

    if form.validate_on_submit():
    
        if is_default_admin:
            flash('Tài khoản admin là mặc định không thể đổi', 'danger')
            return redirect(url_for('main.change_password'))
        
        # Nếu form hợp lệ, set mật khẩu mới
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Đổi mật khẩu thành công!', 'success')
        # Đổi xong thì quay về trang hồ sơ
        return redirect(url_for('main.profile'))

    #tải trang (GET)
    return render_template('change_password.html', 
                           title='Đổi Mật Khẩu', 
                           form=form, 
                           is_default_admin=is_default_admin)

# HÀM TẠO Link-thân-thiện
def slugify(text):
    """Tạo một 'slug' an toàn cho URL từ text."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text

# HÀM TRUY XUẤT (DATABASE)
def find_relevant_products(user_message):
    """
    Tìm các sản phẩm trong CSDL dựa trên tin nhắn của user.
    """
    # Chuẩn hóa tin nhắn
    query = user_message.lower().strip()
    if not query:
        return []

    # Tìm các từ khóa đơn giản
    keywords = query.split()

    # Tìm sản phẩm có tên hoặc mô tả chứa BẤT KỲ từ khóa nào
    q_filters = [
        db.or_(
            Product.name.ilike(f'%{keyword}%'),
            Product.description.ilike(f'%{keyword}%')
        ) for keyword in keywords
    ]

    # Chỉ lấy 3 sản phẩm liên quan nhất
    products = Product.query.filter(db.or_(*q_filters)).limit(3).all()
    return products

# HÀM API_CHAT
@bp.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        api_key = current_app.config['GEMINI_API_KEY']
        if not api_key:
            return jsonify({'reply': 'Lỗi: API Key chưa được cấu hình.'}), 500

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash') 

        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'reply': 'Lỗi: Không nhận được tin nhắn.'}), 400

        user_message = data['message']

        #TRUY XUẤT (Retrieval) ---
        products = find_relevant_products(user_message)
        product_context = ""

        if products:
            product_context += "[Dữ liệu sản phẩm từ CSDL của shop]:\n"
            for p in products:
                slug = slugify(p.name)
                link = url_for('main.product_detail', id=p.id, slug=slug, _external=True)
                product_context += f"- Tên: {p.name}, Mô tả: {p.description}, Link: {link}\n"
        else:
            product_context = "[Không tìm thấy sản phẩm nào trong CSDL khớp với truy vấn này.]"


        # Tạo prompt mới, "nhồi" dữ liệu CSDL vào
        prompt = f"""
        Bạn là một trợ lý chatbot bán hàng tên là Py, làm việc cho Pypy Store.

        **[Bối cảnh cửa hàng Pypy Store (Rất quan trọng)]:**
        Shop của bạn bán 14 danh mục sản phẩm sau:
        - Nhóm Áo: Áo Thun, Áo Sơ Mi, Áo khoác/Hoodie
        - Nhóm Quần: Quần Jean, Quần tây, Quần short, Quần ống rộng/legging, Đồ thể thao (Quần Jogger)
        - Nhóm Nữ: Váy/Đầm, Đồ lót nữ
        - Nhóm Nam: Đồ lót nam
        - Nhóm Ngủ: Đồ ngủ
        - Nhóm Phụ Kiện: Phụ Kiện (ví dụ: Thắt Lưng, Mũ Lưỡi Trai)
        - Khác

        **[Dữ liệu sản phẩm từ CSDL (Kết quả tìm kiếm cho "{user_message}")]:**
        {product_context}

        **[Nhiệm vụ của bạn (Các quy tắc BẮT BUỘC)]:**
        Bạn phải trả lời câu hỏi của khách hàng: "{user_message}".
        Hãy tuân thủ NGHIÊM NGẶT các quy tắc sau:

        **Quy tắc 1 (Ưu tiên Dữ liệu CSDL):**
        - NẾU [Dữ liệu sản phẩm] có kết quả, HÃY ƯU TIÊN đề xuất các sản phẩm đó.
        - Khi đề xuất, BẮT BUỘC chèn link HTML (thẻ <a>) vào tên sản phẩm.
        - Ví dụ: "Dạ, Pypy Store có <a href='link-san-pham'>Áo Hoodie Nỉ Bông</a> đang rất hot, bạn xem thử nhé!"

        **Quy tắc 2 (Sử dụng Bối cảnh cửa hàng - SỬA LỖI "QUẦN SHORT"):**
        - NẾU [Dữ liệu sản phẩm] là trống (không tìm thấy gì), HÃY KIỂM TRA [Bối cảnh cửa hàng].
        - Nếu câu hỏi của khách hàng khớp với 1 trong 14 danh mục (ví dụ: "shop có quần short không?" -> khớp "Quần short"), HÃY trả lời là "CÓ" và giới thiệu chung về danh mục đó.
        - Ví dụ trả lời (khi CSDL không tìm thấy): "Dạ, Pypy Store có bán [Quần short] ạ. Bạn có thể xem tất cả các mẫu ở mục 'Sản Phẩm' trên thanh menu nhé!"
        - **TUYỆT ĐỐI không trả lời "Không" hoặc "Xin lỗi" nếu mặt hàng đó có tên trong 14 danh mục [Bối cảnh cửa hàng].**

        **Quy tắc 3 (Xử lý câu "dân dã" - "tôi muốn..."):**
        - Hiểu các câu hỏi "dân dã" là một yêu cầu tìm kiếm.
        - Ví dụ 1: "tôi muốn mua đồ gì đó ấm áp" -> Hiểu là tìm "Áo khoác/Hoodie". Dùng Quy tắc 1 hoặc 2.
        - Ví dụ 2: "shop có đồ nào lịch sự đi làm không?" -> Hiểu là tìm "Áo Sơ Mi" hoặc "Quần tây". Dùng Quy tắc 1 hoặc 2.
        - Ví dụ 3: "có đồ nào cá tính không?" -> Hiểu là tìm "Quần Jean Rách Gối". Dùng Quy tắc 1 hoặc 2.
        - Ví dụ 4: "tìm đồ mặc nhà" -> Hiểu là tìm "Đồ ngủ". Dùng Quy tắc 1 hoặc 2.

        **Quy tắc 4 (Câu hỏi chung):**
        - Nếu câu hỏi không liên quan đến sản phẩm (ví dụ: "shop giao hàng bao lâu?", "chào shop"), hãy trả lời bình thường, ngắn gọn.

        Hãy bắt đầu. Câu hỏi của khách hàng là: "{user_message}"
        Câu trả lời của bạn (phải là HTML nếu có link):
        """

        
        response = model.generate_content(prompt)
        bot_response_text = response.text

        return jsonify({'reply': bot_response_text})

    except Exception as e:
        print(f"Lỗi khi gọi Gemini API: {e}")
        return jsonify({'reply': 'Xin lỗi, tôi đang gặp lỗi kỹ thuật. Vui lòng thử lại sau.'}), 500

# ----- LOGIC SỔ ĐỊA CHỈ -----

#HÀM XỬ LÝ LƯU ĐỊA CHỈ
@bp.route('/add-address', methods=['GET', 'POST'])
@login_required
def add_address():
    form = AddressForm()
    
    if form.validate_on_submit():
        if form.is_default.data:
            old_default = current_user.addresses.filter_by(is_default=True).first()
            if old_default:
                old_default.is_default = False
                db.session.add(old_default)

        # Tạo địa chỉ mới
        new_addr = Address(
            recipient_name=form.recipient_name.data,
            phone_number=form.phone_number.data,
            street_address=form.street_address.data,
            city=form.city.data,
            is_default=form.is_default.data,
            user_id=current_user.id
        )
        db.session.add(new_addr)
        db.session.commit()
        
        flash('Đã thêm địa chỉ mới thành công!', 'success')
        return redirect(url_for('main.profile', _anchor='address-tab'))
        
    return render_template('add_edit_address.html', 
                           title="Thêm Địa Chỉ Mới", 
                           form=form,
                           legend="Thêm Địa Chỉ Mới")

#TRANG SỬA ĐỊA CHỈ
@bp.route('/edit-address/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    addr = Address.query.get_or_404(address_id)
    if addr.user_id != current_user.id:
        flash('Bạn không có quyền sửa địa chỉ này.', 'danger')
        return redirect(url_for('main.manage_addresses'))
    form = AddressForm(obj=addr)
    
    if form.validate_on_submit():
        if form.is_default.data:
            old_default = current_user.addresses.filter_by(is_default=True).first()
            if old_default and old_default.id != addr.id:
                old_default.is_default = False
                db.session.add(old_default)
        addr.recipient_name = form.recipient_name.data
        addr.phone_number = form.phone_number.data
        addr.street_address = form.street_address.data
        addr.city = form.city.data
        addr.is_default = form.is_default.data
        
        db.session.commit()
        flash('Cập nhật địa chỉ thành công!', 'success')
        return redirect(url_for('main.profile', _anchor='address-tab'))

    return render_template('add_edit_address.html', 
                           title="Chỉnh Sửa Địa Chỉ", 
                           form=form,
                           legend="Chỉnh Sửa Địa Chỉ")

#HÀNH ĐỘNG XÓA ĐỊA CHỈ
@bp.route('/delete-address/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    addr = Address.query.get_or_404(address_id)
    if addr.user_id != current_user.id:
        flash('Bạn không có quyền xóa địa chỉ này.', 'danger')
        return redirect(url_for('main.profile', _anchor='address-tab'))
    
    db.session.delete(addr)
    db.session.commit()
    flash('Đã xóa địa chỉ.', 'info')
    return redirect(url_for('main.profile', _anchor='address-tab'))