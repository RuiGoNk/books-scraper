# Books Scraper

Проект для парсинга данных о книгах с сайта Books to Scrape.

## Цель проекта
Сбор информации о книгах: названия, цены, рейтинги, наличие и описание.

## Используемые библиотеки
- requests
- beautifulsoup4  
- tqdm
- schedule
- pytest

## Запуск проекта

1. Установите зависимости:
`pip install -r requirements.txt`

2. Запустите парсинг:
`python scraper.py`

## Структура проекта
- `scraper.py` - основной скрипт парсинга
- `tests/` - тесты проекта  
- `artifacts/` - результаты парсинга
- `notebooks/` - Jupyter ноутбуки
- `requirements.txt` - список зависимостей