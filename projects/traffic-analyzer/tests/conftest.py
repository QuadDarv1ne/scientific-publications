"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_bbox():
    """Пример bounding box [x1, y1, x2, y2]"""
    return [100.0, 100.0, 200.0, 200.0]


@pytest.fixture
def sample_polygons():
    """Пример полигонов дорог"""
    return {
        "1": [50, 50, 250, 50, 250, 250, 50, 250],
        "2": [300, 300, 500, 300, 500, 500, 300, 500]
    }


@pytest.fixture
def temp_video_path(tmp_path):
    """Создает путь для временного видеофайла"""
    return tmp_path / "test_video.mp4"


def pytest_configure(config):
    """Регистрация пользовательских маркеров"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
