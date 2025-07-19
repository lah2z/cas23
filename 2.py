from app import app, db, Product, Category
import json

def generate_test_products():
    with app.app_context():
        # Создаем категории, если их нет
        categories = {
            'Смартфоны': Category.query.filter_by(name='Смартфоны').first() or Category(name='Смартфоны'),
            'Ноутбуки': Category.query.filter_by(name='Ноутбуки').first() or Category(name='Ноутбуки'),
            'Планшеты': Category.query.filter_by(name='Планшеты').first() or Category(name='Планшеты'),
            'Аксессуары': Category.query.filter_by(name='Аксессуары').first() or Category(name='Аксессуары')
        }
        
        for category in categories.values():
            if not category.id:
                db.session.add(category)
        db.session.commit()

        # Тестовые продукты
        products = [
            {
                'title': 'iPhone 15 Pro Max',
                'category': categories['Смартфоны'],
                'price': 129990,
                'description': 'Флагманский смартфон Apple с процессором A17 Pro, камерой 48 Мп и дисплеем 6.7"',
                'advantages': [
                    'Процессор A17 Pro для максимальной производительности',
                    'Камера 48 Мп с улучшенной стабилизацией',
                    'Дисплей Super Retina XDR 6.7"',
                    'Титановый корпус повышенной прочности',
                    'Поддержка USB-C'
                ],
                'specifications': {
                    'Процессор': 'A17 Pro',
                    'Оперативная память': '8 ГБ',
                    'Встроенная память': '256 ГБ',
                    'Дисплей': '6.7" Super Retina XDR',
                    'Камера': '48 Мп + 12 Мп + 12 Мп',
                    'Аккумулятор': '4422 мАч',
                    'Вес': '221 г'
                },
                'options': {
                    'Дополнительная гарантия 1 год': 5000,
                    'Чехол Apple Silicone': 2990,
                    'MagSafe зарядное устройство': 3990,
                    'AirPods Pro': 19990
                }
            },
            {
                'title': 'MacBook Pro 16" M2 Max',
                'category': categories['Ноутбуки'],
                'price': 249990,
                'description': 'Профессиональный ноутбук с процессором M2 Max, дисплеем Liquid Retina XDR и до 96 ГБ памяти',
                'advantages': [
                    'Процессор M2 Max с 12 ядрами CPU и 38 ядрами GPU',
                    'Дисплей Liquid Retina XDR 16.2"',
                    'До 96 ГБ унифицированной памяти',
                    'До 8 ТБ SSD',
                    'До 22 часов автономной работы'
                ],
                'specifications': {
                    'Процессор': 'M2 Max',
                    'Оперативная память': '32 ГБ',
                    'SSD': '1 ТБ',
                    'Дисплей': '16.2" Liquid Retina XDR',
                    'Графика': '38-ядерный GPU',
                    'Порты': '3x Thunderbolt 4, HDMI, SDXC',
                    'Вес': '2.1 кг'
                },
                'options': {
                    'Дополнительная гарантия 3 года': 15000,
                    'Magic Mouse': 5990,
                    'Magic Keyboard': 8990,
                    'Thunderbolt Display': 29990
                }
            },
            {
                'title': 'iPad Pro 12.9" M2',
                'category': categories['Планшеты'],
                'price': 109990,
                'description': 'Профессиональный планшет с процессором M2, дисплеем Liquid Retina XDR и поддержкой Apple Pencil',
                'advantages': [
                    'Процессор M2 для профессиональных задач',
                    'Дисплей Liquid Retina XDR 12.9"',
                    'Поддержка Apple Pencil 2',
                    'Камера 12 Мп с LiDAR',
                    'Поддержка Magic Keyboard'
                ],
                'specifications': {
                    'Процессор': 'M2',
                    'Оперативная память': '8 ГБ',
                    'Встроенная память': '256 ГБ',
                    'Дисплей': '12.9" Liquid Retina XDR',
                    'Камера': '12 Мп + 10 Мп',
                    'Аккумулятор': '40.88 Вт·ч',
                    'Вес': '682 г'
                },
                'options': {
                    'Apple Pencil 2': 10990,
                    'Magic Keyboard': 29990,
                    'Smart Folio': 5990,
                    'Дополнительная гарантия 2 года': 8000
                }
            },
            {
                'title': 'AirPods Pro 2',
                'category': categories['Аксессуары'],
                'price': 24990,
                'description': 'Беспроводные наушники с активным шумоподавлением и пространственным звуком',
                'advantages': [
                    'Активное шумоподавление',
                    'Пространственный звук',
                    'Адаптивный режим прозрачности',
                    'До 6 часов работы',
                    'Водостойкость IPX4'
                ],
                'specifications': {
                    'Тип': 'Беспроводные наушники',
                    'Подключение': 'Bluetooth 5.3',
                    'Время работы': 'До 6 часов',
                    'Зарядка': 'MagSafe, Lightning, Qi',
                    'Водостойкость': 'IPX4',
                    'Вес': '5.3 г (каждый наушник)'
                },
                'options': {
                    'Чехол для зарядки MagSafe': 2990,
                    'Дополнительные амбушюры': 990,
                    'Дополнительная гарантия 1 год': 2000
                }
            }
        ]

        # Добавляем продукты в базу данных
        for product_data in products:
            product = Product(
                title=product_data['title'],
                category_id=product_data['category'].id,
                price=product_data['price'],
                description=product_data['description'],
                advantages=product_data['advantages'],
                specifications=product_data['specifications'],
                options=product_data['options']
            )
            db.session.add(product)
        
        try:
            db.session.commit()
            print("Тестовые продукты успешно добавлены в базу данных")
        except Exception as e:
            print(f"Ошибка при добавлении продуктов: {e}")
            db.session.rollback()

if __name__ == '__main__':
    generate_test_products() 