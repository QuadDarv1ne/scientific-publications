"""
Пример 2: Анализ солнечных вспышек
===================================

Этот пример демонстрирует:
- Создание тестовых данных GOES
- Обнаружение солнечных вспышек
- Классификацию вспышек
"""

from datetime import datetime, timedelta

import numpy as np

from heliopy.events.flare_detector import FlareDetector, GOESData


def generate_test_goes_data():
    """Генерация тестовых данных GOES с симулированными вспышками."""
    # Временной ряд
    start_time = datetime(2023, 10, 15, 0, 0, 0)
    times = [start_time + timedelta(minutes=i) for i in range(1440)]  # 1 день

    # Фоновый поток
    background = np.random.normal(1e-7, 1e-8, len(times))

    # Добавляем несколько вспышек
    fluxes = background.copy()

    # Вспышка класса C в 06:00
    flare1_start = 360  # 6 часов
    flare1_peak = flare1_start + 10
    flare1_end = flare1_start + 30
    for i in range(flare1_start, flare1_end):
        t = (i - flare1_start) / (flare1_peak - flare1_start)
        if i < flare1_peak:
            fluxes[i] += 5e-6 * t
        else:
            t = (flare1_end - i) / (flare1_end - flare1_peak)
            fluxes[i] += 5e-6 * t

    # Вспышка класса M в 12:00
    flare2_start = 720  # 12 часов
    flare2_peak = flare2_start + 15
    flare2_end = flare2_start + 40
    for i in range(flare2_start, flare2_end):
        t = (i - flare2_start) / (flare2_peak - flare2_start)
        if i < flare2_peak:
            fluxes[i] += 3e-5 * t
        else:
            t = (flare2_end - i) / (flare2_end - flare2_peak)
            fluxes[i] += 3e-5 * t

    # Конвертируем в Time объекты
    from astropy.time import Time

    time_array = Time([t.isoformat() for t in times])

    return GOESData(
        time=time_array,
        xrsa=fluxes,  # 0.5-4 Å канал
        xrsb=fluxes * 1.5,  # 1-8 Å канал
        satellite="GOES-16",
    )


def main():
    print("🌞 HelioPy - Анализ солнечных вспышек\n")

    # 1. Генерация тестовых данных
    print("1. Генерация тестовых данных GOES")
    print("-" * 50)
    goes_data = generate_test_goes_data()
    print(f"Период: {goes_data.time[0]} - {goes_data.time[-1]}")
    print(f"Спутник: {goes_data.satellite}")
    print(f"Точек данных: {len(goes_data.time)}\n")

    # 2. Обнаружение вспышек
    print("2. Обнаружение солнечных вспышек")
    print("-" * 50)
    detector = FlareDetector()
    flares = detector.detect_flares(goes_data)
    print(f"Обнаружено вспышек: {len(flares)}\n")

    # 3. Детали вспышек
    print("3. Детали обнаруженных вспышек")
    print("-" * 50)
    for i, flare in enumerate(flares, 1):
        print(f"Вспышка #{i}:")
        print(f"  Класс: {flare.class_}")
        print(f"  Время начала: {flare.start_time}")
        print(f"  Время пика: {flare.peak_time}")
        print(f"  Время окончания: {flare.end_time}")
        print(f"  Пиковый поток: {flare.peak_flux:.2e} Вт/м²")

        duration = (flare.end_time - flare.start_time).sec / 60
        print(f"  Длительность: {duration:.1f} минут")
        print()

    # 4. Классификация вспышки
    print("4. Примеры классификации")
    print("-" * 50)
    test_fluxes = [1e-7, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4]
    for flux in test_fluxes:
        flare_class = detector._classify_flare(flux)
        print(f"Поток {flux:.2e} Вт/м² → Класс {flare_class}")

    print("\n✅ Анализ завершен успешно!")


if __name__ == "__main__":
    main()
