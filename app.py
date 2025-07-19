from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
import json
from PIL import Image
import re
from db import db
from models import Admin
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

# Настройка базы данных
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Для PostgreSQL (продакшн)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Для SQLite (локальная разработка)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images/products'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Создаем директорию для загрузки файлов, если она не существует
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

from models import *

with app.app_context():
    db.create_all()

# Тестовые данные корзины
cart_items = [
    {
        'id': 1,
        'title': 'DJI Mini 3 Pro',
        'image': '/static/images/products/mini-3-pro.jpg',
        'price': 89900,
        'quantity': 2
    }
]

# Данные о продуктах
products = {
    1: {
        'id': 1,
        'title': 'DJI Mini 3 Pro',
        'description': 'Компактный дрон с 4K HDR видео',
        'price': 89900,
        'image': '/static/images/products/mini-3-pro.jpg',
        'features': [
            'Время полёта: до 34 минут',
            'Дальность передачи: 12 км',
            'Вес: 249 грамм',
            'Камера: 4K HDR',
            'Максимальная скорость: 57.6 км/ч'
        ],
        'specs': {
            'Вес (с аккумулятором)': '249 г',
            'Размеры в сложенном виде': '145×90×62 мм',
            'Размеры в разложенном виде': '171×245×62 мм',
            'Максимальная скорость': '57.6 км/ч',
            'Максимальное время полёта': '34 минуты',
            'Максимальная дальность': '12 км',
            'Рабочая температура': '-10° до 40° C',
            'Спутниковые системы': 'GPS, ГЛОНАСС, Galileo',
            'Камера': '4K HDR',
            'Стабилизация': '3-осевой стабилизатор',
            'Встроенная память': '64 ГБ'
        }
    },
    2: {
        'id': 2,
        'title': 'DJI Air 2S',
        'description': 'Профессиональный дрон с 1-дюймовой матрицей и 5.4K видео',
        'price': 129900,
        'image': '/static/images/products/air-2s.jpg'
    },
    3: {
        'id': 3,
        'title': 'DJI FPV Combo',
        'description': 'Полный комплект для иммерсивных полетов от первого лица',
        'price': 149900,
        'image': '/static/images/products/fpv-combo.jpg'
    }
}

def optimize_image(image_path, max_size=(800, 800), quality=85):
    """Оптимизирует изображение, сохраняя пропорции"""
    try:
        with Image.open(image_path) as img:
            # Конвертируем в RGB, если изображение в другом формате
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Получаем текущие размеры
            width, height = img.size
            
            # Определяем, какая сторона больше
            if width > height:
                # Горизонтальное изображение
                new_width = min(width, max_size[0])
                new_height = int(height * (new_width / width))
            else:
                # Вертикальное изображение
                new_height = min(height, max_size[1])
                new_width = int(width * (new_height / height))
            
            # Изменяем размер, сохраняя пропорции
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Создаем новое изображение с белым фоном
            new_img = Image.new('RGB', max_size, (245, 245, 245))
            
            # Вычисляем позицию для центрирования
            x = (max_size[0] - new_width) // 2
            y = (max_size[1] - new_height) // 2
            
            # Вставляем изображение в центр
            new_img.paste(img, (x, y))
            
            # Сохраняем оптимизированное изображение
            new_img.save(image_path, 'JPEG', quality=quality, optimize=True)
    except Exception as e:
        print(f"Ошибка при оптимизации изображения {image_path}: {e}")

def make_safe_key(key):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', key)

@app.route('/')
def index():
    categories = Category.query.all()
    products = Product.query.all()
    cart = session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('index.html', 
                         categories=categories,
                         products=products,
                         selected_category=None,
                         cart_count=cart_count,
                         cart_total=cart_total)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Преобразуем JSON поля в Python объекты
    if product.advantages:
        try:
            product.advantages = json.loads(product.advantages) if isinstance(product.advantages, str) else product.advantages
        except:
            product.advantages = []
    
    if product.specifications:
        try:
            product.specifications = json.loads(product.specifications) if isinstance(product.specifications, str) else product.specifications
        except:
            product.specifications = {}
    
    if product.options:
        try:
            product.options = json.loads(product.options) if isinstance(product.options, str) else product.options
        except:
            product.options = {}
    
    return render_template('product.html', product=product)

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        user = {
            'name': 'Гость',
            'id': '',
            'username': '',
            'avatar_url': 'https://via.placeholder.com/64'
        }
    return render_template('profile.html', user=user)

