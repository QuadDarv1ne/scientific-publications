"""Локальный шім для запуска веб-приложения из корня репозитория.

Предпочтительно использовать: `python -m heliopy web`.
Этот файл просто проксирует запуск к heliopy.web_app.main().
"""

from heliopy.web_app import main

if __name__ == "__main__":
    # Запуск с настройками по умолчанию
    main(host="127.0.0.1", port=5000, debug=True)
