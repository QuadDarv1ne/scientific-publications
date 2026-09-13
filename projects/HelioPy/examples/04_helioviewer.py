"""
Пример 4: Работа с данными Helioviewer
=====================================

Этот пример демонстрирует:
- Загрузку изображений с Helioviewer
- Получение списка доступных источников данных
- Работу с различными длинами волн
"""


def main():
    print("🌞 HelioPy - Работа с данными Helioviewer\n")

    # 1. Получение списка доступных источников данных
    print("1. Доступные источники данных Helioviewer")
    print("-" * 50)

    try:
        # Для демонстрации создадим структуру данных, которая будет возвращаться
        # В реальной реализации это будет вызов load_helioviewer.get_data_sources()
        data_sources = {
            "SDO": {
                "AIA": {
                    "193Å": {"source_id": 14},
                    "171Å": {"source_id": 13},
                    "211Å": {"source_id": 15},
                    "304Å": {"source_id": 16},
                    "1600Å": {"source_id": 17},
                    "1700Å": {"source_id": 18},
                    "4500Å": {"source_id": 19},
                }
            },
            "SOHO": {
                "EIT": {
                    "171Å": {"source_id": 6},
                    "195Å": {"source_id": 7},
                    "284Å": {"source_id": 8},
                    "304Å": {"source_id": 9},
                }
            },
        }

        print("Доступные источники:")
        for observatory, instruments in data_sources.items():
            print(f"  {observatory}:")
            for instrument, wavelengths in instruments.items():
                print(f"    {instrument}:")
                for wavelength, info in wavelengths.items():
                    print(f"      {wavelength} (ID: {info['source_id']})")
        print()

    except Exception as e:
        print(f"Ошибка при получении источников данных: {e}\n")

    # 2. Загрузка изображения с Helioviewer
    print("2. Загрузка изображения с Helioviewer")
    print("-" * 50)

    try:
        # Загрузка данных Helioviewer для определенной даты
        date = "2023-10-15T12:00:00"
        source_id = 14  # SDO/AIA 193Å

        print(f"Загрузка изображения Helioviewer для {date} (ID: {source_id})...")
        # В реальной реализации это будет:
        # helio_data = load_helioviewer(date, source_id)

        # Для демонстрации создадим фиктивные данные
        helio_data = type(
            "SolarImage",
            (),
            {
                "shape": (4096, 4096),
                "instrument": "AIA",
                "observatory": "SDO",
                "wavelength": 193.0,
                "time": type("Time", (), {"iso": date})(),
            },
        )()

        print("Данные загружены успешно!")
        print(f"  Форма изображения: {helio_data.shape}")
        print(f"  Инструмент: {helio_data.instrument}")
        print(f"  Обсерватория: {helio_data.observatory}")
        print(f"  Длина волны: {helio_data.wavelength} Å")
        print(f"  Время наблюдения: {helio_data.time.iso}")
        print()

    except Exception as e:
        print(f"Ошибка при загрузке данных Helioviewer: {e}\n")

    # 3. Загрузка изображений с разных источников
    print("3. Загрузка изображений с разных источников")
    print("-" * 50)

    date = "2023-10-15T12:00:00"  # Определяем переменную заранее
    sources = [
        {"name": "SDO/AIA 171Å", "id": 13},
        {"name": "SDO/AIA 211Å", "id": 15},
        {"name": "SDO/AIA 304Å", "id": 16},
    ]

    for source in sources:
        try:
            print(f"Загрузка {source['name']} (ID: {source['id']})...")
            # В реальной реализации это будет:
            # data = load_helioviewer(date, source['id'])

            # Для демонстрации создадим фиктивные данные
            data = type(
                "SolarImage",
                (),
                {
                    "shape": (4096, 4096),
                    "instrument": "AIA",
                    "observatory": "SDO",
                    "wavelength": float(source["name"].split()[-1].replace("Å", "")),
                    "time": type("Time", (), {"iso": date})(),
                },
            )()

            print(f"  ✓ Успешно загружено: {data.shape}")
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")

    print("\n✅ Пример завершен успешно!")


if __name__ == "__main__":
    main()
