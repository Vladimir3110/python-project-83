def get_url_and_checks(cursor, url_id):
    """Получает URL и все проверки для данного URL из базы данных."""
    cursor.execute(
        'SELECT id, name, created_at FROM urls WHERE id = %s', (url_id,)
    )
    url = cursor.fetchone()
    if not url:
        return None, None  # Если URL не найден, возвращаем None
    # Получаем все проверки для данного URL
    cursor.execute(
        'SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC',
        (url_id,)
    )
    checks = cursor.fetchall()

    return url, checks  # Возвращаем URL и проверки
