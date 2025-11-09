import requests
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm
import schedule

def get_book_data(book_url):
    """
    Получает данные о книге с одной страницы
    """
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Название (с проверкой)
        title_element = soup.find('h1')
        title = title_element.text.strip() if title_element else "Нет названия"

        # Цена (с проверкой)
        price_element = soup.find('p', class_='price_color')
        price = price_element.text.strip() if price_element else "Нет цены"

        # Рейтинг (с проверкой)
        rating_element = soup.find('p', class_='star-rating')
        if rating_element and len(rating_element.get('class', [])) > 1:
            rating = rating_element['class'][1]
        else:
            rating = "No rating"

        # В наличии (с проверкой)
        stock_element = soup.find('p', class_='instock availability')
        stock = "0"
        if stock_element:
            stock_text = stock_element.text
            stock_match = re.search(r'\((\d+) available\)', stock_text)
            if stock_match:
                stock = stock_match.group(1)

        # Описание (с проверкой)
        description_element = soup.find('div', id='product_description')
        description = "Нет описания"
        if description_element:
            description_sibling = description_element.find_next_sibling('p')
            if description_sibling:
                description = description_sibling.text.strip()

        # Таблица с дополнительной информацией (с проверкой)
        product_info = {}
        table = soup.find('table', class_='table table-striped')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                header_element = row.find('th')
                value_element = row.find('td')
                if header_element and value_element:
                    header = header_element.text.strip()
                    value = value_element.text.strip()
                    product_info[header] = value

        book_data = {
            'title': title,
            'price': price,
            'rating': rating,
            'stock': stock,
            'description': description,
            'upc': product_info.get('UPC', ''),
            'product_type': product_info.get('Product Type', ''),
            'price_excl_tax': product_info.get('Price (excl. tax)', ''),
            'price_incl_tax': product_info.get('Price (incl. tax)', ''),
            'tax': product_info.get('Tax', ''),
            'availability': product_info.get('Availability', ''),
            'number_of_reviews': product_info.get('Number of reviews', '')
        }

        return book_data

    except Exception as e:
        print(f"Ошибка в get_book_data: {e}")
        return {
            'title': f'Ошибка: {str(e)[:50]}',
            'price': '0',
            'rating': 'Zero',
            'stock': '0',
            'description': 'Ошибка загрузки',
            'upc': '',
            'product_type': '',
            'price_excl_tax': '',
            'price_incl_tax': '',
            'tax': '',
            'availability': '',
            'number_of_reviews': ''
        }


def scrape_books(is_save=False):
    """
    Собирает данные обо всех книгах с сайта
    """
    all_books = []
    book_urls = []
    page_number = 1

    print("Начинаем сбор данных о книгах...")

    # Собираем все URL книг без прогресс-бара
    while True:
        try:
            if page_number == 1:
                url = "http://books.toscrape.com/index.html"
            else:
                url = f"http://books.toscrape.com/catalogue/page-{page_number}.html"

            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            books = soup.find_all('article', class_='product_pod')

            if not books:
                break

            # Собираем URL книг с текущей страницы
            for book in books:
                link_tag = book.find('h3').find('a')
                if link_tag:
                    link = link_tag['href']
                    if link.startswith('../../../'):
                        full_url = link.replace('../../../', 'http://books.toscrape.com/catalogue/')
                    elif link.startswith('../'):
                        full_url = link.replace('../', 'http://books.toscrape.com/catalogue/')
                    elif link.startswith('catalogue/'):
                        full_url = 'http://books.toscrape.com/' + link
                    else:
                        full_url = 'http://books.toscrape.com/catalogue/' + link
                    book_urls.append(full_url)

            # Проверяем есть ли следующая страница
            next_button = soup.find('li', class_='next')
            if not next_button:
                break

            page_number += 1
            time.sleep(0.1)

        except Exception as e:
            print(f"Ошибка при поиске страниц: {e}")
            break

    print(f"Всего найдено книг: {len(book_urls)}")

    with tqdm(total=len(book_urls), desc="Обработка книг", unit="книга") as pbar:
        for book_url in book_urls:
            try:
                book_info = get_book_data(book_url)
                all_books.append(book_info)
                pbar.set_postfix(book=book_info['title'][:20])
                time.sleep(0.1)
            except Exception as e:
                pbar.set_postfix(error="Ошибка")
            finally:
                pbar.update(1)

    # Сохраняем в файл
    if is_save and all_books:
        try:
            with open('artifacts/books_data.txt', 'w', encoding='utf-8') as f:
                for i, (book_url, book) in enumerate(zip(book_urls, all_books), 1):
                    f.write(f"URL: {book_url}\n")
                    f.write(str(book))
                    f.write("\n\n")

            print(f"Сохранено {len(all_books)} книг в файл artifacts/books_data.txt")

        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
    elif is_save:
        print("Нет данных для сохранения")

    print(f"Обработано книг: {len(all_books)}")
    return all_books

def schedule_scrape_books() -> None:
    """
    Автоматически парсит книги со всех страниц сайта Books to Scrape.
    Расписание:
    - Основной запуск: ежедневно в 19:00
    """
    # Настройка ежедневного автоматического парсинга в 19:00
    schedule.every().day.at('19:00').do(scrape_books, is_save=True)

    # Проверки выполнения запланированных задач (каждые 60 секунд)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    print("Запуск парсинга")
    scrape_books(is_save=True)