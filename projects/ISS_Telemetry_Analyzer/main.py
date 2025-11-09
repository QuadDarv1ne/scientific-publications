#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS Telemetry Analyzer - Main Entry Point
Точка входа в анализатор телеметрии МКС
"""

import sys
import os
from pathlib import Path

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.iss_orbital_analysis import ISSTracker
from src.iss_environment_analysis import ISSEnvironmentAnalyzer
from src.utils import print_header, print_section


def show_menu():
    """Отображение главного меню"""
    print_header("ISS TELEMETRY ANALYZER")
    print("\nВыберите режим анализа:")
    print("1. 🛰️  Орбитальная телеметрия")
    print("2. 🌡️  Условия окружающей среды")
    print("3. 📊 Комплексный анализ")
    print("4. 🧪 Запуск тестов")
    print("5. 📖 Методология исследования")
    print("0. ❌ Выход")
    print("-" * 50)


def run_orbital_analysis():
    """Запуск анализа орбитальной телеметрии"""
    print_section("ОРБИТАЛЬНАЯ ТЕЛЕМЕТРИЯ")
    
    try:
        tracker = ISSTracker()
        
        # Получение текущего положения МКС
        print("📡 Получение текущего положения МКС...")
        position = tracker.get_current_position()
        if position:
            print(f"📍 Широта: {position['latitude']:.4f}°")
            print(f"📍 Долгота: {position['longitude']:.4f}°")
            print(f"⏰ Время: {position['timestamp']}")
        else:
            print("❌ Не удалось получить текущее положение")
        
        # Сбор траектории
        print("\n📊 Сбор траектории МКС (30 секунд)...")
        tracker.collect_positions(duration_minutes=0.5, interval_seconds=5)
        
        # Расчет параметров
        print("\n🧮 Расчет орбитальных параметров...")
        params = tracker.calculate_orbital_parameters()
        if params:
            print(f"📏 Высота орбиты: {params['altitude_km']:.1f} км")
            print(f"🚀 Скорость: {params['avg_speed_kmh']:.0f} км/ч")
            print(f"⏱️  Период обращения: {params['orbital_period_min']:.1f} минут")
        
        # Визуализация
        print("\n🖼️  Создание визуализаций...")
        tracker.plot_ground_track(show=False)
        print("✅ Орбитальный анализ завершен")
        
    except Exception as e:
        print(f"❌ Ошибка в орбитальном анализе: {e}")


def run_environment_analysis():
    """Запуск анализа условий окружающей среды"""
    print_section("УСЛОВИЯ ОКРУЖАЮЩЕЙ СРЕДЫ")
    
    try:
        analyzer = ISSEnvironmentAnalyzer()
        
        # Получение TLE данных
        print("📡 Получение TLE данных...")
        tle_data = analyzer.get_tle_data()
        if tle_data:
            print(f"✅ Получены данные: {tle_data['name']}")
        else:
            print("⚠️  Не удалось получить TLE данные")
        
        # Анализ условий
        print("\n📊 Создание графиков условий среды...")
        analyzer.plot_environmental_conditions(duration_hours=12, show=False)
        
        # Анализ радиации
        print("\n☢️  Анализ радиационного воздействия...")
        total_dose = analyzer.analyze_radiation_exposure(days=30, show=False)
        print(f"📈 Накопленная доза за 30 дней: {total_dose:.2f} мЗв")
        
        # Генерация отчета
        print("\n📋 Генерация комплексного отчета...")
        analyzer.generate_telemetry_report()
        
        print("✅ Анализ условий среды завершен")
        
    except Exception as e:
        print(f"❌ Ошибка в анализе условий среды: {e}")


def run_comprehensive_analysis():
    """Запуск комплексного анализа"""
    print_section("КОМПЛЕКСНЫЙ АНАЛИЗ")
    
    try:
        print("🛰️  Запуск орбитального анализа...")
        run_orbital_analysis()
        
        print("\n🌡️  Запуск анализа условий среды...")
        run_environment_analysis()
        
        print("\n" + "="*60)
        print("✅ КОМПЛЕКСНЫЙ АНАЛИЗ ЗАВЕРШЕН!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Ошибка в комплексном анализе: {e}")


def run_tests():
    """Запуск тестов"""
    print_section("ЗАПУСК ТЕСТОВ")
    
    try:
        # Импорт и запуск тестов
        sys.path.insert(0, str(Path(__file__).parent / 'tests'))
        
        # Запуск тестов орбитального модуля
        from tests.test_orbital import run_tests as run_orbital_tests
        print("🧪 Запуск тестов орбитального модуля...")
        success = run_orbital_tests()
        
        if success:
            print("✅ Все тесты пройдены успешно")
        else:
            print("❌ Некоторые тесты не пройдены")
            
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")


def show_methodology():
    """Отображение методологии исследования"""
    print_section("МЕТОДОЛОГИЯ ИССЛЕДОВАНИЯ")
    
    try:
        methodology_path = Path(__file__).parent / 'docs' / 'methodology.md'
        if methodology_path.exists():
            with open(methodology_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[:2000])  # Показываем первые 2000 символов
                if len(content) > 2000:
                    print("\n... (полный текст в файле docs/methodology.md)")
        else:
            print("❌ Файл методологии не найден")
    except Exception as e:
        print(f"❌ Ошибка при чтении методологии: {e}")


def main():
    """Главная функция приложения"""
    while True:
        show_menu()
        
        try:
            choice = input("Введите номер режима: ").strip()
            
            if choice == '1':
                run_orbital_analysis()
            elif choice == '2':
                run_environment_analysis()
            elif choice == '3':
                run_comprehensive_analysis()
            elif choice == '4':
                run_tests()
            elif choice == '5':
                show_methodology()
            elif choice == '0':
                print("\n👋 До свидания! Спасибо за использование ISS Telemetry Analyzer!")
                break
            else:
                print("❌ Неверный выбор. Пожалуйста, введите число от 0 до 5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"❌ Непредвиденная ошибка: {e}")
        
        # Пауза перед следующим меню
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()