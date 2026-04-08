# ADS-B Receiver

**Мониторинг воздушного движения через RTL-SDR**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Описание

Приём и декодирование данных ADS-B (Automatic Dependent Surveillance-Broadcast) с самолётов с использованием RTL-SDR dongle.

## Требования

### Аппаратное обеспечение
- RTL-SDR V4 (или совместимый dongle)
- Антенна для 1090 MHz

### Программное обеспечение (Linux)
```bash
sudo apt-get update
sudo apt-get install -y rtl-sdr dump1090-mutability librtlsdr-dev
```

## Использование

### Запуск приёмника
```bash
python src/adsb_receiver.py
```

### Опции
```bash
python src/adsb_receiver.py --help
```

## Частота

**ADS-B:** 1090 MHz

## Структура проекта

```
adsb_receiver/
├── src/
│   ├── adsb_receiver.py   # Основной модуль
│   └── ...
├── data/                  # Данные
├── results/               # Результаты
└── README.md
```
