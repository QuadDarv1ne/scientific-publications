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
import json

def _load_translations() -> dict:
    translations = {}
    for code in ["en", "ru"]:
        path = BASE_DIR / "i18n" / f"{code}.json"
        try:
            with path.open("r", encoding="utf-8") as f:
                translations[code] = json.load(f)
        except Exception:
            translations[code] = {}
    return translations

TRANSLATIONS = _load_translations()

# Flask application (redefine after STATIC_DIR introduction if needed)
app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
if not app.secret_key:
    app.secret_key = "heliopy-dev-key"


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


@app.route("/api/plot/timeseries")
def api_plot_timeseries():
    """Синтетический временной ряд для демонстрации визуализации.

    Возвращает массив точек времени и поток (условные значения), а также
    локализованные подписи для осей и заголовок.
    """
    import math
    import time as _time
    lang = get_locale()
    tdict = TRANSLATIONS.get(lang, TRANSLATIONS.get("en", {}))
    # Генерация синтетических данных (sin+noise)
    n = 50
    base = _time.time()
    times = [base + i * 360 for i in range(n)]  # шаг 6 минут
    flux = [1e-6 + 5e-7 * math.sin(i / 5.0) + (1e-7 * math.sin(i / 2.0)) for i in range(n)]
    return jsonify({
        "times": times,
        "flux": flux,
        "labels": {
            "x": tdict.get("chart_time", "Time"),
            "y": tdict.get("chart_flux", "Flux"),
            "title": tdict.get("chart_title_demo", "Synthetic Solar Flux Time Series")
        }
    })


if __name__ == "__main__":  # Локальный запуск
    main(debug=True)
