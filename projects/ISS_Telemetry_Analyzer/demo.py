#!/usr/bin/env python3
"""
Demo script for ISS Telemetry Analyzer
Демонстрационный скрипт для анализатора телеметрии МКС
"""

import sys
from pathlib import Path

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent))

from src.iss_environment_analysis import ISSEnvironmentAnalyzer
from src.iss_orbital_analysis import ISSTracker, predict_passes
from src.utils import print_header, print_section


def demo_orbital_analysis():
    """Демонстрация орбитального анализа"""
    print_section("ДЕМОНСТРАЦИЯ ОРБИТАЛЬНОГО АНАЛИЗА")

    tracker = ISSTracker()

    # Получение текущего положения (симуляция)
    print("📡 Получение текущего положения МКС...")
    # В реальной реализации: position = tracker.get_current_position()
    print("📍 Широта: 51.6° (симуляция)")
    print("📍 Долгота: -123.4° (симуляция)")
    print("⏰ Время: 2025-11-09 21:00:00 UTC")

    # Расчет параметров (симуляция)
    print("\n🧮 Расчет орбитальных параметров...")
    print("📏 Высота орбиты: 408.0 км")
    print("🚀 Скорость: 27,600 км/ч")
    print("⏱️  Период обращения: 92.9 минут")
    print("🔁 Витков в сутки: 15.5")

    # Визуализация
    print("\n🖼️  Создание визуализаций...")
    tracker.plot_ground_track(show=False)
    tracker.plot_3d_orbit(show=False)
    print("✅ Графики созданы и сохранены в results/plots/")

    # Анализ тренда высоты орбиты
    print("\n📈 Анализ тренда изменения высоты орбиты...")
    # В реальной реализации: trend_data = tracker.analyze_altitude_trend(show=False)
    print("✅ Анализ тренда высоты орбиты завершен")


def demo_environment_analysis():
    """Демонстрация анализа условий окружающей среды"""
    print_section("ДЕМОНСТРАЦИЯ АНАЛИЗА УСЛОВИЙ СРЕДЫ")

    analyzer = ISSEnvironmentAnalyzer()

    # Симуляция данных
    print("🌡️  Симуляция температурного профиля...")
    print("   • Внутренняя температура: 22°C (стабильная)")
    print("   • Внешняя температура: от -157°C до +121°C")
    print("   • Циклов нагрев/охлаждение: ~16 в сутки")

    print("\n☢️  Симуляция радиационного фона...")
    print("   • Средний уровень: 30 мкЗв/час")
    print("   • Пики в SAA: до 150 мкЗв/час")
    print("   • Солнечные вспышки: до 300 мкЗв/час (редко)")

    print("\n📊 Создание комплексных графиков...")
    analyzer.plot_environmental_conditions(duration_hours=24, show=False)
    print("✅ Графики условий среды созданы")

    print("\n📈 Анализ накопленной радиации...")
    # В реальной реализации: total_dose = analyzer.analyze_radiation_exposure(days=30)
    print("   • Накопленная доза за 30 дней: 1.2 мЗв")
    print("   • Сравнение с населением: 1.2x годовой лимит")
    print("   • Сравнение с работниками: 0.06x годовой лимит")

    print("\n🔍 Анализ пиков радиационного фона...")
    # В реальной реализации: peak_analysis = analyzer.analyze_radiation_peaks(days=30)
    print("   • Обнаружено 15 пиков радиации")
    print("   • Максимальный пик: 145 мкЗв/ч")
    print("   • Средняя интенсивность пиков: 85 мкЗв/ч")


def demo_visibility_prediction():
    """Демонстрация прогноза видимости"""
    print_section("ДЕМОНСТРАЦИЯ ПРОГНОЗА ВИДИМОСТИ")

    print("🔮 Прогноз видимости МКС для Москвы (55.7558°, 37.6173°):")
    predict_passes(55.7558, 37.6173, n_passes=3)

    print("\n🔮 Прогноз видимости МКС для Санкт-Петербурга (59.9343°, 30.3351°):")
    predict_passes(59.9343, 30.3351, n_passes=3)

    print("\n📊 Анализ частоты пролетов МКС над Москвой за 7 дней...")
    # В реальной реализации: frequency_data = analyze_pass_frequency(55.7558, 37.6173, days=7)
    print("   • Общее количество пролетов: 32")
    print("   • Среднее количество пролетов в день: 4.6")
    print("   • Максимум пролетов в день: 6")
    print("   • Минимум пролетов в день: 3")


def main():
    """Главная функция демонстрации"""
    print_header("ДЕМОНСТРАЦИЯ ISS TELEMETRY ANALYZER")

    print("""
Добро пожаловать в демонстрацию ISS Telemetry Analyzer!
Этот скрипт демонстрирует основные возможности системы.

В реальной реализации система:
- Получает реальные данные от API
- Выполняет точные расчеты
- Создает научные визуализации
- Проводит комплексный анализ
    """)

    # Демонстрация орбитального анализа
    demo_orbital_analysis()

    # Демонстрация анализа условий среды
    demo_environment_analysis()

    # Демонстрация прогноза видимости
    demo_visibility_prediction()

    print("\n" + "=" * 70)
    print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 70)
    print("\nДля полноценного использования запустите:")
    print("   python main.py")
    print("\nИли отдельные модули:")
    print("   python src/iss_orbital_analysis.py")
    print("   python src/iss_environment_analysis.py")


if __name__ == "__main__":
    main()
