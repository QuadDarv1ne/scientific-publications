"""
Базовые примеры использования HelioPy.

Этот скрипт демонстрирует основные возможности библиотеки.
"""

from heliopy import load_sdo_aia, load_goes
from heliopy.events import FlareDetector
from heliopy.imaging import ImageVisualizer
from heliopy.space_weather import forecast_geoeffectiveness


def example_load_sdo():
    """Пример загрузки данных SDO/AIA."""
    print("Пример 1: Загрузка данных SDO/AIA")
    print("-" * 50)
    
    try:
        # Загрузка данных SDO/AIA для определенной даты
        date = "2023-10-15"
        wavelength = 193  # Å
        
        print(f"Загрузка данных SDO/AIA {wavelength}Å для {date}...")
        sdo_data = load_sdo_aia(date, wavelength)
        
        print(f"Данные загружены успешно!")
        print(f"  Форма изображения: {sdo_data.shape}")
        print(f"  Инструмент: {sdo_data.instrument}")
        print(f"  Обсерватория: {sdo_data.observatory}")
        print(f"  Время наблюдения: {sdo_data.time.iso}")
        
        # Создание визуализации
        visualizer = ImageVisualizer()
        fig = visualizer.plot_solar_image(
            sdo_data,
            title=f"SDO/AIA {wavelength}Å - {date}",
            save_path="sdo_image.png"
        )
        print("Изображение сохранено в sdo_image.png")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        print("Примечание: Для работы этого примера требуется подключение к интернету")
        print("и установленная библиотека SunPy.")


def example_flare_detection():
    """Пример обнаружения солнечных вспышек."""
    print("\nПример 2: Обнаружение солнечных вспышек")
    print("-" * 50)
    
    try:
        # Загрузка данных GOES
        date = "2023-10-15"
        print(f"Загрузка данных GOES для {date}...")
        goes_data = load_goes(date)
        
        # Обнаружение вспышек
        detector = FlareDetector()
        flares = detector.detect_flares(goes_data)
        
        print(f"Обнаружено вспышек: {len(flares)}")
        for i, flare in enumerate(flares, 1):
            print(f"  Вспышка {i}:")
            print(f"    Класс: {flare.class_}")
            print(f"    Время начала: {flare.start_time.iso}")
            print(f"    Пик: {flare.peak_time.iso}")
            print(f"    Пиковый поток: {flare.peak_flux:.2e} W/m²")
        
        # Прогноз воздействия на Землю
        if flares:
            print("\nПрогноз воздействия на Землю:")
            impact_forecast = forecast_geoeffectiveness(flares[-1])
            print(f"  {impact_forecast.summary}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        print("Примечание: Для работы этого примера требуется подключение к интернету")


if __name__ == "__main__":
    print("=" * 50)
    print("Примеры использования HelioPy")
    print("=" * 50)
    
    # Запуск примеров
    example_load_sdo()
    example_flare_detection()
    
    print("\n" + "=" * 50)
    print("Примеры завершены!")

