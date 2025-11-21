"""
Unit tests for FPS Counter functionality
"""

import pytest
from unittest.mock import patch
from utils_local.utils import FPS_Counter


class TestFPSCounterEdgeCases:
    """Дополнительные тесты для граничных случаев FPS_Counter"""
    
    def test_single_frame_returns_zero(self):
        """Один кадр должен возвращать 0 FPS"""
        counter = FPS_Counter(calc_time_perion_N_frames=10)
        
        fps = counter.calc_FPS()
        
        assert fps == 0.0
        assert len(counter.time_buffer) == 1
    
    @patch('utils_local.utils.time.time')
    def test_high_fps_calculation(self, mock_time):
        """Проверка расчета при высоком FPS"""
        counter = FPS_Counter(calc_time_perion_N_frames=5)
        
        # Симулируем 60 FPS: 5 кадров за ~0.0833 сек
        timestamps = [i * (1/60) for i in range(5)]
        mock_time.side_effect = timestamps
        
        for _ in range(5):
            fps = counter.calc_FPS()
        
        # Ожидаем примерно 60 FPS
        assert fps == pytest.approx(60.0, rel=0.1)
    
    @patch('utils_local.utils.time.time')
    def test_low_fps_calculation(self, mock_time):
        """Проверка расчета при низком FPS"""
        counter = FPS_Counter(calc_time_perion_N_frames=3)
        
        # Симулируем 5 FPS: 3 кадра за 0.6 сек
        timestamps = [i * 0.2 for i in range(3)]
        mock_time.side_effect = timestamps
        
        for _ in range(3):
            fps = counter.calc_FPS()
        
        # Ожидаем примерно 5 FPS
        assert fps == pytest.approx(5.0, rel=0.1)
    
    def test_buffer_size_parameter(self):
        """Проверка различных размеров буфера"""
        for buffer_size in [1, 5, 10, 30, 100]:
            counter = FPS_Counter(calc_time_perion_N_frames=buffer_size)
            
            for _ in range(buffer_size + 10):
                counter.calc_FPS()
            
            assert len(counter.time_buffer) == buffer_size
