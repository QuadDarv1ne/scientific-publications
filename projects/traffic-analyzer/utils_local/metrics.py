"""
Модуль для сбора и отправки метрик производительности системы.
Отслеживает FPS, задержки обработки, размеры очередей и другие метрики.
"""

from dataclasses import dataclass, asdict
from time import time
from typing import Dict, Any, Optional
import json


@dataclass
class PerformanceMetrics:
    """Класс для хранения метрик производительности."""
    
    camera_id: int
    timestamp: float
    
    # FPS метрики
    current_fps: float = 0.0
    avg_fps: float = 0.0
    
    # Задержки обработки (в миллисекундах)
    detection_latency_ms: float = 0.0
    tracking_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    
    # Метрики очередей
    queue_detection_size: int = 0
    queue_tracking_size: int = 0
    queue_max_size: int = 50
    
    # Метрики детекции
    objects_detected: int = 0
    active_tracks: int = 0
    
    # Использование ресурсов
    memory_usage_mb: Optional[float] = None
    gpu_usage_percent: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует метрики в словарь."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Преобразует метрики в JSON строку."""
        return json.dumps(self.to_dict())
    
    def to_influx_format(self) -> str:
        """
        Преобразует метрики в формат InfluxDB Line Protocol.
        
        Returns:
            str: Строка в формате InfluxDB Line Protocol
        """
        tags = f"camera_id={self.camera_id}"
        
        fields = [
            f"current_fps={self.current_fps}",
            f"avg_fps={self.avg_fps}",
            f"detection_latency_ms={self.detection_latency_ms}",
            f"tracking_latency_ms={self.tracking_latency_ms}",
            f"total_latency_ms={self.total_latency_ms}",
            f"queue_detection_size={self.queue_detection_size}",
            f"queue_tracking_size={self.queue_tracking_size}",
            f"objects_detected={self.objects_detected}",
            f"active_tracks={self.active_tracks}",
        ]
        
        if self.memory_usage_mb is not None:
            fields.append(f"memory_usage_mb={self.memory_usage_mb}")
        
        if self.gpu_usage_percent is not None:
            fields.append(f"gpu_usage_percent={self.gpu_usage_percent}")
        
        fields_str = ",".join(fields)
        timestamp_ns = int(self.timestamp * 1_000_000_000)
        
        return f"performance_metrics,{tags} {fields_str} {timestamp_ns}"


class MetricsCollector:
    """Сборщик метрик производительности."""
    
    def __init__(self, camera_id: int, window_size: int = 30):
        """
        Инициализация сборщика метрик.
        
        Args:
            camera_id: ID камеры
            window_size: Размер окна для расчета средних значений
        """
        self.camera_id = camera_id
        self.window_size = window_size
        
        self._fps_history = []
        self._detection_latency_history = []
        self._tracking_latency_history = []
        
        self._last_frame_time = time()
        self._frame_count = 0
    
    def update_fps(self) -> float:
        """
        Обновляет и возвращает текущий FPS.
        
        Returns:
            float: Текущий FPS
        """
        current_time = time()
        elapsed = current_time - self._last_frame_time
        
        if elapsed > 0:
            fps = 1.0 / elapsed
            self._fps_history.append(fps)
            
            # Ограничиваем размер истории
            if len(self._fps_history) > self.window_size:
                self._fps_history.pop(0)
        else:
            fps = 0.0
        
        self._last_frame_time = current_time
        self._frame_count += 1
        
        return fps
    
    def get_average_fps(self) -> float:
        """
        Возвращает средний FPS за окно наблюдения.
        
        Returns:
            float: Средний FPS
        """
        if not self._fps_history:
            return 0.0
        return sum(self._fps_history) / len(self._fps_history)
    
    def record_detection_latency(self, latency_ms: float):
        """
        Записывает задержку детекции.
        
        Args:
            latency_ms: Задержка в миллисекундах
        """
        self._detection_latency_history.append(latency_ms)
        if len(self._detection_latency_history) > self.window_size:
            self._detection_latency_history.pop(0)
    
    def record_tracking_latency(self, latency_ms: float):
        """
        Записывает задержку трекинга.
        
        Args:
            latency_ms: Задержка в миллисекундах
        """
        self._tracking_latency_history.append(latency_ms)
        if len(self._tracking_latency_history) > self.window_size:
            self._tracking_latency_history.pop(0)
    
    def get_average_detection_latency(self) -> float:
        """Возвращает среднюю задержку детекции."""
        if not self._detection_latency_history:
            return 0.0
        return sum(self._detection_latency_history) / len(self._detection_latency_history)
    
    def get_average_tracking_latency(self) -> float:
        """Возвращает среднюю задержку трекинга."""
        if not self._tracking_latency_history:
            return 0.0
        return sum(self._tracking_latency_history) / len(self._tracking_latency_history)
    
    def create_metrics(
        self,
        queue_detection_size: int = 0,
        queue_tracking_size: int = 0,
        objects_detected: int = 0,
        active_tracks: int = 0,
        detection_latency_ms: Optional[float] = None,
        tracking_latency_ms: Optional[float] = None
    ) -> PerformanceMetrics:
        """
        Создает объект метрик с текущими значениями.
        
        Args:
            queue_detection_size: Размер очереди детекции
            queue_tracking_size: Размер очереди трекинга
            objects_detected: Количество обнаруженных объектов
            active_tracks: Количество активных треков
            detection_latency_ms: Задержка детекции (опционально)
            tracking_latency_ms: Задержка трекинга (опционально)
        
        Returns:
            PerformanceMetrics: Объект с метриками
        """
        current_fps = self.update_fps()
        avg_fps = self.get_average_fps()
        
        if detection_latency_ms is not None:
            self.record_detection_latency(detection_latency_ms)
        
        if tracking_latency_ms is not None:
            self.record_tracking_latency(tracking_latency_ms)
        
        avg_detection = self.get_average_detection_latency()
        avg_tracking = self.get_average_tracking_latency()
        
        return PerformanceMetrics(
            camera_id=self.camera_id,
            timestamp=time(),
            current_fps=current_fps,
            avg_fps=avg_fps,
            detection_latency_ms=detection_latency_ms or avg_detection,
            tracking_latency_ms=tracking_latency_ms or avg_tracking,
            total_latency_ms=(detection_latency_ms or avg_detection) + (tracking_latency_ms or avg_tracking),
            queue_detection_size=queue_detection_size,
            queue_tracking_size=queue_tracking_size,
            objects_detected=objects_detected,
            active_tracks=active_tracks
        )
