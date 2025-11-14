# seed.py
from app import create_app, db
from app.models import User, Category, Product, Order, OrderItem, Promotion, OrderStatus
from datetime import datetime, timedelta

app = create_app()

with app.app_context():

    #CHÚ Ý: sẽ xóa toàn bộ CSDL cũ và thêm mới
    db.drop_all()
    db.create_all()

    cat1 = Category(name='Áo Thun')
    cat2 = Category(name='Quần Jean')
    cat3 = Category(name='Áo Sơ Mi')
    cat4 = Category(name='Phụ Kiện')
    cat5 = Category(name='Đồ lót nam')
    cat6 = Category(name='Đồ lót nữ')
    cat7 = Category(name='Đồ ngủ')
    cat8 = Category(name='Áo khoác/Hoodie')
    cat9 = Category(name='Đồ thể thao')
    cat10 = Category(name='Quần tây')
    cat11 = Category(name='Quần short')
    cat12 = Category(name='Váy/Đầm')
    cat13 = Category(name='Quần ống rộng/legging')
    cat14 = Category(name='Khác')
    db.session.add_all([cat1, cat2, cat3, cat4, cat5, cat6, cat7, cat8, cat9, cat10, cat11, cat12, cat13, cat14])
    db.session.commit()

    user1 = User(username='admin', email='admin@shop.com', password='123456')
    user2 = User(username='customer', email='customer@example.com', password='123456')
    db.session.add_all([user1, user2])
    db.session.commit()

    p1 = Product(name='Áo Thun Basic Trắng', description='Áo thun cotton 100%, thoáng mát.', price=180000, stock=50, category=cat1,img_file='ao_thun_basic_trang.jpg')
    p2 = Product(name='Quần Jean Slimfit Xanh Đậm', description='Quần jean co giãn, form ôm.', price=450000, stock=30, category=cat2, img_file='jean_slimfit.jpg')
    p3 = Product(name='Áo Sơ Mi Oxford Trắng', description='Chất liệu vải oxford, lịch sự.', price=350000, stock=25, category=cat3, img_file='ao_so_mi_trang.jpg')
    p4 = Product(name='Áo Thun Polo Đen', description='Áo polo vải cá sấu cao cấp.', price=280000, stock=40, category=cat1, img_file='ao_polo_den.jpg')
    p5 = Product(name='Quần Jean Rách Gối', description='Phong cách cá tính, năng động.', price=520000, stock=15, category=cat2, img_file='jean_rach_goi.jpg')
    p6 = Product(name='Thắt Lưng Da Bò', description='Thắt lưng da bò thật, khóa kim loại.', price=250000, stock=60, category=cat4, img_file='that_lung_da_bo.jpg')
    p7 = Product(name='Áo Hoodie Nỉ Bông', description='Chất nỉ bông dày dặn, ấm áp cho mùa đông.', price=550000, stock=20, category=cat8, img_file='hoodie_ni_bong.jpg')
    p8 = Product(name='Quần Jogger Thể Thao', description='Vải thun co giãn, thoải mái vận động.', price=320000, stock=35, category=cat9, img_file='quan_jogger.jpg')
    p9 = Product(name='Quần Tây Âu Slimfit', description='Lịch lãm, phù hợp môi trường công sở.', price=480000, stock=25, category=cat10, img_file='quan_tay_au.jpg')
    p10 = Product(name='Quần Short Kaki Be', description='Năng động, trẻ trung, dễ phối đồ.', price=260000, stock=40, category=cat11, img_file='quan_short_kaki.jpg')
    p11 = Product(name='Váy Hoa Nhí Vintage', description='Vải voan mềm mại, phong cách retro.', price=420000, stock=22, category=cat12, img_file='vay_hoa_nhi.jpg')
    p12 = Product(name='Quần Ống Rộng Lưng Cao', description='Hack dáng, chất liệu linen thoáng mát.', price=390000, stock=30, category=cat13, img_file='quan_ong_rong.jpg')
    p13 = Product(name='Combo 3 Quần Boxer Nam', description='Cotton 4 chiều, kháng khuẩn.', price=299000, stock=50, category=cat5, img_file='combo_boxer_nam.jpg')
    p14 = Product(name='Mũ Lưỡi Trai Logo', description='Chất liệu Kaki, thêu logo nổi.', price=190000, stock=45, category=cat4, img_file='mu_luoi_trai.jpg')
    p15 = Product(name='Áo Khoác Dù 2 Lớp', description='Chống nước, chống gió nhẹ, có túi trong.', price=410000, stock=30, category=cat8, img_file='ao_khoac_du.jpg')
    db.session.add_all([
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, 
        p11, p12, p13, p14, p15
    ])
    db.session.commit()

    # order1 = Order(status=OrderStatus.COMPLETED, total_amount=630000, customer=user2, order_date=datetime.utcnow() - timedelta(days=5))
    # db.session.add(order1) 
    # db.session.commit()

    # order_item1 = OrderItem(order=order1, product=p1, quantity=1, price_per_item=180000)
    # order_item2 = OrderItem(order=order1, product=p2, quantity=1, price_per_item=450000)
    # db.session.add_all([order_item1, order_item2])

    # order2 = Order(status=OrderStatus.SHIPPING, total_amount=280000, customer=user2)
    # db.session.add(order2)
    # db.session.commit()

    # order_item3 = OrderItem(order=order2, product=p4, quantity=1, price_per_item=280000)
    # db.session.add(order_item3)

    promo1 = Promotion(code='TET2026', discount_percent=20.0, end_date=datetime.utcnow() + timedelta(days=30))
    promo2 = Promotion(code='NEWYEAR001', discount_percent=10.0, end_date=datetime.utcnow() + timedelta(days=90))
    db.session.add_all([promo1, promo2])

    db.session.commit()

    print("Database has been seeded successfully!")