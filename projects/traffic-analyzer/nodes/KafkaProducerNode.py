from kafka import KafkaProducer
from json import dumps
import time
import logging

from utils_local.utils import profile_time
from utils_local.metrics import MetricsCollector
from elements.VideoEndBreakElement import VideoEndBreakElement
from elements.FrameElement import FrameElement


class KafkaProducerNode:
    """
    Узел для отправки статистики и метрик производительности в Kafka.
    Отправляет данные о трафике и системные метрики в отдельные топики.
    """
    
    def __init__(self, config) -> None:
        """
        Инициализация Kafka Producer.
        
        Args:
            config: Конфигурация приложения
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        config_kafka = config["kafka_producer_node"]
        bootstrap_servers = config_kafka["bootstrap_servers"]
        self.topic_name = config_kafka["topic_name"]
        self.how_often_sec = config_kafka["how_often_sec"]
        self.camera_id = config_kafka["camera_id"]
        self.last_send_time = None
        
        # Топик для метрик производительности
        self.metrics_topic = f"metrics_{self.camera_id}"
        
        # Инициализация сборщика метрик
        self.metrics_collector = MetricsCollector(camera_id=self.camera_id)
        
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda x: dumps(x).encode("utf-8"),
            )
            self.logger.info(f"Kafka Producer инициализирован. Topics: {self.topic_name}, {self.metrics_topic}")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации Kafka Producer: {e}")
            raise

        self.buffer_analytics_sec = (
            config["general"]["buffer_analytics"] * 60 + config["general"]["min_time_life_track"]
        )  # столько по времени буфер набирается и информацию о статистеке выводить рано

    @profile_time
    def process(self, frame_element: FrameElement):
        """
        Обработка кадра и отправка данных в Kafka.
        
        Args:
            frame_element: Элемент кадра с данными
        
        Returns:
            FrameElement: Обработанный элемент кадра
        """
        # Выйти из обработки если это пришел VideoEndBreakElement а не FrameElement
        if isinstance(frame_element, VideoEndBreakElement):
            return frame_element

        current_time = time.time()
        timestamp = frame_element.timestamp

        if frame_element.frame_num == 1:
            self.last_send_time = current_time

        if current_time - self.last_send_time > self.how_often_sec or frame_element.frame_num == 1:
            # Отправка статистики трафика
            traffic_data = {
                f"camera_id": f"id_{self.camera_id}",
                f"cars": frame_element.info["cars_amount"],
                f"road_1": (
                    frame_element.info["roads_activity"][1]
                    if timestamp >= self.buffer_analytics_sec
                    else None
                ),
                f"road_2": (
                    frame_element.info["roads_activity"][2]
                    if timestamp >= self.buffer_analytics_sec
                    else None
                ),
                f"road_3": (
                    frame_element.info["roads_activity"][3]
                    if timestamp >= self.buffer_analytics_sec
                    else None
                ),
                f"road_4": (
                    frame_element.info["roads_activity"][4]
                    if timestamp >= self.buffer_analytics_sec
                    else None
                ),
                f"road_5": (
                    frame_element.info["roads_activity"][5]
                    if timestamp >= self.buffer_analytics_sec
                    else None
                ),
            }
            
            try:
                self.kafka_producer.send(self.topic_name, value=traffic_data).get(timeout=1)
                self.logger.debug(f"Отправлена статистика трафика в топик {self.topic_name}")
            except Exception as e:
                self.logger.error(f"Ошибка отправки статистики трафика: {e}")
            
            # Сбор и отправка метрик производительности
            try:
                # Получаем количество активных треков
                active_tracks = len(frame_element.info.get("active_tracks_id", []))
                
                # Создаем объект метрик
                metrics = self.metrics_collector.create_metrics(
                    queue_detection_size=getattr(frame_element, 'queue_detection_size', 0),
                    queue_tracking_size=getattr(frame_element, 'queue_tracking_size', 0),
                    objects_detected=len(frame_element.info.get("tracks", [])),
                    active_tracks=active_tracks
                )
                
                # Отправка метрик в Kafka
                metrics_data = metrics.to_dict()
                self.kafka_producer.send(self.metrics_topic, value=metrics_data).get(timeout=1)
                self.logger.debug(f"Отправлены метрики производительности в топик {self.metrics_topic}")
                
            except Exception as e:
                self.logger.error(f"Ошибка при отправке метрик производительности: {e}")
            
            self.last_send_time = current_time
            frame_element.send_to_kafka = True

        return frame_element
