import datetime
import enum
from sqlalchemy import ForeignKey
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
                
    def set_password(self, new_password_text):
        self.password = new_password_text

    def check_password(self, password_to_check):
        return self.password == password_to_check

    #them tham chieu nguoc
    orders=db.relationship('Order',backref='customer',lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='customer', lazy='dynamic')
    addresses = db.relationship('Address', backref='user', lazy='dynamic', cascade='all, delete-orphan')

class Category(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False,unique=True)
    products=db.relationship('Product',backref='category',lazy='dynamic')

class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text)
    old_price=db.Column(db.Float,nullable=True)
    price=db.Column(db.Float,nullable=False)
    stock=db.Column(db.Integer,nullable=False,default=0)     
    img_file=db.Column(db.String(100),nullable=False,default='default.jpg')
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    order_items=db.relationship('OrderItem',backref='product',lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic')

class OrderStatus(enum.Enum):
    PENDING='Pending'
    SHIPPING='Shipping'
    COMPLETED='Completed'
    CANCELED='Canceled'
 
class Order(db.Model):
    __tablename__ = 'orders'

    id=db.Column(db.Integer,primary_key=True)
    order_date=db.Column(db.DateTime,nullable=False,default=db.func.now())
    status=db.Column(db.Enum(OrderStatus),nullable=False,default=OrderStatus.PENDING)
    total_amount=db.Column(db.Float,nullable=False,default=0.0)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    items=db.relationship('OrderItem',backref='order',lazy='dynamic')


    shipping_address_id = db.Column(db.Integer, db.ForeignKey('address.id', name='fk_orders_shipping_address'), nullable=True) 
    # ---------------------

    shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id])

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

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_address_user'), nullable=False)
    # ---------------------

    def __repr__(self):
        return f'<Address {self.recipient_name} - {self.city}>'