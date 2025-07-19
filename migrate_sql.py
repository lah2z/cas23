import sqlite3
import json

def export_sqlite_to_sql():
    """Экспортирует данные из SQLite в SQL-файл для PostgreSQL"""
    
    # Подключение к SQLite
    sqlite_conn = sqlite3.connect('instance/shop.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    sql_commands = []
    
    # Получаем данные категорий
    sqlite_cursor.execute("SELECT id, name FROM category")
    categories = sqlite_cursor.fetchall()
    
    for cat_id, name in categories:
        safe_name = name.replace("'", "''") if name else ''
        sql_commands.append(f"INSERT INTO category (id, name) VALUES ({cat_id}, '{safe_name}');")
    
    # Получаем данные продуктов
    sqlite_cursor.execute("""
        SELECT id, title, description, price, image, category_id, 
               advantages, specifications, options 
        FROM product
    """)
    products = sqlite_cursor.fetchall()
    
    for (prod_id, title, description, price, image, category_id, 
         advantages, specifications, options) in products:
        
        # Экранируем кавычки в строках
        title = title.replace("'", "''") if title else ''
        description = description.replace("'", "''") if description else ''
        image = image.replace("'", "''") if image else ''
        advantages = advantages.replace("'", "''") if advantages else ''
        specifications = specifications.replace("'", "''") if specifications else ''
        options = options.replace("'", "''") if options else ''
        
        sql_commands.append(f"""
        INSERT INTO product (id, title, description, price, image, category_id, advantages, specifications, options) 
        VALUES ({prod_id}, '{title}', '{description}', {price}, '{image}', {category_id}, '{advantages}', '{specifications}', '{options}');
        """)
    
    # Получаем данные админов
    sqlite_cursor.execute("SELECT id, username, password_hash FROM admin")
    admins = sqlite_cursor.fetchall()
    
    for admin_id, username, password_hash in admins:
        username = username.replace("'", "''") if username else ''
        password_hash = password_hash.replace("'", "''") if password_hash else ''
        sql_commands.append(f"INSERT INTO admin (id, username, password_hash) VALUES ({admin_id}, '{username}', '{password_hash}');")
    
    # Записываем в файл
    with open('migration_data.sql', 'w', encoding='utf-8') as f:
        f.write("-- Миграция данных из SQLite в PostgreSQL\n")
        f.write("-- Выполните этот файл в PostgreSQL\n\n")
        
        for command in sql_commands:
            f.write(command + "\n")
    
    print(f"✅ Экспортировано:")
    print(f"   - {len(categories)} категорий")
    print(f"   - {len(products)} продуктов") 
    print(f"   - {len(admins)} админов")
    print(f"📁 Файл сохранён: migration_data.sql")
    
    sqlite_conn.close()

if __name__ == "__main__":
    export_sqlite_to_sql() 