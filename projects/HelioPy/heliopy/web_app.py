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
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import heliopy
from heliopy.events.flare_detector import FlareDetector
from heliopy.utils.time_utils import TimeUtils
from heliopy.utils.math_utils import MathUtils

BASE_DIR = Path(__file__).parent
# Определяем путь к шаблонам и статике внутри установленного пакета
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))

# Секрет для сессий (для хранения языка)
if not app.secret_key:
    app.secret_key = "heliopy-dev-secret-key"

# -------------------- I18N --------------------
TRANSLATIONS = {
    "en": {
        "app_name": "HelioPy",
        "welcome": "Welcome to HelioPy web interface!",
        "tagline": "Analysis of solar activity and space weather.",
        "features_title": "Features:",
        "feature_1": "Data ingestion and processing from solar missions",
        "feature_2": "Solar flare and CME analysis",
        "feature_3": "Space weather forecasting",
        "feature_4": "Visualization and interactive charts",
        "nav_analysis": "Analysis",
        "nav_visualization": "Visualization",
        "nav_api_docs": "API & Docs",
        "nav_about": "About",
        "lang_en": "English",
        "lang_ru": "Русский",
        "index_title": "Home",
        "analysis_title": "Solar Data Analysis",
        "analysis_desc": "Run basic analysis operations via API.",
        "flare_peak_flux": "Peak flux (W/m²)",
        "btn_classify": "Classify",
        "carrington_rotation": "Carrington rotation",
        "time_utc": "Time (UTC)",
        "btn_compute": "Compute",
        "coords_convert": "Coordinate Conversion",
        "r": "r",
        "theta": "theta (rad)",
        "phi": "phi (rad)",
        "btn_convert": "Convert",
        "back_home": "← Back to home",
        "visualization_title": "Visualization",
        "visualization_desc": "Interactive charts, maps and event animations.",
        "api_docs_title": "API and Documentation",
        "api_docs_desc": "Available API endpoints and documentation links.",
        "api_info": "/api/info — Library information",
        "api_data": "/api/data — Data retrieval (example)",
        "docs_link": "HelioPy documentation",
        "about_title": "About HelioPy",
        "about_desc": "HelioPy is an open-source library for solar activity and space weather analysis.",
    },
    "ru": {
        "app_name": "HelioPy",
        "welcome": "Добро пожаловать в веб-интерфейс HelioPy!",
        "tagline": "Анализ солнечной активности и космической погоды.",
        "features_title": "Возможности:",
        "feature_1": "Загрузка и обработка данных солнечных миссий",
        "feature_2": "Анализ солнечных вспышек и корональных выбросов массы",
        "feature_3": "Прогнозирование космической погоды",
        "feature_4": "Визуализация и интерактивные графики",
        "nav_analysis": "Анализ",
        "nav_visualization": "Визуализация",
        "nav_api_docs": "API и документация",
        "nav_about": "О проекте",
        "lang_en": "English",
        "lang_ru": "Русский",
        "index_title": "Главная",
        "analysis_title": "Анализ солнечных данных",
        "analysis_desc": "Выполняйте базовые операции анализа через API.",
        "flare_peak_flux": "Пиковый поток (W/m²)",
        "btn_classify": "Классифицировать",
        "carrington_rotation": "Вращение Кэррингтона",
        "time_utc": "Время (UTC)",
        "btn_compute": "Вычислить",
        "coords_convert": "Преобразование координат",
        "r": "r",
        "theta": "theta (рад)",
        "phi": "phi (рад)",
        "btn_convert": "Преобразовать",
        "back_home": "← На главную",
        "visualization_title": "Визуализация",
        "visualization_desc": "Интерактивные графики, карты и анимации событий.",
        "api_docs_title": "API и документация",
        "api_docs_desc": "Описание доступных API и ссылки на документацию.",
        "api_info": "/api/info — Информация о библиотеке",
        "api_data": "/api/data — Получение данных (пример)",
        "docs_link": "Документация HelioPy",
        "about_title": "О проекте HelioPy",
        "about_desc": "HelioPy — библиотека для анализа солнечной активности и космической погоды.",
    },
}


def get_locale() -> str:
    lang = request.args.get("lang")
    if lang in TRANSLATIONS:
        session["lang"] = lang
        return lang
    return session.get("lang", "ru")


@app.context_processor
def inject_translations():
    lang = get_locale()
    return {"t": TRANSLATIONS.get(lang, TRANSLATIONS["en"]), "lang_code": lang}


@app.route("/set-lang/<lang>")
def set_lang(lang: str):
    if lang in TRANSLATIONS:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))


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


# ---------- Дополнительные API для демонстрации ----------
@app.route("/api/flare/classify")
def api_flare_classify():
    """Классифицировать вспышку по пиковому потоку (W/m^2).

    Query params:
      flux: float (например 1e-6)
    """
    try:
        flux_str = request.args.get("flux")
        if flux_str is None:
            return jsonify({"error": "missing 'flux' query param"}), 400
        flux = float(flux_str)
        detector = FlareDetector()
        classification = detector._classify_flare(flux)
        if classification is None:
            classification = "below-A"
        return jsonify({"flux": flux, "class": classification})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/time/carrington")
def api_time_carrington():
    """Вычислить номер вращения Кэррингтона для заданного времени.

    Query params:
      time: str в формате 'YYYY-MM-DD HH:MM:SS' или ISO
    """
    try:
        t_str = request.args.get("time")
        if not t_str:
            return jsonify({"error": "missing 'time' query param"}), 400
        t = TimeUtils.parse_time(t_str)
        cr = TimeUtils.carrington_rotation(t)
        return jsonify({"time": t_str, "carrington_rotation": cr})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/coords/convert", methods=["POST"])
def api_coords_convert():
    """Преобразование сферических координат в декартовы.

    JSON body: {"r": float, "theta": float, "phi": float}
    Углы в радианах.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        r = float(data.get("r"))
        theta = float(data.get("theta"))
        phi = float(data.get("phi"))
        x, y, z = MathUtils.spherical_to_cartesian(r, theta, phi)
        return jsonify({"x": x, "y": y, "z": z})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":  # Локальный запуск
    main(debug=True)