@app.route('/orders')
def orders():
    user = session.get('user', {})
    orders = []
    if user.get('id'):
        orders = Order.query.filter_by(user_id=user['id']).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/balance')
def balance():
    return render_template('balance.html')

@app.route('/address')
def address():
    return render_template('address.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/test_order')
def test_order():
    return render_template('test_order.html')

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = [{'key': k, 'safe_key': make_safe_key(k), **v} for k, v in cart.items()]
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/pay')
def pay():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('pay.html', total=total, bonus_available=500.00, bonus_can_use=85.00)

@app.route('/ton')
def pay_method_ton():
    order_id = request.args.get('order_id')
    order = Order.query.get(order_id) if order_id else None
    total = order.total if order else 0
    return render_template('ton.html', order_id=order_id, order=order, total=total)

@app.route('/spb')
def pay_method_spb():
    order_id = request.args.get('order_id')
    order = Order.query.get(order_id) if order_id else None
    total = order.total if order else 0
    return render_template('spb.html', order_id=order_id, order=order, total=total)

@app.route('/cart/update_quantity', methods=['POST'])
def update_cart_quantity():
    data = request.get_json()
    item_key = data.get('item_id')
    delta = data.get('delta')
    if not item_key or delta is None:
        return jsonify({'success': False, 'error': 'Missing required parameters'})
    cart = session.get('cart', {})
    if str(item_key) in cart:
        new_quantity = cart[str(item_key)]['quantity'] + delta
        if new_quantity <= 0:
            del cart[str(item_key)]
        else:
            cart[str(item_key)]['quantity'] = new_quantity
        session['cart'] = cart
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        return jsonify({
            'success': True,
            'total': total
        })
    return jsonify({'success': False, 'error': 'Item not found'})

@app.route('/cart/remove_item', methods=['POST'])
def remove_cart_item():
    data = request.get_json()
    item_key = data.get('item_id')
    if not item_key:
        return jsonify({'success': False, 'error': 'Missing item_id'})
    cart = session.get('cart', {})
    if str(item_key) in cart:
        del cart[str(item_key)]
        session['cart'] = cart
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        return jsonify({
            'success': True,
            'total': total
        })
    return jsonify({'success': False, 'error': 'Item not found'})

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    selected_options = data.get('options', [])
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    # Получаем текущую корзину из сессии или создаем новую
    cart = session.get('cart', {})
    # Считаем итоговую цену с учётом опций
    base_price = float(product.price)
    options_price = 0
    options_dict = product.options or {}
    options_text = []
    for opt in selected_options:
        price = options_dict.get(opt, 0)
        options_price += float(price)
        options_text.append(f"{opt} (+{int(price)} ₽)" if price else opt)
    total_price = base_price + options_price
    # Ключ для уникальности товара с опциями
    cart_key = f"{product_id}-{'-'.join(sorted(selected_options))}" if selected_options else str(product_id)
    if cart_key in cart:
        cart[cart_key]['quantity'] += 1
    else:
        cart[cart_key] = {
            'id': product.id,
            'title': product.title,
            'price': total_price,
            'image': product.image,
            'quantity': 1,
            'options': options_text if options_text else None
        }
    session['cart'] = cart
    total_items = sum(item['quantity'] for item in cart.values())
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
    return jsonify({
        'success': True,
        'cart_count': total_items,
        'cart_total': total_amount,
        'message': 'Товар добавлен в корзину'
    })

# Маршруты для админ-панели
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    products_count = Product.query.count()
    categories_count = Category.query.count()
    recent_products = Product.query.order_by(Product.id.desc()).limit(5).all()
    return render_template('admin/dashboard.html', 
                         products_count=products_count,
                         categories_count=categories_count,
                         recent_products=recent_products)

@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/category/add', methods=['POST'])
@login_required
def admin_add_category():
    name = request.form.get('name')
    print(f"Adding category: {name}")  # Логирование
    if name:
        category = Category(name=name)
        db.session.add(category)
        try:
            db.session.commit()
            print("Category added successfully")  # Логирование
            flash('Категория успешно добавлена')
        except Exception as e:
            print(f"Error adding category: {e}")  # Логирование
            db.session.rollback()
            flash('Ошибка при добавлении категории')
    return redirect(url_for('admin_categories'))

