import os
import sqlite3
from app import app, db
from models import Category, Product, Order, OrderItem, Admin

def migrate_data():
    """Мигрирует данные из локальной SQLite в PostgreSQL"""
    
    # Проверяем, есть ли локальная база
    if not os.path.exists('instance/shop.db'):
        print("Локальная база данных не найдена!")
        return
    
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
                print(f"Добавлена категория: {name}")
        
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
                print(f"Добавлен продукт: {title}")
        
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
                print(f"Добавлен админ: {username}")
        
        # Сохраняем изменения
        db.session.commit()
        print("✅ Миграция завершена успешно!")
        print(f"Перенесено: {len(categories)} категорий, {len(products)} продуктов, {len(admins)} админов")
    
    sqlite_conn.close()

if __name__ == "__main__":
    migrate_data() 