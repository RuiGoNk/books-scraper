import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import get_book_data, scrape_books


class TestBookParser:
    """Тесты для функций парсинга книг"""

    def test_get_book_data_returns_dict(self):
        """Тест: get_book_data возвращает словарь"""
        # Используем реальный URL для тестирования
        test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        result = get_book_data(test_url)

        assert isinstance(result, dict), "Функция должна возвращать словарь"

    def test_get_book_data_has_required_keys(self):
        """Тест: словарь содержит все необходимые ключи"""
        test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        result = get_book_data(test_url)

        required_keys = [
            'title', 'price', 'rating', 'stock', 'description',
            'upc', 'product_type', 'price_excl_tax', 'price_incl_tax',
            'tax', 'availability', 'number_of_reviews'
        ]

        for key in required_keys:
            assert key in result, f"Отсутствует ключ: {key}"

    def test_get_book_data_title_not_empty(self):
        """Тест: название книги не пустое"""
        test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        result = get_book_data(test_url)

        assert result['title'] != "", "Название книги не должно быть пустым"
        assert len(result['title']) > 0, "Название книги должно содержать текст"
        assert result['title'] != "Нет названия", "Название должно быть получено"

    def test_scrape_books_returns_list(self):
        """Тест: scrape_books возвращает список"""
        # Ограничиваем сбор 1 страницей для быстрого теста
        result = scrape_books(is_save=False)

        assert isinstance(result, list), "Функция должна возвращать список"

    def test_scrape_books_contains_books(self):
        """Тест: scrape_books возвращает непустой список книг"""
        result = scrape_books(is_save=False)

        assert len(result) > 0, "Список книг не должен быть пустым"
        assert all(isinstance(book, dict) for book in result), "Все элементы должны быть словарями"


if __name__ == "__main__":
    # Запуск тестов вручную
    test_class = TestBookParser()

    print("ЗАПУСК АВТОТЕСТОВ")

    tests = [
        ("get_book_data возвращает словарь", test_class.test_get_book_data_returns_dict),
        ("словарь содержит все необходимые ключи", test_class.test_get_book_data_has_required_keys),
        ("название книги не пустое", test_class.test_get_book_data_title_not_empty),
        ("scrape_books возвращает список", test_class.test_scrape_books_returns_list),
        ("scrape_books возвращает непустой список книг", test_class.test_scrape_books_contains_books),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"PASS: {test_name}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_name}")
            print(f"   Ошибка: {e}")
            failed += 1

    print(f"Результат: {passed} passed, {failed} failed")

    if failed == 0:
        print("Все тесты прошли успешно!")
    else:
        print("Некоторые тесты не прошли")