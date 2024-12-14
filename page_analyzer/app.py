from datetime import datetime

import psycopg2
from flask import Flask, flash, redirect, render_template, request, url_for
from page_analyzer.config import DATABASE_URL, SECRET_KEY
from page_analyzer.db_operators.url_service import get_url_and_checks
from page_analyzer.url_check import handle_check_url
from page_analyzer.validate import normalize_url, validate_url

app = Flask(__name__)
app.config['DATABASE_URL'] = DATABASE_URL
app.config['SECRET_KEY'] = SECRET_KEY


try:
    # Пытаемся подключиться к базе данных
    conn = psycopg2.connect(app.config['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    print('Установлено соединение с базой данных')
except KeyError:
    print('DATABASE_URL не найден в конфигурации приложения')
except psycopg2.OperationalError:
    # В случае сбоя подключения будет выведено сообщение
    print('Невозможно установить соединение с базой данных')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form.get('url')
    # Валидация URL
    if not validate_url(url):
        return redirect(url_for('home'))
    # Нормализация URL
    url = normalize_url(url)
    # Добавление URL в базу данных
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            # Проверка на существование URL
            cursor.execute('SELECT id FROM urls WHERE name = %s', (url,))
            existing_url = cursor.fetchone()
            if existing_url:
                flash('Страница уже существует', 'error')
                return redirect(url_for('home'))

        # =====================
        # Добавление URL в базу данных
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s)\
                RETURNING id", (url, created_at))
            new_url_id = cursor.fetchone()[0]  # Получаем ID нового URL
            conn.commit()
            flash('Страница успешно добавлена!', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении URL: {e}', 'error')
    finally:
        if 'conn' in locals():
            conn.close()
    # Перенаправление на страницу с деталями добавленного URL
    return redirect(url_for('show_url', id=new_url_id))


@app.route('/urls')
def urls():
    """Обработчик маршрута для отображения списка URL с их проверками."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            # Извлечение URL и их последних проверок
            cursor.execute("""
                SELECT u.id, u.name, u.created_at, uc.status_code
                FROM urls u
                LEFT JOIN (
                    SELECT url_id, status_code
                    FROM url_checks
                    WHERE id IN (
                        SELECT MAX(id) FROM url_checks GROUP BY url_id
                    )
                ) uc ON u.id = uc.url_id
                ORDER BY u.created_at DESC
            """)
            urls = cursor.fetchall()
    except Exception as e:
        flash(f'Ошибка при получении URL: {e}', 'error')
        urls = []
    finally:
        if 'conn' in locals():
            conn.close()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    """Маршрут для отображения списка URL и его проверок."""
    url, checks = get_url_and_checks(id)
    if not url:
        flash('URL не найден', 'error')
        return redirect(url_for('urls'))
    return render_template('url.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    """Обработчик маршрута для проверки URL."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return handle_check_url(conn, id)
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=False)
