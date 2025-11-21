from time import sleep, time
from multiprocessing import Process, Queue
import logging
import sys

import hydra
from tqdm import tqdm

from nodes.VideoReader import VideoReader
from nodes.ShowNode import ShowNode
from nodes.VideoSaverNode import VideoSaverNode
from nodes.DetectionTrackingNodes import DetectionTrackingNodes
from nodes.TrackerInfoUpdateNode import TrackerInfoUpdateNode
from nodes.CalcStatisticsNode import CalcStatisticsNode
from nodes.FlaskServerVideoNode import VideoServer
from nodes.KafkaProducerNode import KafkaProducerNode
from elements.VideoEndBreakElement import VideoEndBreakElement
from utils_local.utils import check_and_set_env_var
from utils_local.logger import get_process_logger

PRINT_PROFILE_INFO = False


def proc_frame_reader_and_detection(queue_out: Queue, config: dict, time_sleep_start: int):
    """
    Процесс чтения кадров из видео и детекции объектов.
    
    Args:
        queue_out: Очередь для передачи обработанных кадров
        config: Конфигурация приложения
        time_sleep_start: Время ожидания перед стартом (сек)
    """
    logger = get_process_logger("frame_reader_detection")
    
    try:
        sleep_message = f"Система разогревается.. sleep({time_sleep_start})"
        for _ in tqdm(range(time_sleep_start), desc=sleep_message):
            sleep(1)
        
        logger.info("Инициализация VideoReader и DetectionTrackingNodes")
        video_reader = VideoReader(config["video_reader"])
        detection_node = DetectionTrackingNodes(config)
        
        logger.info("Начало обработки видеопотока")
        for frame_element in video_reader.process():
            ts0 = time()
            frame_element = detection_node.process(frame_element)
            ts1 = time()
            
            try:
                queue_out.put(frame_element, timeout=5)
            except Exception as e:
                logger.error(f"Ошибка при добавлении в очередь: {e}")
                break
            
            if PRINT_PROFILE_INFO:
                print(
                    f"PROC_FRAME_READER_AND_DETECTION: {(time()-ts0) * 1000:.0f} ms: "
                    + f"detection_node {(ts1-ts0) * 1000:.0f} | "
                    + f"put {(time()-ts1) * 1000:.0f}"
                )
            
            if isinstance(frame_element, VideoEndBreakElement):
                logger.info("Получен сигнал завершения видео")
                break
    
    except Exception as e:
        logger.exception(f"Критическая ошибка в процессе чтения и детекции: {e}")
        raise
    finally:
        logger.info("Процесс frame_reader_detection завершен")


def proc_tracker_update_and_calc(queue_in: Queue, queue_out: Queue, config: dict):
    """
    Процесс обновления информации о треках и вычисления статистики.
    
    Args:
        queue_in: Очередь входящих кадров
        queue_out: Очередь исходящих обработанных кадров
        config: Конфигурация приложения
    """
    logger = get_process_logger("tracker_update_calc")
    
    try:
        logger.info("Инициализация TrackerInfoUpdateNode и CalcStatisticsNode")
        tracker_info_update_node = TrackerInfoUpdateNode(config)
        calc_statistics_node = CalcStatisticsNode(config)
        
        send_info_kafka = config["pipeline"]["send_info_kafka"]
        if send_info_kafka:
            logger.info("Инициализация KafkaProducerNode")
            kafka_producer_node = KafkaProducerNode(config)
        
        logger.info("Начало обработки треков и статистики")
        while True:
            ts0 = time()
            
            try:
                frame_element = queue_in.get(timeout=10)
            except Exception as e:
                logger.error(f"Ошибка при получении из очереди: {e}")
                break
            
            ts1 = time()
            
            try:
                frame_element = tracker_info_update_node.process(frame_element)
                frame_element = calc_statistics_node.process(frame_element)
                
                if send_info_kafka:
                    frame_element = kafka_producer_node.process(frame_element)
            except Exception as e:
                logger.error(f"Ошибка при обработке кадра: {e}")
                continue
            
            ts2 = time()
            
            try:
                queue_out.put(frame_element, timeout=5)
            except Exception as e:
                logger.error(f"Ошибка при добавлении в выходную очередь: {e}")
                break
            
            if PRINT_PROFILE_INFO:
                print(
                    f"PROC_TRACKER_UPDATE_AND_CALC: {(time()-ts0) * 1000:.0f} ms: "
                    + f"get {(ts1-ts0) * 1000:.0f} | "
                    + f"nodes_inference {(ts2-ts1) * 1000:.0f} | "
                    + f"put {(time()-ts2) * 1000:.0f}"
                )
            
            if isinstance(frame_element, VideoEndBreakElement):
                logger.info("Получен сигнал завершения видео")
                break
    
    except Exception as e:
        logger.exception(f"Критическая ошибка в процессе tracker_update_calc: {e}")
        raise
    finally:
        logger.info("Процесс tracker_update_calc завершен")


