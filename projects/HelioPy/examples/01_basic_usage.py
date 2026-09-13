"""
Пример 1: Базовое использование HelioPy
========================================

Этот пример демонстрирует базовые возможности библиотеки:
- Загрузка конфигурации
- Работа с временными данными
- Математические утилиты
"""

from datetime import timedelta

import numpy as np

from heliopy.utils.math_utils import MathUtils
from heliopy.utils.stats_utils import StatsUtils
from heliopy.utils.time_utils import TimeUtils


def main():
    print("🌞 HelioPy - Пример базового использования\n")

    # 1. Работа со временем
    print("1. Работа со временем")
    print("-" * 50)

    # Парсинг времени
    time_str = "2023-10-15 12:00:00"
    time = TimeUtils.parse_time(time_str)
    print(f"Время: {time}")

    # Вычисление номера вращения Кэррингтона
    cr_number = TimeUtils.carrington_rotation(time)
    print(f"Номер вращения Кэррингтона: {cr_number:.2f}")

    # Конвертация в юлианскую дату
    jd = TimeUtils.to_julian_date(time)
    print(f"Юлианская дата: {jd:.2f}\n")

    # 2. Математические утилиты
    print("2. Математические преобразования")
    print("-" * 50)

    # Преобразование координат
    r, theta, phi = 1.0, np.pi / 4, np.pi / 6
    x, y, z = MathUtils.spherical_to_cartesian(r, theta, phi)
    print(f"Сферические ({r}, {theta:.4f}, {phi:.4f}) →")
    print(f"Декартовы ({x:.4f}, {y:.4f}, {z:.4f})")

    # Обратное преобразование
    r2, theta2, phi2 = MathUtils.cartesian_to_spherical(x, y, z)
    print(f"Декартовы ({x:.4f}, {y:.4f}, {z:.4f}) →")
    print(f"Сферические ({r2:.4f}, {theta2:.4f}, {phi2:.4f})\n")

    # 3. Статистические утилиты
    print("3. Статистический анализ")
    print("-" * 50)

    # Генерация тестовых данных с выбросами
    np.random.seed(42)
    data = np.concatenate([np.random.normal(100, 10, 100), [200, 250, 300]])
    print(f"Размер данных: {len(data)}")

    # Робастные статистики
    stats = StatsUtils.robust_statistics(data)
    print(f"Медиана: {stats['median']:.2f}")
    print(f"MAD: {stats['mad']:.2f}")
    print(f"IQR: {stats['iqr']:.2f}")

    # Удаление выбросов
    cleaned = StatsUtils.remove_outliers(data, method="iqr")
    print(f"Размер после удаления выбросов: {len(cleaned)}\n")

    # 4. Генерация временного ряда
    print("4. Временной ряд")
    print("-" * 50)

    start = "2023-10-15 00:00:00"
    end = "2023-10-15 06:00:00"
    step = timedelta(hours=1)

    times = TimeUtils.time_range(start, end, step)
    print(f"Создано {len(times)} временных точек:")
    for i, t in enumerate(times):
        dt = TimeUtils.to_datetime(t)
        print(f"  {i + 1}. {dt.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n✅ Пример завершен успешно!")


if __name__ == "__main__":
    main()
