# System Monitor

**Кроссплатформенный мониторинг системы с поддержкой GPU**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Возможности

- CPU мониторинг (общая загрузка и по ядрам)
- Оперативная память и swap
- Диски и файловые системы
- Сетевой трафик (скорость загрузки/выгрузки)
- GPU мониторинг (NVIDIA через nvidia-ml-py3)
- Топ процессов по CPU и памяти
- Логирование в файл
- Экспорт данных в JSON/CSV

## Установка

```bash
pip install psutil nvidia-ml-py3
```

## Использование

```bash
# Запуск мониторинга
python system_monitor.py

# С опциями
python system_monitor.py --interval 2 --gpu
python system_monitor.py --export json
python system_monitor.py --daemon
```

## Опции

- `--interval` - Интервал обновления (сек)
- `--gpu` - Включить мониторинг GPU
- `--export` - Экспорт (json/csv)
- `--daemon` - Работа в фоне
- `--log` - Путь к лог-файлу