def proc_show_node(queue_in: Queue, config: dict):
    """
    Процесс отображения результатов обработки.
    
    Args:
        queue_in: Очередь входящих обработанных кадров
        config: Конфигурация приложения
    """
    logger = get_process_logger("show_node")
    
    try:
        logger.info("Инициализация ShowNode")
        show_node = ShowNode(config)
        
        save_video = config["pipeline"]["save_video"]
        show_in_web = config["pipeline"]["show_in_web"]
        
        if save_video:
            logger.info("Инициализация VideoSaverNode")
            video_saver_node = VideoSaverNode(config["video_saver_node"])
        
        if show_in_web:
            logger.info("Инициализация VideoServer")
            video_server_node = VideoServer(config)
        
        logger.info("Начало отображения результатов")
        while True:
            ts0 = time()
            
            try:
                frame_element = queue_in.get(timeout=10)
            except Exception as e:
                logger.error(f"Ошибка при получении из очереди: {e}")
                break
            
            ts1 = time()
            
            try:
                frame_element = show_node.process(frame_element)
                
                if save_video:
                    video_saver_node.process(frame_element)
                
                if show_in_web:
                    video_server_node.process(frame_element)
            except Exception as e:
                logger.error(f"Ошибка при обработке кадра для отображения: {e}")
                continue
            
            ts2 = time()
            
            if PRINT_PROFILE_INFO:
                print(
                    f"PROC_SHOW_NODE: {(time()-ts0) * 1000:.0f} ms: "
                    + f"get {(ts1-ts0) * 1000:.0f} | "
                    + f"show_node {(ts2-ts1) * 1000:.0f} | "
                    + f"put {(time()-ts2) * 1000:.0f}"
                )
            
            if isinstance(frame_element, VideoEndBreakElement):
                logger.info("Получен сигнал завершения видео")
                break
    
    except Exception as e:
        logger.exception(f"Критическая ошибка в процессе show_node: {e}")
        raise
    finally:
        logger.info("Процесс show_node завершен")


@hydra.main(version_base=None, config_path="configs", config_name="app_config")
def main(config) -> None:
    """
    Главная функция приложения для анализа трафика.
    Запускает параллельные процессы обработки видеопотока.
    
    Args:
        config: Конфигурация из Hydra
    """
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(handler)
    
    try:
        time_sleep_start = 5

        queue_frame_reader_and_detect_out = Queue(maxsize=50)
        queue_track_update_out = Queue(maxsize=50)

        processes = [
            Process(
                target=proc_frame_reader_and_detection,
                args=(queue_frame_reader_and_detect_out, config, time_sleep_start),
                name="proc_frame_reader_and_detection",
            ),
            Process(
                target=proc_tracker_update_and_calc,
                args=(queue_frame_reader_and_detect_out, queue_track_update_out, config),
                name="proc_tracker_update_and_calc",
            ),
            Process(
                target=proc_show_node,
                args=(queue_track_update_out, config),
                name="proc_show_node",
            ),
        ]

        logger.info(f"Запуск {len(processes)} процессов обработки")
        
        for p in processes:
            p.daemon = True
            p.start()
            logger.info(f"Процесс {p.name} запущен (PID: {p.pid})")

        # Ждем, пока последний процесс завершится
        processes[-1].join()
        
        logger.info("Основной процесс завершен успешно")
    
    except KeyboardInterrupt:
        logger.warning("Получен сигнал прерывания (Ctrl+C)")
        for p in processes:
            if p.is_alive():
                logger.info(f"Завершение процесса {p.name}")
                p.terminate()
                p.join(timeout=5)
    
    except Exception as e:
        logger.exception(f"Критическая ошибка в главном процессе: {e}")
        raise


if __name__ == "__main__":
    ts = time()

    # Проверяем и устанавливаем переменные окружения если их нет
    check_and_set_env_var("VIDEO_SRC", "test_videos/test_video.mp4")
    check_and_set_env_var("ROADS_JSON", "configs/entry_exit_lanes.json")
    check_and_set_env_var("TOPIC_NAME", "statistics_1")
    check_and_set_env_var("CAMERA_ID", 1)

    main()
    print(f"\n total time: {(time()-ts) / 60:.2} minute")
