from app import app, db, Admin

def create_admin(username, password):
    with app.app_context():
        # Проверяем, существует ли уже администратор
        if Admin.query.first():
            print("Администратор уже существует")
            return
        
        # Создаем нового администратора
        admin = Admin(username=username)
        admin.set_password(password)
        
        # Добавляем в базу данных
        db.session.add(admin)
        db.session.commit()
        
        print(f"Администратор {username} успешно создан")

if __name__ == '__main__':
    username = input("Введите имя пользователя: ")
    password = input("Введите пароль: ")
    create_admin(username, password) 