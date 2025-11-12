"""
Пример 5: Работа с данными Parker Solar Probe
============================================

Этот пример демонстрирует:
- Загрузку данных SWEAP (Solar Wind Electrons Alphas and Protons)
- Загрузку данных FIELDS (магнитное и электрическое поле)
- Анализ in-situ данных солнечного ветра
"""

import matplotlib.pyplot as plt
import numpy as np

from heliopy import load_psp_sweap, load_psp_fld


def main():
    print(" Parker Solar Probe - Анализ данных\n")

    # Инициализация переменных данных
    spc_data = None
    mag_data = None

    # 1. Загрузка данных SWEAP
    print("1. Загрузка данных SWEAP")
    print("-" * 50)
    
    try:
        date = "2023-10-15"
        
        # Загрузка данных Solar Probe Cup (плазма солнечного ветра)
        print(f"Загрузка SWEAP/SPC данных для {date}...")
        spc_data = load_psp_sweap(date, data_type="spc")
        print(f"  Загружено точек: {len(spc_data)}")
        print(f"  Колонки: {list(spc_data.columns)}")
        print(f"  Плотность: {spc_data['density'].mean():.2f} ± {spc_data['density'].std():.2f} частиц/см³")
        print(f"  Скорость: {spc_data['velocity'].mean():.2f} ± {spc_data['velocity'].std():.2f} км/с")
        print(f"  Температура: {spc_data['temperature'].mean()/1e6:.2f} ± {spc_data['temperature'].std()/1e6:.2f} MK")
        print()
        
        # Загрузка данных Solar Probe Electrons
        print(f"Загрузка SWEAP/SPE данных для {date}...")
        spe_data = load_psp_sweap(date, data_type="spe")
        print(f"  Загружено точек: {len(spe_data)}")
        print(f"  Колонки: {list(spe_data.columns)}")
        print()
        
    except Exception as e:
        print(f"Ошибка при загрузке данных SWEAP: {e}\n")

    # 2. Загрузка данных FIELDS
    print("2. Загрузка данных FIELDS")
    print("-" * 50)
    
    try:
        date = "2023-10-15"
        
        # Загрузка магнитного поля
        print(f"Загрузка FIELDS/mag_rtn данных для {date}...")
        mag_data = load_psp_fld(date, data_type="mag_rtn")
        print(f"  Загружено точек: {len(mag_data)}")
        print(f"  Колонки: {list(mag_data.columns)}")
        print(f"  |B|: {mag_data['Btot'].mean():.2f} ± {mag_data['Btot'].std():.2f} нТл")
        print(f"  Br: {mag_data['Br'].mean():.2f} ± {mag_data['Br'].std():.2f} нТл")
        print(f"  Bt: {mag_data['Bt'].mean():.2f} ± {mag_data['Bt'].std():.2f} нТл")
        print(f"  Bn: {mag_data['Bn'].mean():.2f} ± {mag_data['Bn'].std():.2f} нТл")
        print()
        
    except Exception as e:
        print(f"Ошибка при загрузке данных FIELDS: {e}\n")

    # 3. Визуализация данных
    print("3. Визуализация данных")
    print("-" * 50)
    
    try:
        # Проверяем, что данные были успешно загружены
        if spc_data is None or mag_data is None:
            print("Невозможно создать графики: данные не были загружены")
        else:
            # Создание графиков для демонстрации
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle("Данные Parker Solar Probe", fontsize=16)
            
            # График плотности солнечного ветра
            axes[0, 0].plot(spc_data['time'], spc_data['density'])
            axes[0, 0].set_title("Плотность солнечного ветра")
            axes[0, 0].set_ylabel("Плотность (частиц/см³)")
            axes[0, 0].grid(True)
            
            # График скорости солнечного ветра
            axes[0, 1].plot(spc_data['time'], spc_data['velocity'])
            axes[0, 1].set_title("Скорость солнечного ветра")
            axes[0, 1].set_ylabel("Скорость (км/с)")
            axes[0, 1].grid(True)
            
            # График магнитного поля
            axes[1, 0].plot(mag_data['time'], mag_data['Btot'])
            axes[1, 0].set_title("Магнитное поле")
            axes[1, 0].set_ylabel("|B| (нТл)")
            axes[1, 0].set_xlabel("Время")
            axes[1, 0].grid(True)
            
            # График температуры
            axes[1, 1].plot(spc_data['time'], spc_data['temperature']/1e6)
            axes[1, 1].set_title("Температура солнечного ветра")
            axes[1, 1].set_ylabel("Температура (MK)")
            axes[1, 1].set_xlabel("Время")
            axes[1, 1].grid(True)
            
            plt.tight_layout()
            plt.savefig("psp_data_example.png", dpi=150, bbox_inches='tight')
            print("Графики сохранены в 'psp_data_example.png'")
        print()
        
    except Exception as e:
        print(f"Ошибка при создании графиков: {e}\n")

    print("✅ Пример завершен успешно!")


if __name__ == "__main__":
    main()