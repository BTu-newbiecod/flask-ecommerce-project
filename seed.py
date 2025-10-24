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
    db.session.add_all([cat1, cat2, cat3, cat4])
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
    db.session.add_all([p1, p2, p3, p4, p5, p6])
    db.session.commit()

    order1 = Order(status=OrderStatus.COMPLETED, total_amount=630000, customer=user2, order_date=datetime.utcnow() - timedelta(days=5))
    db.session.add(order1)
    db.session.commit()

    order_item1 = OrderItem(order=order1, product=p1, quantity=1, price_per_item=180000)
    order_item2 = OrderItem(order=order1, product=p2, quantity=1, price_per_item=450000)
    db.session.add_all([order_item1, order_item2])

    order2 = Order(status=OrderStatus.SHIPPING, total_amount=280000, customer=user2)
    db.session.add(order2)
    db.session.commit()

    order_item3 = OrderItem(order=order2, product=p4, quantity=1, price_per_item=280000)
    db.session.add(order_item3)

    promo1 = Promotion(code='TET2026', discount_percent=20.0, end_date=datetime.utcnow() + timedelta(days=30))
    promo2 = Promotion(code='NEWYEAR001', discount_percent=10.0, end_date=datetime.utcnow() + timedelta(days=90))
    db.session.add_all([promo1, promo2])

    db.session.commit()

    print("Database has been seeded successfully!")