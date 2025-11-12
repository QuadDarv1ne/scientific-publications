HelioPy Documentation
=====================

**HelioPy** — open-source библиотека для анализа солнечной активности и прогнозирования космической погоды.

.. image:: https://img.shields.io/github/actions/workflow/status/QuadDarv1ne/scientific-publications/ci.yml?branch=main
   :alt: CI Status
   :target: https://github.com/QuadDarv1ne/scientific-publications/actions

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :alt: Python Version
   :target: https://www.python.org/downloads/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :alt: Code Style
   :target: https://github.com/psf/black

Введение
--------

HelioPy предоставляет инструменты для:

* Загрузки и обработки гелиофизических данных
* Обнаружения солнечных событий (вспышки, CME)
* Анализа магнитных полей
* Прогнозирования космической погоды
* Визуализации солнечных данных

Быстрый старт
-------------

Установка::

   pip install -e .

Простой пример::

   from heliopy.utils import time_utils
   from datetime import datetime
   
   # Конвертация времени
   dt = datetime(2023, 10, 15, 12, 0, 0)
   jd = time_utils.to_julian_date(dt)
   print(f"Julian Date: {jd}")

Содержание
----------

.. toctree::
   :maxdepth: 2
   :caption: Руководство пользователя

   installation
   quickstart
   examples
   helioviewer

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/data_sources
   api/events
   api/imaging
   api/magnetic_fields
   api/models
   api/space_weather
   api/utils
   api/visualization

.. toctree::
   :maxdepth: 1
   :caption: Разработка

   contributing
   changelog

Индексы и таблицы
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
