# API Documentation

## Основные компоненты

### 1. DetectionTrackingNodes

Модуль для детекции и трекинга объектов на видео.

```python
from nodes.DetectionTrackingNodes import DetectionTrackingNodes

# Инициализация
config = {
    "detection_node": {
        "weight_pth": "weights/yolov8m.pt",
        "classes_to_detect": [2, 3, 5, 7],  # car, motorcycle, bus, truck
        "confidence": 0.1,
        "iou": 0.7,
        "imgsz": 640
    },
    "tracking_node": {
        "first_track_thresh": 0.5,
        "second_track_thresh": 0.1,
        "match_thresh": 0.95,
        "track_buffer": 125
    }
}

detector = DetectionTrackingNodes(config)

# Обработка кадра
frame_element = detector.process(frame_element)
```

**Attributes:**
- `model`: YOLO модель для детекции
- `tracker`: ByteTracker для отслеживания
- `conf`: Порог уверенности (0.0-1.0)
- `iou`: Порог IoU для NMS (0.0-1.0)

**Returns:**
- `frame_element.id_list`: Список ID треков
- `frame_element.tracked_xyxy`: Координаты bbox [[x1,y1,x2,y2], ...]
- `frame_element.tracked_cls`: Классы объектов
- `frame_element.tracked_conf`: Уверенность детекций

---

### 2. FPS_Counter

Счетчик FPS по скользящему окну кадров.

```python
from utils_local.utils import FPS_Counter

# Инициализация с окном в 30 кадров
fps_counter = FPS_Counter(calc_time_perion_N_frames=30)

# В цикле обработки
while True:
    # ... обработка кадра ...
    fps = fps_counter.calc_FPS()
    print(f"Current FPS: {fps}")
```

**Methods:**
- `calc_FPS()`: Вычисляет FPS, возвращает `float`

---

### 3. FrameElement

Элемент данных для передачи информации о кадре между нодами.

```python
from elements.FrameElement import FrameElement

frame_element = FrameElement(
    frame=frame,           # numpy.ndarray: BGR изображение
    frame_number=1,        # int: Номер кадра
    timestamp=time.time()  # float: Временная метка
)
```

**Attributes:**
- `frame`: numpy.ndarray - исходный кадр
- `frame_number`: int - номер кадра
- `timestamp`: float - время получения кадра
- `detected_xyxy`: List - координаты детекций
- `detected_conf`: List - уверенность детекций
- `detected_cls`: List - классы объектов
- `id_list`: List[int] - ID треков
- `tracked_xyxy`: List - координаты треков
- `tracked_conf`: List - уверенность треков
- `tracked_cls`: List - классы треков

---

### 4. Утилиты

#### check_and_set_env_var

```python
from utils_local.utils import check_and_set_env_var

# Установка переменной окружения с значением по умолчанию
check_and_set_env_var("VIDEO_SRC", "test_videos/video.mp4")
```

#### intersects_central_point

```python
from utils_local.utils import intersects_central_point

bbox = [100, 100, 200, 200]
polygons = {
    "1": [50, 50, 250, 50, 250, 250, 50, 250]  # x1,y1, x2,y2, ...
}

road_id = intersects_central_point(bbox, polygons)
# Returns: int или None
```

---

## Конфигурация

### app_config.yaml структура

```yaml
pipeline:
  save_video: false          # Сохранять ли результат
  show_in_web: true          # Веб-интерфейс Flask
  send_info_kafka: true      # Отправка в Kafka

video_reader:
  src: ${oc.env:VIDEO_SRC}   # Путь к видео или RTSP
  skip_secs: 0               # Пропуск кадров (сек)
  roads_info: "configs/entry_exit_lanes.json"

detection_node:
  weight_pth: "weights/yolov8m.pt"
  classes_to_detect: [2,3,5,7]  # COCO классы
  confidence: 0.10               # Порог уверенности
  iou: 0.7                       # Порог NMS
  imgsz: 640                     # Размер для инференса

tracking_node:
  first_track_thresh: 0.5        # Инициализация трека
  second_track_thresh: 0.10      # Поддержание трека
  match_thresh: 0.95             # Порог сопоставления
  track_buffer: 125              # Время жизни (кадры)

show_node:
  scale: 0.6                     # Масштаб отображения
  imshow: false                  # cv2.imshow
  draw_fps_info: true            # Показывать FPS
  show_roi: true                 # Показывать регионы
```

---

## Примеры использования

### Пример 1: Обработка видео файла

```python
import hydra
from main_optimized import main

if __name__ == "__main__":
    # Hydra автоматически загрузит configs/app_config.yaml
    main()
```

### Пример 2: Кастомная обработка

```python
from nodes.VideoReader import VideoReader
from nodes.DetectionTrackingNodes import DetectionTrackingNodes
from nodes.ShowNode import ShowNode

# Конфигурация
config = {...}

# Инициализация нод
video_reader = VideoReader(config["video_reader"])
detector = DetectionTrackingNodes(config)
show_node = ShowNode(config)

# Обработка
for frame_element in video_reader.process():
    frame_element = detector.process(frame_element)
    frame_element = show_node.process(frame_element)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

### Пример 3: Только детекция без трекинга

```python
from ultralytics import YOLO

model = YOLO("weights/yolov8m.pt")

results = model.predict(
    frame,
    imgsz=640,
    conf=0.1,
    iou=0.7,
    classes=[2, 3, 5, 7],
    verbose=False
)

boxes = results[0].boxes.xyxy.cpu().numpy()
confidences = results[0].boxes.conf.cpu().numpy()
classes = results[0].boxes.cls.cpu().numpy()
```

---

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `VIDEO_SRC` | Путь к видео или RTSP URL | `test_videos/test_video.mp4` |
| `ROADS_JSON` | Конфигурация полигонов дорог | `configs/entry_exit_lanes.json` |
| `TOPIC_NAME` | Kafka топик для статистики | `statistics_1` |
| `CAMERA_ID` | ID камеры | `1` |

---

## Типы данных

### BBox Format

```python
# XYXY формат (используется в проекте)
bbox = [x1, y1, x2, y2]  # List[float]
# где x1,y1 - верхний левый угол
#     x2,y2 - нижний правый угол
```

### Polygon Format

```python
# Плоский список координат
polygon = [x1, y1, x2, y2, x3, y3, ...]  # List[float]
# Минимум 3 точки (6 координат) для треугольника
```

---

## Ошибки и исключения

### Общие исключения

```python
try:
    detector = DetectionTrackingNodes(config)
except FileNotFoundError:
    # Файл весов модели не найден
    pass
except RuntimeError:
    # Ошибка инициализации модели
    pass
except ValueError:
    # Невалидная конфигурация
    pass
```

### Логирование

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Использование
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.exception("Критическая ошибка с traceback")
```
