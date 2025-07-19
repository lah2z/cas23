import os
import sqlite3
from sqlalchemy import create_engine, text
from app import app, db
from models import Category, Product, Order, OrderItem, Admin

def migrate_data():
    """Мигрирует данные из SQLite в PostgreSQL"""
    
    # Подключение к SQLite
    sqlite_conn = sqlite3.connect('instance/shop.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    with app.app_context():
        # Создаем таблицы в PostgreSQL
        db.create_all()
        
        # Мигрируем категории
        print("Мигрируем категории...")
        sqlite_cursor.execute("SELECT id, name FROM category")
        categories = sqlite_cursor.fetchall()
        
        for cat_id, name in categories:
            category = Category.query.get(cat_id)
            if not category:
                category = Category(id=cat_id, name=name)
                db.session.add(category)
        
        # Мигрируем продукты
        print("Мигрируем продукты...")
        sqlite_cursor.execute("""
            SELECT id, title, description, price, image, category_id, 
                   advantages, specifications, options 
            FROM product
        """)
        products = sqlite_cursor.fetchall()
        
        for (prod_id, title, description, price, image, category_id, 
             advantages, specifications, options) in products:
            product = Product.query.get(prod_id)
            if not product:
                product = Product(
                    id=prod_id,
                    title=title,
                    description=description,
                    price=price,
                    image=image,
                    category_id=category_id,
                    advantages=advantages,
                    specifications=specifications,
                    options=options
                )
                db.session.add(product)
        
        # Мигрируем заказы
        print("Мигрируем заказы...")
        sqlite_cursor.execute("""
            SELECT id, user_id, username, phone, address, fio, 
                   payment_method, delivery_method, total, status, 
                   order_number, created_at 
            FROM `order`
        """)
        orders = sqlite_cursor.fetchall()
        
        for (order_id, user_id, username, phone, address, fio,
             payment_method, delivery_method, total, status,
             order_number, created_at) in orders:
            order = Order.query.get(order_id)
            if not order:
                order = Order(
                    id=order_id,
                    user_id=user_id,
                    username=username,
                    phone=phone,
                    address=address,
                    fio=fio,
                    payment_method=payment_method,
                    delivery_method=delivery_method,
                    total=total,
                    status=status,
                    order_number=order_number,
                    created_at=created_at
                )
                db.session.add(order)
        
        # Мигрируем элементы заказов
        print("Мигрируем элементы заказов...")
        sqlite_cursor.execute("""
            SELECT id, order_id, product_id, title, price, quantity, options 
            FROM order_item
        """)
        order_items = sqlite_cursor.fetchall()
        
        for (item_id, order_id, product_id, title, price, quantity, options) in order_items:
            order_item = OrderItem.query.get(item_id)
            if not order_item:
                order_item = OrderItem(
                    id=item_id,
                    order_id=order_id,
                    product_id=product_id,
                    title=title,
                    price=price,
                    quantity=quantity,
                    options=options
                )
                db.session.add(order_item)
        
        # Мигрируем админов
        print("Мигрируем админов...")
        sqlite_cursor.execute("SELECT id, username, password_hash FROM admin")
        admins = sqlite_cursor.fetchall()
        
        for admin_id, username, password_hash in admins:
            admin = Admin.query.get(admin_id)
            if not admin:
                admin = Admin(
                    id=admin_id,
                    username=username,
                    password_hash=password_hash
                )
                db.session.add(admin)
        
        # Сохраняем изменения
        db.session.commit()
        print("Миграция завершена успешно!")
    
    sqlite_conn.close()

if __name__ == "__main__":
    migrate_data() 