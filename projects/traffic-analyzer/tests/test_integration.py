"""
Integration tests for main processing pipeline
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Эти тесты требуют наличия реальных зависимостей
pytest.importorskip("ultralytics")
pytest.importorskip("cv2")


@pytest.mark.integration
class TestMainPipeline:
    """Интеграционные тесты для главного пайплайна обработки"""
    
    @pytest.fixture
    def mock_config(self):
        """Создание моковой конфигурации"""
        return {
            "pipeline": {
                "save_video": False,
                "show_in_web": False,
                "send_info_kafka": False
            },
            "video_reader": {
                "src": "test_videos/test_video.mp4",
                "skip_secs": 0,
                "roads_info": "configs/entry_exit_lanes.json"
            },
            "detection_node": {
                "weight_pth": "weights/yolov8m.pt",
                "classes_to_detect": [2, 3, 5, 7],
                "confidence": 0.1,
                "iou": 0.7,
                "imgsz": 640
            },
            "tracking_node": {
                "first_track_thresh": 0.5,
                "second_track_thresh": 0.1,
                "match_thresh": 0.95,
                "track_buffer": 125
            },
            "show_node": {
                "scale": 0.6,
                "imshow": False,
                "fps_counter_N_frames_stat": 15,
                "draw_fps_info": True,
                "show_roi": True,
                "overlay_transparent_mask": False,
                "show_only_yolo_detections": False,
                "show_track_id_different_colors": False,
                "show_info_statistics": False
            },
            "general": {
                "colors_of_roads": {
                    1: [102, 204, 255],
                    2: [0, 0, 170],
                    3: [17, 70, 10],
                    4: [120, 56, 126]
                },
                "buffer_analytics": 0.5,
                "min_time_life_track": 3,
                "count_cars_buffer_frames": 25
            }
        }
    
    def test_config_validation_success(self, mock_config):
        """Проверка успешной валидации конфигурации"""
        from main_optimized import validate_config
        from omegaconf import DictConfig
        
        config = DictConfig(mock_config)
        
        # Не должно вызвать исключение
        validate_config(config)
    
    def test_config_validation_fails_on_missing_section(self):
        """Проверка провала валидации при отсутствии секции"""
        from main_optimized import validate_config
        from omegaconf import DictConfig
        
        incomplete_config = DictConfig({"pipeline": {}})
        
        with pytest.raises(ValueError, match="Отсутствует обязательная секция"):
            validate_config(incomplete_config)
    
    @pytest.mark.slow
    def test_config_validation_fails_on_missing_weights(self, mock_config):
        """Проверка провала валидации при отсутствии файла весов"""
        from main_optimized import validate_config
        from omegaconf import DictConfig
        
        mock_config["detection_node"]["weight_pth"] = "nonexistent/weights.pt"
        config = DictConfig(mock_config)
        
        with pytest.raises(ValueError, match="Файл весов модели не найден"):
            validate_config(config)


@pytest.mark.integration
class TestEnvironmentVariables:
    """Тесты для проверки переменных окружения"""
    
    def test_default_env_values_set_correctly(self, monkeypatch):
        """Проверка корректной установки значений по умолчанию"""
        from main_optimized import DEFAULT_ENV_VALUES
        from utils_local.utils import check_and_set_env_var
        
        # Очищаем переменные окружения
        for var in DEFAULT_ENV_VALUES.keys():
            monkeypatch.delenv(var, raising=False)
        
        # Устанавливаем значения
        for var, value in DEFAULT_ENV_VALUES.items():
            check_and_set_env_var(var, value)
        
        # Проверяем
        import os
        assert os.environ["VIDEO_SRC"] == "test_videos/test_video.mp4"
        assert os.environ["ROADS_JSON"] == "configs/entry_exit_lanes.json"
        assert os.environ["TOPIC_NAME"] == "statistics_1"
        assert os.environ["CAMERA_ID"] == "1"
