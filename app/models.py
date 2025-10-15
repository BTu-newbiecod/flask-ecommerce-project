import datetime
import enum
from sqlalchemy import ForeignKey
from app import db

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)

    #them tham chieu nguoc
    orders=db.relationship('Order',backref='customer',lazy='dynamic')

class Category(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False,unique=True)

    #them tham chieu nguoc
    products=db.relationship('Product',backref='category',lazy='dynamic')

class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text)
    price=db.Column(db.Float,nullable=False)
    stock=db.Column(db.Integer,nullable=False,default=0)    

# CHU Y: db.ForeignKey('tên_bảng_viết_thường.tên_cột')
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)

    #them tham chieu nguoc
    order_items=db.relationship('OrderItem',backref='product',lazy='dynamic')


#Tao ra cac gt cu the
class OrderStatus(enum.Enum):
    PENDING='Pending'
    SHIPPING='Shipping'
    COMPLETED='Completed'
    CANCELED='Canceled'

    

class Order(db.Model):
    # Chỉ định tên bảng rõ ràng ->tranh xung dot voi truy van order by
    __tablename__ = 'orders'

    id=db.Column(db.Integer,primary_key=True)
    order_date=db.Column(db.DateTime,nullable=False,default=db.func.now())
    status=db.Column(db.Enum(OrderStatus),nullable=False,default=OrderStatus.PENDING)
    total_amount=db.Column(db.Float,nullable=False,default=0.0)

    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    #them tham chieu nguoc
    items=db.relationship('OrderItem',backref='order',lazy='dynamic')


class OrderItem(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    quantity=db.Column(db.Integer,nullable=False,default=1)
    price_per_item=db.Column(db.Float,nullable=False)

    product_id=db.Column(db.Integer,db.ForeignKey('product.id'),nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey('orders.id'),nullable=False)

class Promotion(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    code=db.Column(db.String(100),nullable=False,unique=True)
    end_date=db.Column(db.DateTime,nullable=False)
    discount_percent=db.Column(db.Float,nullable=False)
