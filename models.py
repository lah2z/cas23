from db import db
from datetime import datetime
from flask_login import UserMixin

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True, cascade="all, delete")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))  # Основное изображение
    images = db.Column(db.JSON)  # Дополнительные изображения в формате JSON
    features = db.Column(db.Text)  # JSON строка с характеристиками
    specs = db.Column(db.JSON)     # JSON объект с техническими характеристиками
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    advantages = db.Column(db.JSON)
    specifications = db.Column(db.JSON)
    options = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.title}>'

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64))
    username = db.Column(db.String(64))
    phone = db.Column(db.String(32))
    address = db.Column(db.String(255))
    fio = db.Column(db.String(255))
    payment_method = db.Column(db.String(32))
    delivery_method = db.Column(db.String(32))
    total = db.Column(db.Float)
    status = db.Column(db.String(32), default='created')
    order_number = db.Column(db.String(100))  # Номер заказа в формате {user_id}-{sequence}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    options = db.Column(db.JSON) 