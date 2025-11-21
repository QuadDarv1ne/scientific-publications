"""
Unit tests for utility functions in utils_local/utils.py
"""

import os
import pytest
from unittest.mock import Mock, patch
import numpy as np
from shapely.geometry import Point, Polygon as ShapelyPolygon

from utils_local.utils import (
    check_and_set_env_var,
    FPS_Counter,
    intersects_central_point
)


class TestCheckAndSetEnvVar:
    """Тесты для функции check_and_set_env_var"""
    
    def test_sets_env_var_when_not_exists(self, monkeypatch):
        """Проверка установки переменной окружения, если она не существует"""
        monkeypatch.delenv("TEST_VAR", raising=False)
        
        check_and_set_env_var("TEST_VAR", "test_value")
        
        assert os.environ["TEST_VAR"] == "test_value"
    
    def test_does_not_override_existing_env_var(self, monkeypatch):
        """Проверка, что существующая переменная не перезаписывается"""
        monkeypatch.setenv("TEST_VAR", "existing_value")
        
        check_and_set_env_var("TEST_VAR", "new_value")
        
        assert os.environ["TEST_VAR"] == "existing_value"
    
    def test_converts_int_to_string(self, monkeypatch):
        """Проверка конвертации числового значения в строку"""
        monkeypatch.delenv("TEST_INT", raising=False)
        
        check_and_set_env_var("TEST_INT", 42)
        
        assert os.environ["TEST_INT"] == "42"


class TestFPSCounter:
    """Тесты для класса FPS_Counter"""
    
    def test_initialization(self):
        """Проверка инициализации счетчика"""
        counter = FPS_Counter(calc_time_perion_N_frames=10)
        
        assert counter.time_buffer == []
        assert counter.calc_time_perion_N_frames == 10
    
    def test_returns_zero_when_buffer_not_full(self):
        """Возвращает 0 когда буфер еще не заполнен"""
        counter = FPS_Counter(calc_time_perion_N_frames=5)
        
        fps = counter.calc_FPS()
        
        assert fps == 0.0
        assert len(counter.time_buffer) == 1
    
    @patch('utils_local.utils.time.time')
    def test_calculates_fps_when_buffer_full(self, mock_time):
        """Проверка расчета FPS когда буфер заполнен"""
        counter = FPS_Counter(calc_time_perion_N_frames=3)
        
        # Симулируем временные метки: 0, 0.1, 0.2, 0.3 секунды
        mock_time.side_effect = [0.0, 0.1, 0.2, 0.3]
        
        counter.calc_FPS()  # t=0.0, buffer=[0.0]
        counter.calc_FPS()  # t=0.1, buffer=[0.0, 0.1]
        fps = counter.calc_FPS()  # t=0.2, buffer=[0.0, 0.1, 0.2]
        
        # FPS = 3 frames / (0.2 - 0.0) = 15.0
        assert fps == pytest.approx(15.0, rel=0.01)
    
    @patch('utils_local.utils.time.time')
    def test_maintains_buffer_size(self, mock_time):
        """Проверка, что размер буфера не превышает заданный"""
        counter = FPS_Counter(calc_time_perion_N_frames=3)
        
        mock_time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4]
        
        for _ in range(5):
            counter.calc_FPS()
        
        assert len(counter.time_buffer) == 3


class TestIntersectsCentralPoint:
    """Тесты для функции intersects_central_point"""
    
    def test_point_inside_polygon_returns_road_id(self):
        """Проверка: точка внутри полигона возвращает ID дороги"""
        bbox = [100.0, 100.0, 200.0, 200.0]  # центр в (150, 150)
        polygons = {
            "1": [50, 50, 250, 50, 250, 250, 50, 250]  # квадрат 50-250
        }
        
        result = intersects_central_point(bbox, polygons)
        
        assert result == 1
    
    def test_point_outside_all_polygons_returns_none(self):
        """Проверка: точка вне всех полигонов возвращает None"""
        bbox = [500.0, 500.0, 600.0, 600.0]  # центр в (550, 550)
        polygons = {
            "1": [50, 50, 250, 50, 250, 250, 50, 250]  # квадрат 50-250
        }
        
        result = intersects_central_point(bbox, polygons)
        
        assert result is None
    
    def test_finds_correct_polygon_among_multiple(self):
        """Проверка: находит правильный полигон среди нескольких"""
        bbox = [300.0, 300.0, 400.0, 400.0]  # центр в (350, 350)
        polygons = {
            "1": [50, 50, 250, 50, 250, 250, 50, 250],    # квадрат 50-250
            "2": [280, 280, 450, 280, 450, 450, 280, 450] # квадрат 280-450
        }
        
        result = intersects_central_point(bbox, polygons)
        
        assert result == 2
    
    def test_handles_edge_case_on_polygon_boundary(self):
        """Проверка граничного случая: точка на границе полигона"""
        bbox = [200.0, 200.0, 300.0, 300.0]  # центр в (250, 250) - на границе
        polygons = {
            "1": [50, 50, 250, 50, 250, 250, 50, 250]
        }
        
        result = intersects_central_point(bbox, polygons)
        
        # На границе - может быть как внутри, так и снаружи в зависимости от реализации
        assert result in [None, 1]
