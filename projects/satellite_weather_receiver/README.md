# Satellite Weather Image Receiver

**Приём изображений с NOAA и Meteor M2 спутников**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Описание

Программный комплекс для приёма и декодирования изображений с метеорологических спутников:

- **NOAA** (15, 18, 19) - APT формат
- **Meteor M2** - LRPT формат

## Требования

### Аппаратное обеспечение
- RTL-SDR V4 (или совместимый dongle)
- Антенна для 137 MHz (квадратная или V-диполь)

### Программное обеспечение (Linux)
```bash
sudo apt-get update
sudo apt-get install -y rtl-sdr sox predict gpsbabel
```

### Python зависимости
```bash
pip install -r requirements.txt
```

## Использование

### NOAA APT приём
```bash
python src/satellite_receiver.py --satellite noaa --duration 300
```

### Meteor M2 LRPT приём
```bash
python src/satellite_receiver.py --satellite meteor --duration 180
```

### Мониторинг пролётов
```bash
python src/satellite_receiver.py --monitor
```

## Частоты

| Спутник | Частота | Формат |
|---------|---------|--------|
| NOAA 15 | 137.6200 MHz | APT |
| NOAA 18 | 137.9125 MHz | APT |
| NOAA 19 | 137.1000 MHz | APT |
| Meteor M2 | 137.1000 MHz | LRPT |

## Структура проекта

```
satellite_weather_receiver/
├── src/
│   ├── satellite_receiver.py  # Основной модуль
│   ├── pass_predictor.py      # Предсказание пролётов
│   └── decoder.py             # Декодеры
├── data/                      # Временные файлы
├── images/                    # Принятые изображения
└── README.md
```
