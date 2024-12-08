import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) "
                  "Gecko/20100101 Firefox/53.0",
    "Referer": "https://www.similarweb.com/",
    "Accept-Language": "en-US,en;q=0.5"
}


def check_seo(url):
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # Проверка на ошибки HTTP
        # Выводим HTML-код страницы в консоль для отладки
        print(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')  # html.parser
        title = soup.title.string if soup.title else 'Нет заголовка'
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else 'Нет описания'

        return {
            'title': title,
            'description': description,
            'status_code': response.status_code
        }
    except Exception as e:
        print(f"Ошибка при проверке SEO: {e}")  # ошибка в консоль для отладки
        # Возвращаем None, если произошла ошибка
        return {
            'status_code': None,
            'title': None,
            'description': None,
            'error': str(e)
        }
