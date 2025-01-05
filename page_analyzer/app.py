from datetime import datetime

import psycopg2
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.config import DATABASE_URL, SECRET_KEY
from page_analyzer.db_operators.url_service import (
    get_url_and_checks,
    get_urls_with_checks,
)
from page_analyzer.url_check import handle_check_url
from page_analyzer.validate import (
    add_url_to_db,
    check_existing_url,
    normalize_url,
    validate_url,
)

app = Flask(__name__)
app.config['DATABASE_URL'] = DATABASE_URL
app.config['SECRET_KEY'] = SECRET_KEY


def get_db_connection():
    """Создает и возвращает соединение с базой данных."""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='prefer')
        print('Установлено соединение с базой данных')
        return conn
    except KeyError:
        print('DATABASE_URL не найден в конфигурации приложения')
        return None
    except psycopg2.OperationalError:
        print('Невозможно установить соединение с базой данных')
        return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form.get('url')
    # Валидация URL
    errors = validate_url(url)
    if errors:
        return render_template('index.html', errors=errors), 422
    # Нормализация URL
    normalized_url = normalize_url(url)
    # Проверка на существование URL
    existing_url_id = check_existing_url(normalized_url)
    if existing_url_id:
        flash('Страница уже существует', 'success')
        return redirect(url_for('show_url', id=existing_url_id))

    # Добавление URL в базу данных
    date = datetime.now()
    is_added, new_url_id = add_url_to_db(
        app.config['DATABASE_URL'], normalized_url, date)
    if is_added:
        flash('Страница успешно добавлена!', 'success')
    else:
        flash('Произошла ошибка при проверке', 'error')
    return redirect(url_for('show_url', id=new_url_id))


@app.route('/urls')
def urls():
    """Обработчик маршрута для отображения списка URL с их проверками."""
    urls = get_urls_with_checks()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id: int):
    """Маршрут для отображения URL и его проверок."""
    try:
        url, checks = get_url_and_checks(id)
        if not url:
            flash('URL не найден', 'error')
            return redirect(url_for('urls'))
        return render_template('url.html', url=url, checks=checks)
    except Exception as e:
        flash(f'Произошла ошибка: {e}', 'error')
        return redirect(url_for('urls'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    """Обработчик маршрута для проверки URL."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return handle_check_url(conn, id)
    except Exception as e:
        flash(f'Ошибка при подключении к базе данных: {e}', 'error')
        return redirect(url_for('urls'))
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(debug=False)
