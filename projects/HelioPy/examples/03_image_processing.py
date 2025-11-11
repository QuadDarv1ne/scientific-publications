"""
Пример 3: Обработка изображений
=================================

Этот пример демонстрирует:
- Создание объекта SolarImage
- Нормализацию изображений
- Базовую обработку
"""

import numpy as np
from datetime import datetime

from heliopy.imaging.image_processor import SolarImage, ImageProcessor
from heliopy.core.data_processor import DataProcessor


def create_test_solar_image():
    """Создание тестового солнечного изображения."""
    # Создаем синтетическое изображение Солнца
    size = 512
    center = size // 2

    # Создаем координатную сетку
    y, x = np.ogrid[-center:size - center, -center:size - center]
    r = np.sqrt(x**2 + y**2)

    # Солнечный диск с лимбовым затемнением
    solar_radius = 200
    disk = (r <= solar_radius).astype(float)
    limb_darkening = 1.0 - 0.4 * (r / solar_radius) ** 2
    image_data = disk * limb_darkening

    # Добавляем активные области (горячие точки)
    active_regions = [
        (center + 50, center + 30, 20),  # (y, x, размер)
        (center - 70, center - 40, 15),
        (center + 20, center - 80, 25),
    ]

    for y_pos, x_pos, ar_size in active_regions:
        y_grid, x_grid = np.ogrid[-ar_size : ar_size + 1, -ar_size : ar_size + 1]
        r_ar = np.sqrt(x_grid**2 + y_grid**2)
        ar_mask = r_ar <= ar_size
        ar_brightness = (1.0 - r_ar / ar_size) * ar_mask

        # Добавляем активную область к изображению
        y_start = max(0, y_pos - ar_size)
        y_end = min(size, y_pos + ar_size + 1)
        x_start = max(0, x_pos - ar_size)
        x_end = min(size, x_pos + ar_size + 1)

        ar_y_start = ar_size - (y_pos - y_start)
        ar_y_end = ar_y_start + (y_end - y_start)
        ar_x_start = ar_size - (x_pos - x_start)
        ar_x_end = ar_x_start + (x_end - x_start)

        image_data[y_start:y_end, x_start:x_end] += (
            0.5 * ar_brightness[ar_y_start:ar_y_end, ar_x_start:ar_x_end]
        )

    # Добавляем шум
    noise = np.random.normal(0, 0.02, (size, size))
    image_data = np.clip(image_data + noise, 0, 2)

    # Создаем метаданные
    header = {
        "TELESCOP": "SDO/AIA",
        "INSTRUME": "AIA",
        "WAVELNTH": 193,
        "DATE-OBS": "2023-10-15T12:00:00",
        "EXPTIME": 2.0,
    }

    return SolarImage(
        data=image_data,
        header=header,
        time=datetime(2023, 10, 15, 12, 0, 0),
        wavelength=193,
        instrument="AIA",
        observatory="SDO",
    )


def main():
    print("🌞 HelioPy - Обработка солнечных изображений\n")

    # 1. Создание тестового изображения
    print("1. Создание тестового изображения")
    print("-" * 50)
    solar_image = create_test_solar_image()
    print(f"Инструмент: {solar_image.instrument}")
    print(f"Обсерватория: {solar_image.observatory}")
    print(f"Длина волны: {solar_image.wavelength} Å")
    print(f"Время: {solar_image.time}")
    print(f"Размер: {solar_image.data.shape}")
    print(f"Диапазон значений: {solar_image.data.min():.4f} - {solar_image.data.max():.4f}\n")

    # 2. Нормализация данных
    print("2. Нормализация изображения")
    print("-" * 50)
    processor = DataProcessor()

    # Нормализация minmax
    normalized_minmax = processor.normalize(solar_image.data, method="minmax")
    print(f"MinMax нормализация:")
    print(f"  Мин: {normalized_minmax.min():.4f}")
    print(f"  Макс: {normalized_minmax.max():.4f}")

    # Нормализация zscore
    normalized_zscore = processor.normalize(solar_image.data, method="zscore")
    print(f"\nZ-score нормализация:")
    print(f"  Среднее: {normalized_zscore.mean():.4e}")
    print(f"  Ст. отклонение: {normalized_zscore.std():.4f}\n")

    # 3. Базовая статистика изображения
    print("3. Статистика изображения")
    print("-" * 50)
    data = solar_image.data

    # Только солнечный диск (убираем фон)
    threshold = 0.1
    disk_mask = data > threshold
    disk_data = data[disk_mask]

    print(f"Пикселей на диске: {disk_mask.sum()}")
    print(f"Средняя яркость диска: {disk_data.mean():.4f}")
    print(f"Медианная яркость: {np.median(disk_data):.4f}")
    print(f"Ст. отклонение: {disk_data.std():.4f}")
    print(f"Мин яркость: {disk_data.min():.4f}")
    print(f"Макс яркость: {disk_data.max():.4f}\n")

    # 4. Поиск ярких областей
    print("4. Обнаружение активных областей")
    print("-" * 50)

    # Находим яркие пиксели (> 90-й перцентиль)
    bright_threshold = np.percentile(disk_data, 90)
    bright_mask = (data > bright_threshold) & disk_mask
    bright_pixels = bright_mask.sum()

    print(f"Порог яркости: {bright_threshold:.4f}")
    print(f"Ярких пикселей: {bright_pixels}")
    print(f"Процент от диска: {100 * bright_pixels / disk_mask.sum():.2f}%")

    print("\n✅ Обработка завершена успешно!")
    print("\n💡 Совет: В реальных сценариях вы можете загрузить изображения")
    print("   используя SDOLoader или другие загрузчики данных.")


if __name__ == "__main__":
    main()
