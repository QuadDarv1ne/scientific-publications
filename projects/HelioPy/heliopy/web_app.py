"""Flask-приложение HelioPy

Позволяет запускать веб-интерфейс с различными страницами:
- /              главная
- /analysis      анализ данных
- /visualization визуализация
- /api-docs      документация и API
- /about         о проекте
- /api/info      машинный эндпоинт с базовой информацией

Используйте main() для запуска из CLI: `python -m heliopy web`.
"""
from __future__ import annotations

from pathlib import Path
from flask import Flask, render_template, jsonify
import heliopy

# Определяем путь к шаблонам внутри установленного пакета
TEMPLATE_DIR = Path(__file__).parent / "templates"
app = Flask(__name__, template_folder=str(TEMPLATE_DIR))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


@app.route("/visualization")
def visualization():
    return render_template("visualization.html")


@app.route("/api-docs")
def api_docs():
    return render_template("api.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/api/info")
def info():
    return jsonify(
        {
            "name": "HelioPy",
            "description": "Библиотека для анализа солнечной активности и космической погоды",
            "version": getattr(heliopy, "__version__", "0.1.0"),
        }
    )


@app.route("/ping")
def ping():
    """Простой health-check маршрут."""
    return jsonify({"status": "ok"})


def main(host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> int:
    """Точка входа для запуска из CLI.

    Parameters
    ----------
    host: str
        Адрес для бинда
    port: int
        Порт для сервера
    debug: bool
        Режим отладки Flask
    """
    app.run(debug=debug, host=host, port=port)
    return 0


if __name__ == "__main__":  # Локальный запуск
    main(debug=True)
