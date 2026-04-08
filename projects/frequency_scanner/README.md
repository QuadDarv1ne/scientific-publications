# Frequency Scanner

**Сканер радиочастот и анализатор спектра на RTL-SDR**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

## Описание

Сканер радиоэфира для обнаружения активных частот и анализа спектра с использованием RTL-SDR.

## Требования

```bash
sudo apt-get install rtl-sdr sox hackrf
```

## Использование

```bash
# Сканирование диапазона
python src/scanner.py --range 88 108

# Анализ конкретной частоты
python src/scanner.py --freq 145.800 --duration 30

# Спектральный анализ
python src/scanner.py --spectrum --range 100 500
```

## Возможности

- Сканирование заданного диапазона частот
- Обнаружение активных станций
- Запись и анализ сигналов
- Экспорт результатов
