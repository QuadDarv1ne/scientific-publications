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

from src.iss_orbital_analysis import ISSTracker, analyze_pass_frequency
from src.iss_environment_analysis import ISSEnvironmentAnalyzer
from src.utils import print_header, print_section
from src.sstv_receiver import SSTVReceiver


def run_sstv_receiver():
    """Запуск SSTV приёмника для приёма изображений с МКС"""
    print_section("SSTV ПРИЁМНИК")
    
    try:
        from src.sstv_receiver import SSTVReceiver
        import time
        
        receiver = SSTVReceiver()
        
        # Проверка оборудования
        print("📡 Проверка RTL-SDR...")
        
        if not receiver.check_rtl_sdr():
            print("❌ RTL-SDR не найден!")
            print("   Для работы SSTV приёмника требуется:")
            print("   1. RTL-SDR донгл (V4 рекомендуется)")
            print("   2. sudo apt-get install rtl-sdr sox")
            return
            
        missing = receiver.check_dependencies()
        if missing:
            print(f"⚠️ Отсутствуют зависимости: {', '.join(missing)}")
            print("   Установите: sudo apt-get install rtl-sdr-utils sox rx-sstv")
            return
            
        print("✅ RTL-SDR готов к работе")
        print("\n" + "-" * 50)
        print("📺 Информация о SSTV на МКС:")
        print("   Частота: 145.800 MHz FM")
        print("   Время передачи: 60-120 секунд")
        print("   Лучшее время: во время пролёта над вами")
        print("-" * 50)
        
        # Получение информации о пролётах
        print("\n🌍 Получение информации о пролётах МКС...")
        lat = float(input("Введите широту (например, 55.7558 для Москвы): ").strip() or "55.7558")
        lon = float(input("Введите долготу (например, 37.6173 для Москвы): ").strip() or "37.6173")
        
        passes_info = receiver.get_iss_passes(lat, lon)
        if passes_info['status'] == 'success' and passes_info.get('passes'):
            print("\n📅 Ближайшие пролёты:")
            for i, p in enumerate(passes_info['passes'][:3], 1):
                print(f"   {i}. {p['risetime'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"      Продолжительность: {p['duration']} сек, Высота: {p['altitude']}°")
        else:
            print("⚠️ Не удалось получить данные о пролётах")
        
        # Запуск приёма
        print("\n" + "-" * 50)
        duration = int(input("Длительность приёма (сек, по умолчанию 180): ").strip() or "180"))
        print(f"🚀 Запуск приёма на {duration} секунд...")
        
        result = receiver.receive_sstv(duration=duration)
        
        if result:
            print(f"\n✅ Запись сохранена: {result}")
            print("   Для декодирования изображения установите RX-SSTV:")
            print("   sudo apt-get install rx-sstv")
            print("   Или используйте онлайн-декодер")
        else:
            print("\n❌ Приём не удался")
            print("   Возможные причины:")
            print("   - МКС не передавала SSTV в это время")
            print("   - Слабый сигнал")
            print("   - Помехи")
            
    except KeyboardInterrupt:
        print("\n⚠️ Приём прерван пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def show_menu():
    """Отображение главного меню"""
    print_header("ISS TELEMETRY ANALYZER")
    print("\nВыберите режим анализа:")
    print("1. 🛰️  Орбитальная телеметрия")
    print("2. 🌡️  Условия окружающей среды")
    print("3. 📊 Комплексный анализ")
    print("4. 🧪 Запуск тестов")
    print("5. 📖 Методология исследования")
    print("6. 📈 Расширенный орбитальный анализ")
    print("7. 🔍 Расширенный анализ условий среды")
    print("8. 📻 SSTV приём (RTL-SDR)")
    print("9. 📡 Мониторинг частот")
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
        tracker.collect_positions(duration_minutes=1, interval_seconds=5)
        
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


def run_advanced_orbital_analysis():
    """Запуск расширенного орбитального анализа"""
    print_section("РАСШИРЕННЫЙ ОРБИТАЛЬНЫЙ АНАЛИЗ")
    
    try:
        tracker = ISSTracker()
        
        # Получение TLE данных
        print("📡 Получение TLE данных...")
        tle_data = tracker.get_tle_data()
        if tle_data:
            print(f"✅ Получены данные: {tle_data['name']}")
        else:
            print("⚠️  Не удалось получить TLE данные")
        
        # Анализ тренда высоты орбиты
        print("\n📈 Анализ тренда изменения высоты орбиты...")
        trend_data = tracker.analyze_altitude_trend(show=False)
        if trend_data:
            print(f"📉 Тренд изменения высоты: {trend_data['trend_slope_m_per_day']:.1f} м/день")
            print(f"📊 Средняя высота орбиты: {trend_data['average_altitude']:.1f} км")
        
        # Анализ частоты пролетов (для Москвы)
        print("\n📊 Анализ частоты пролетов МКС над Москвой...")
        frequency_data = analyze_pass_frequency(55.7558, 37.6173, days=7)
        if frequency_data:
            print(f"📈 Среднее количество пролетов в день: {frequency_data['avg_passes_per_day']:.1f}")
            print(f"🔢 Общее количество пролетов за 7 дней: {frequency_data['total_passes']}")
        
        # 3D визуализация орбиты
        print("\n🌍 Создание 3D визуализации орбиты...")
        tracker.plot_3d_orbit(show=False)
        
        print("✅ Расширенный орбитальный анализ завершен")
        
    except Exception as e:
        print(f"❌ Ошибка в расширенном орбитальном анализе: {e}")


def run_advanced_environment_analysis():
    """Запуск расширенного анализа условий окружающей среды"""
    print_section("РАСШИРЕННЫЙ АНАЛИЗ УСЛОВИЙ СРЕДЫ")
    
    try:
        analyzer = ISSEnvironmentAnalyzer()
        
        # Получение TLE данных
        print("📡 Получение TLE данных...")
        tle_data = analyzer.get_tle_data()
        if tle_data:
            print(f"✅ Получены данные: {tle_data['name']}")
        else:
            print("⚠️  Не удалось получить TLE данные")
        
        # Расширенный анализ радиации
        print("\n🔍 Расширенный анализ радиационного фона...")
        peak_analysis = analyzer.analyze_radiation_peaks(days=30)
        if peak_analysis:
            print(f"🔺 Обнаружено пиков радиации: {peak_analysis['total_peaks']}")
            print(f"📊 Средняя интенсивность пиков: {peak_analysis['avg_peak']:.1f} мкЗв/ч")
            print(f"📈 Частота пиков: {peak_analysis['peak_frequency_per_day']:.1f} пиков/день")
        
        # Создание комплексных графиков
        print("\n📊 Создание расширенных графиков условий среды...")
        analyzer.plot_environmental_conditions(duration_hours=24, show=False)
        
        # Анализ радиационного воздействия
        print("\n☢️  Подробный анализ радиационного воздействия...")
        total_dose = analyzer.analyze_radiation_exposure(days=90, show=False)
        print(f"📈 Накопленная доза за 90 дней: {total_dose:.2f} мЗв")
        
        # Генерация отчета
        print("\n📋 Генерация расширенного телеметрического отчета...")
        analyzer.generate_telemetry_report()
        
        print("✅ Расширенный анализ условий среды завершен")
        
    except Exception as e:
        print(f"❌ Ошибка в расширенном анализе условий среды: {e}")


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


def run_sstv_receiver():
    """Запуск SSTV приёмника для МКС"""
    print_section("SSTV ПРИЁМНИК (RTL-SDR)")
    
    try:
        receiver = SSTVReceiver()
        
        # Проверка оборудования
        print("📡 Проверка RTL-SDR...")
        
        if not receiver.check_rtl_sdr():
            print("❌ RTL-SDR не найден!")
            print("\nДля работы SSTV приёмника требуется:")
            print("  1. RTL-SDR dongle")
            print("  2. Установить: sudo apt-get install rtl-sdr sox")
            print("  3. Создать blacklist для встроенных карт:")
            print("     echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/rtl-sdr.conf")
            return
            
        missing = receiver.check_dependencies()
        if missing:
            print(f"⚠️ Отсутствуют: {', '.join(missing)}")
            print("   Установите: sudo apt-get install rtl-sdr-utils sox")
            
        print("✓ RTL-SDR готов")
        print(f"\n📻 Частота МКС SSTV: {receiver.ISS_SSTV_FREQ} MHz")
        print("📻 Частота МКС APRS: {receiver.ISS_APRS_FREQ} MHz")
        
        # Выбор режима
        print("\nВыберите режим:")
        print("1. Одиночный приём (2 минуты)")
        print("2. Длительный приём (5 минут)")
        print("3. Мониторинг пролётов МКС")
        print("4. Показать последние изображения")
        
        choice = input("Выбор: ").strip()
        
        if choice == '1':
            print("\n🎬 Запись SSTV сигнала (120 сек)...")
            result = receiver.receive_sstv(duration=120)
            if result:
                print(f"✅ Записано: {result}")
            else:
                print("❌ Запись не удалась")
                
        elif choice == '2':
            print("\n🎬 Запись SSTV сигнала (300 сек)...")
            result = receiver.receive_sstv(duration=300)
            if result:
                print(f"✅ Записано: {result}")
            else:
                print("❌ Запись не удалась")
                
        elif choice == '3':
            print("\n🔄 Запуск мониторинга пролётов...")
            print("   (Для остановки нажмите Ctrl+C)")
            receiver.is_receiving = True
            receiver.start_monitoring(interval=300)
            
            # Ожидаем прерывания
            try:
                import time
                while receiver.is_receiving:
                    time.sleep(1)
            except KeyboardInterrupt:
                receiver.stop()
                print("\n✅ Мониторинг остановлен")
                
        elif choice == '4':
            images = receiver.get_recent_images(limit=5)
            if images:
                print("\n📷 Последние принятые изображения:")
                for i, img in enumerate(images, 1):
                    print(f"  {i}. {img}")
            else:
                print("📷 Изображений пока нет")
        else:
            print("❌ Неверный выбор")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def run_frequency_monitor():
    """Мониторинг радиочастот"""
    print_section("МОНИТОРИНГ ЧАСТОТ")
    
    try:
        receiver = SSTVReceiver()
        
        if not receiver.check_rtl_sdr():
            print("❌ RTL-SDR не найден!")
            return
            
        print("📡 Доступные частоты для мониторинга:")
        print("-" * 40)
        print("  МКС SSTV:      145.800 MHz FM")
        print("  МКС APRS:      145.825 MHz")
        print("  NOAA:          137.100-137.500 MHz (APT)")
        print("  Meteor M2:     137.100 MHz (LRPT)")
        print("  ADS-B:         1090 MHz")
        print("  ACARS:         131.550 MHz")
        print("  APRS:          144.800 MHz")
        print("-" * 40)
        
        print("\nДля мониторинга используйте:")
        print("  rtl_fm -f 145800000 -s 48000 - | play -r 48000 -t raw -e signed -b 16 -")
        print("\nИли запустите Gqrx для визуального мониторинга:")
        print("  gqrx")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


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
            elif choice == '6':
                run_advanced_orbital_analysis()
            elif choice == '7':
                run_advanced_environment_analysis()
            elif choice == '8':
                run_sstv_receiver()
            elif choice == '9':
                run_frequency_monitor()
            elif choice == '0':
                print("\n👋 До свидания! Спасибо за использование ISS Telemetry Analyzer!")
                break
            else:
                print("❌ Неверный выбор. Пожалуйста, введите число от 0 до 9.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"❌ Непредвиденная ошибка: {e}")
        
        # Пауза перед следующим меню
        try:
            input("\nНажмите Enter для продолжения...")
        except EOFError:
            # Handle case when input is not available (e.g., in automated testing)
            pass


if __name__ == "__main__":
    main()