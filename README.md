## Установка и запуск

1. Клонировать репозиторий
2. Создать виртуальное окружение: `python -m venv venv`
3. Активировать: `venv\Scripts\activate`
4. Установить зависимости: `pip install -r requirements.txt`
5. Создать базу данных PostgreSQL: `createdb -U postgres mywebapp_db`
6. Импортировать данные: `pg_restore -U postgres -d mywebapp_db database.dump`
7. В файле `app/config.py` указать свой пароль от PostgreSQL
8. Запустить: `python run.py`
9. Открыть в браузере: `http://127.0.0.1:5000/`

## Суперпользователь
Логин: Sanay
Пароль: Sanay123
