from app import app, db, Order
from sqlalchemy import text

def migrate_order_numbers():
    with app.app_context():
        # Добавляем колонку order_number, если её нет
        try:
            db.engine.execute(text("ALTER TABLE `order` ADD COLUMN order_number VARCHAR(100)"))
            print("Колонка order_number добавлена")
        except Exception as e:
            print(f"Колонка уже существует или ошибка: {e}")
        
        # Получаем все заказы
        orders = Order.query.all()
        
        # Группируем заказы по пользователю
        user_orders = {}
        for order in orders:
            user_id = order.user_id or 'unknown'
            if user_id not in user_orders:
                user_orders[user_id] = []
            user_orders[user_id].append(order)
        
        # Генерируем номера заказов для каждого пользователя
        for user_id, user_order_list in user_orders.items():
            # Сортируем заказы по дате создания
            user_order_list.sort(key=lambda x: x.created_at)
            
            for i, order in enumerate(user_order_list, 1):
                order_number = f"{user_id}-{i}"
                order.order_number = order_number
                print(f"Заказ {order.id}: {order_number}")
        
        # Сохраняем изменения
        db.session.commit()
        print("Миграция завершена успешно!")

if __name__ == "__main__":
    migrate_order_numbers() 