@app.route('/admin/category/edit', methods=['POST'])
@login_required
def admin_edit_category():
    category_id = request.form.get('category_id')
    name = request.form.get('name')
    category = Category.query.get(category_id)
    if category and name:
        category.name = name
        db.session.commit()
        flash('Категория успешно обновлена')
    return redirect(url_for('admin_categories'))

@app.route('/admin/category/delete', methods=['POST'])
@login_required
def admin_delete_category():
    data = request.get_json()
    category_id = data.get('category_id')
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/admin/product/add', methods=['POST'])
@login_required
def admin_add_product():
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    price = request.form.get('price')
    description = request.form.get('description')
    
    # Обработка JSON полей
    def parse_json_field(field_value):
        if not field_value:
            return None
        try:
            return json.loads(field_value)
        except json.JSONDecodeError:
            # Если это не валидный JSON, создаем список из строк
            if isinstance(field_value, str):
                return [line.strip() for line in field_value.split('\n') if line.strip()]
            return None
    
    advantages = parse_json_field(request.form.get('advantages'))
    specifications = parse_json_field(request.form.get('specifications'))
    options = parse_json_field(request.form.get('options'))
    
    # Обработка загрузки изображений
    image = None
    images = []
    if 'image' in request.files:
        file = request.files['image']
        if file.filename:
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            filename = secure_filename(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            optimize_image(file_path)  # Оптимизируем основное изображение
            image = filename
    
    # Обработка дополнительных изображений
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file.filename:
                ext = os.path.splitext(file.filename)[1]
                filename = f"{uuid.uuid4().hex}{ext}"
                filename = secure_filename(filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                optimize_image(file_path)  # Оптимизируем каждое дополнительное изображение
                images.append(filename)
    
    # Создаем новый продукт
    product = Product(
        title=title,
        category_id=category_id,
        price=price,
        description=description,
        image=image,
        images=images,
        advantages=advantages,
        specifications=specifications,
        options=options
    )
    
    db.session.add(product)
    db.session.commit()
    
    flash('Товар успешно добавлен', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/product/edit/<int:product_id>', methods=['POST'])
@login_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    product.title = request.form.get('title')
    product.category_id = request.form.get('category_id')
    product.price = request.form.get('price')
    product.description = request.form.get('description')
    
    # Обработка JSON полей
    def parse_json_field(field_value):
        if not field_value:
            return None
        try:
            return json.loads(field_value)
        except json.JSONDecodeError:
            # Если это не валидный JSON, создаем список из строк
            if isinstance(field_value, str):
                return [line.strip() for line in field_value.split('\n') if line.strip()]
            return None
    
    product.advantages = parse_json_field(request.form.get('advantages'))
    product.specifications = parse_json_field(request.form.get('specifications'))
    product.options = parse_json_field(request.form.get('options'))
    
    # Обработка загрузки основного изображения
    if 'image' in request.files:
        file = request.files['image']
        if file.filename:
            # Удаляем старое изображение, если оно существует
            if product.image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            filename = secure_filename(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            optimize_image(file_path)  # Оптимизируем новое основное изображение
            product.image = filename
    
    # Обработка загрузки дополнительных изображений
    if 'images' in request.files:
        files = request.files.getlist('images')
        new_images = []
        for file in files:
            if file.filename:
                ext = os.path.splitext(file.filename)[1]
                filename = f"{uuid.uuid4().hex}{ext}"
                filename = secure_filename(filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                optimize_image(file_path)  # Оптимизируем каждое новое дополнительное изображение
                new_images.append(filename)
        
        # Удаляем старые дополнительные изображения
        if product.images:
            for old_image in product.images:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
        
        product.images = new_images
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/product/delete', methods=['POST'])
@login_required
def admin_delete_product():
    product_id = request.form.get('product_id')
    product = Product.query.get_or_404(product_id)
    
    # Удаляем файл изображения, если он существует
    if product.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/product/<int:product_id>')
@login_required
def admin_get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': product.price,
        'image': product.image,
        'category_id': product.category_id,
        'advantages': product.advantages,
        'specifications': product.specifications,
        'options': product.options
    })

@app.route('/category/<int:category_id>')
def category(category_id):
    if category_id == 0:
        products = Product.query.all()
    else:
        products = Product.query.filter_by(category_id=category_id).all()
    
    # Преобразуем продукты в JSON формат
    products_data = [{
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': product.price,
        'image': product.image
    } for product in products]
    
    return jsonify({
        'products': products_data
    })

@app.route('/admin/fix-images')
@login_required
def admin_fix_images():
    """Проверяет и исправляет отсутствующие изображения продуктов"""
    products = Product.query.all()
    fixed = 0
    for product in products:
        if product.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
            if not os.path.exists(image_path):
                # Если изображение отсутствует, устанавливаем заглушку
                product.image = 'placeholder.jpg'
                fixed += 1
    
    if fixed > 0:
        db.session.commit()
        flash(f'Исправлено {fixed} отсутствующих изображений', 'success')
    else:
        flash('Все изображения на месте', 'info')
    
    return redirect(url_for('admin_products'))

@app.route('/api/telegram_user', methods=['POST'])
def telegram_user():
    data = request.get_json()
    session['user'] = {
        'id': data.get('user_id'),
        'name': f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
        'username': data.get('username'),
        'avatar_url': data.get('photo_url')
    }
    return jsonify({'success': True})

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.get_json()
    user = session.get('user', {})
    cart = session.get('cart', {})
    
    if not cart:
        return jsonify({'success': False, 'error': 'Корзина пуста'}), 400
    
    # Получаем данные из формы
    address = data.get('address')
    phone = data.get('phone')
    fio = data.get('fio')
    payment_method = data.get('payment_method')
    delivery_method = data.get('delivery_method')
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Генерируем номер заказа
    user_id = user.get('id')
    if not user_id:
        # Если пользователь не авторизован, используем временный ID
        user_id = 'guest'
    
    # Находим последний заказ этого пользователя
    last_order = Order.query.filter_by(user_id=user_id).order_by(Order.id.desc()).first()
    if last_order and last_order.order_number:
        # Извлекаем номер из последнего заказа и увеличиваем на 1
        try:
            last_number = int(last_order.order_number.split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            new_number = 1
    else:
        new_number = 1
    
    order_number = f"{user_id}-{new_number}"
    
    # Создаем заказ
    order = Order(
        user_id=user_id,
        username=user.get('username'),
        phone=phone,
        address=address,
        fio=fio,
        payment_method=payment_method,
        delivery_method=delivery_method,
        total=total,
        order_number=order_number
    )
    db.session.add(order)
    db.session.commit()  # чтобы получить order.id
    
    # Добавляем товары заказа
    for item in cart.values():
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.get('id'),
            title=item.get('title'),
            price=item.get('price'),
            quantity=item.get('quantity'),
            options=item.get('options')
        )
        db.session.add(order_item)
    db.session.commit()
    
    # Очищаем корзину
    session['cart'] = {}
    return jsonify({'success': True, 'order_id': order.id, 'order_number': order_number})

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('status')
    
    if not order_id or not new_status:
        return jsonify({'success': False, 'error': 'Неверные параметры'}), 400
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404
    
    # Проверяем, что пользователь может изменять этот заказ
    user = session.get('user', {})
    user_id = user.get('id')
    
    # Если пользователь не авторизован, разрешаем обновление по номеру заказа
    if not user_id:
        # Проверяем, что заказ существует и не был уже обработан
        if order.status in ['Принят в работу', 'Отменен']:
            return jsonify({'success': False, 'error': 'Заказ уже обработан'}), 400
    else:
        # Если пользователь авторизован, проверяем права доступа
        if str(order.user_id) != str(user_id):
            return jsonify({'success': False, 'error': 'Нет доступа к заказу'}), 403
    
    # Обновляем статус
    if new_status == 'paid':
        order.status = 'Принят в работу'
    elif new_status == 'cancelled':
        order.status = 'Отменен'
    else:
        return jsonify({'success': False, 'error': 'Неверный статус'}), 400
    
    db.session.commit()
    return jsonify({'success': True, 'status': order.status})

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/guarantee')
def guarantee():
    return render_template('guarantee.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# Для Vercel
app.debug = False