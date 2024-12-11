import psycopg2
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.config import DATABASE_URL, SECRET_KEY
from page_analyzer.db_operators.database import (
    add_url_check_to_db,
    add_url_to_db,
)
from page_analyzer.db_operators.url_service import get_url_and_checks
from page_analyzer.parser import check_seo
from page_analyzer.url_check import handle_check_url
from page_analyzer.validate import (
    check_url_length,
    normalize_url,
    validate_url,
)

app = Flask(__name__)
app.config['DATABASE_URL'] = DATABASE_URL
app.config['SECRET_KEY'] = SECRET_KEY


try:
    # Пытаемся подключиться к базе данных
    conn = psycopg2.connect(app.config['DATABASE_URL'], sslmode='require')
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

    # Проверка длины URL
    if not check_url_length(url):
        return redirect(url_for('home'))

    # Проверяем SEO-параметры и получаем код ответа
    seo_data = check_seo(url)
    status_code = seo_data.get('status_code', None)

    # Добавление URL в базу данных
    try:
        with conn.cursor() as cursor:  # контекстный менеджер для курсора
            url_id = add_url_to_db(cursor, url)
            if url_id is not None and status_code is not None:
                add_url_check_to_db(cursor, url_id, status_code)
            conn.commit()
            flash('URL успешно добавлен!', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении URL: {e}', 'error')
    return redirect(url_for('list_urls'))

#    try:
#        cursor = conn.cursor()
#        url_id = add_url_to_db(cursor, url)
#        if url_id is not None and status_code is not None:
#            add_url_check_to_db(cursor, url_id, status_code)
#        conn.commit()
#        flash('URL успешно добавлен!', 'success')
#    except Exception as e:
#        flash(f'Ошибка при добавлении URL: {e}', 'error')
#    return redirect(url_for('list_urls'))


@app.route('/urls', methods=['GET'])
def list_urls():
    cursor.execute('''
        SELECT u.id, u.name,
               (
                   SELECT MAX(created_at)
                   FROM url_checks
                   WHERE url_id = u.id
               ) AS last_check,
               (
                   SELECT status_code
                   FROM url_checks
                   WHERE url_id = u.id
                   ORDER BY created_at DESC
                   LIMIT 1
               ) AS status_code
        FROM urls u
        ORDER BY u.created_at DESC
    ''')
    urls = cursor.fetchall()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    """Маршрут для отображения URL и его проверок."""
    url, checks = get_url_and_checks(cursor, id)
    if not url:
        return 'URL не найден', 404  # Если URL не найден, возвращаем 404

    return render_template('url.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    """Обработчик маршрута для проверки URL."""
    return handle_check_url(cursor, conn, id)


if __name__ == '__main__':
    app.run(debug=False)
