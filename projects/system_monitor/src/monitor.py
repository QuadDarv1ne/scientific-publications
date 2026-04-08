#!/usr/bin/env python3
"""
System Monitor - Кроссплатформенный мониторинг системы
Поддержка CPU, памяти, дисков, сети и GPU (NVIDIA)
"""

import psutil
import platform
import time
import threading
import json
import csv
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List, Optional, Callable

# GPU мониторинг
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


class SystemMonitor:
    """Основной класс системного мониторинга"""
    
    def __init__(
        self,
        history_size: int = 100,
        enable_gpu: bool = True,
        log_file: Optional[str] = None
    ):
        self.history_size = history_size
        self.enable_gpu = enable_gpu and PYNVML_AVAILABLE
        self.log_file = log_file
        
        self.running = False
        self.monitor_thread = None
        self.callbacks: List[Callable] = []
        
        # Инициализация GPU
        if self.enable_gpu:
            self._init_gpu()
        
        # Настройка логирования
        self._setup_logging()
        
        # Структуры данных
        self._init_data_structures()
    
    def _init_gpu(self):
        """Инициализация NVIDIA GPU"""
        try:
            pynvml.nvmlInit()
            self.gpu_count = pynvml.nvmlDeviceGetCount()
            self.gpu_handles = [
                pynvml.nvmlDeviceGetHandleByIndex(i) 
                for i in range(self.gpu_count)
            ]
            logging.info(f"Обнаружено GPU: {self.gpu_count}")
        except Exception as e:
            logging.warning(f"Не удалось инициализировать GPU: {e}")
            self.enable_gpu = False
    
    def _setup_logging(self):
        """Настройка логирования"""
        if self.log_file:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.log_file),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(
                level=logging.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
    
    def _init_data_structures(self):
        """Инициализация структур данных"""
        self.timestamps = deque(maxlen=self.history_size)
        
        # CPU
        self.cpu_total = deque(maxlen=self.history_size)
        self.cpu_cores: Dict[str, deque] = {}
        
        # Память
        self.memory_percent = deque(maxlen=self.history_size)
        self.memory_used = deque(maxlen=self.history_size)
        
        # Сеть
        self.network_sent = deque(maxlen=self.history_size)
        self.network_recv = deque(maxlen=self.history_size)
        
        # GPU
        self.gpu_load = deque(maxlen=self.history_size)
        self.gpu_memory = deque(maxlen=self.history_size)
        self.gpu_temp = deque(maxlen=self.history_size)
        
        # Диски
        self.disk_usage: Dict[str, deque] = {}
    
    def add_callback(self, callback: Callable):
        """Добавить функцию обратного вызова"""
        self.callbacks.append(callback)
    
    def get_cpu_info(self) -> Dict:
        """Получить информацию о CPU"""
        try:
            # Общая загрузка
            total = psutil.cpu_percent(interval=0.1)
            self.cpu_total.append(total)
            
            # По ядрам
            cores = psutil.cpu_percent(interval=0.1, percpu=True)
            for i, core_val in enumerate(cores):
                key = f'core_{i}'
                if key not in self.cpu_cores:
                    self.cpu_cores[key] = deque(maxlen=self.history_size)
                self.cpu_cores[key].append(core_val)
            
            # Частота
            freq = psutil.cpu_freq()
            
            return {
                'total': total,
                'cores': cores,
                'count_physical': psutil.cpu_count(logical=False),
                'count_logical': psutil.cpu_count(logical=True),
                'frequency_current': freq.current if freq else 0,
                'frequency_min': freq.min if freq else 0,
                'frequency_max': freq.max if freq else 0
            }
        except Exception as e:
            logging.error(f"Ошибка CPU: {e}")
            return {'error': str(e)}
    
    def get_memory_info(self) -> Dict:
        """Получить информацию о памяти"""
        try:
            vm = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            self.memory_percent.append(vm.percent)
            self.memory_used.append(vm.used / (1024**3))
            
            return {
                'total_gb': vm.total / (1024**3),
                'available_gb': vm.available / (1024**3),
                'used_gb': vm.used / (1024**3),
                'percent': vm.percent,
                'swap_total_gb': swap.total / (1024**3),
                'swap_used_gb': swap.used / (1024**3),
                'swap_percent': swap.percent
            }
        except Exception as e:
            logging.error(f"Ошибка памяти: {e}")
            return {'error': str(e)}
    
    def get_disk_info(self) -> Dict:
        """Получить информацию о дисках"""
        disks = {}
        try:
            for partition in psutil.disk_partitions():
                try:
                    if partition.fstype in ('tmpfs', 'devtmpfs', 'squashfs'):
                        continue
                    
                    usage = psutil.disk_usage(partition.mountpoint)
                    device = partition.device
                    
                    if device not in self.disk_usage:
                        self.disk_usage[device] = deque(maxlen=self.history_size)
                    self.disk_usage[device].append(usage.percent)
                    
                    disks[device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3),
                        'percent': usage.percent
                    }
                except PermissionError:
                    continue
        except Exception as e:
            logging.error(f"Ошибка диска: {e}")
        
        return disks
    
    def get_network_info(self) -> Dict:
        """Получить информацию о сети"""
        try:
            net_io = psutil.net_io_counters()
            
            now = time.time()
            if hasattr(self, 'last_net_time'):
                dt = now - self.last_net_time
                if dt > 0:
                    sent_speed = (net_io.bytes_sent - self.last_net.bytes_sent) / dt / 1024
                    recv_speed = (net_io.bytes_recv - self.last_net.bytes_recv) / dt / 1024
                else:
                    sent_speed = recv_speed = 0
            else:
                sent_speed = recv_speed = 0
            
            self.last_net = net_io
            self.last_net_time = now
            
            self.network_sent.append(sent_speed)
            self.network_recv.append(recv_speed)
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'sent_speed_kbs': sent_speed,
                'recv_speed_kbs': recv_speed,
                'err_in': net_io.errin,
                'err_out': net_io.errout,
                'drop_in': net_io.dropin,
                'drop_out': net_io.dropout
            }
        except Exception as e:
            logging.error(f"Ошибка сети: {e}")
            return {'error': str(e)}
    
    def get_gpu_info(self) -> Dict:
        """Получить информацию о GPU (NVIDIA)"""
        if not self.enable_gpu:
            return {'message': 'GPU мониторинг отключен'}
        
        gpus = {}
        try:
            for i, handle in enumerate(self.gpu_handles):
                # Имя
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                
                # Загрузка
                load = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_load = load.gpu
                mem_load = load.memory
                
                # Память
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Температура
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    temp = 0
                
                # Энергопотребление
                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # mW -> W
                except:
                    power = 0
                
                # История
                self.gpu_load.append(gpu_load)
                self.gpu_memory.append(mem_load)
                self.gpu_temp.append(temp)
                
                gpus[f'GPU_{i}'] = {
                    'name': name,
                    'load_percent': gpu_load,
                    'memory_used_mb': mem_info.used / (1024**2),
                    'memory_total_mb': mem_info.total / (1024**2),
                    'memory_percent': mem_load,
                    'temperature_c': temp,
                    'power_w': power
                }
        except Exception as e:
            logging.error(f"Ошибка GPU: {e}")
            return {'error': str(e)}
        
        return gpus
    
    def get_processes_info(self, top_n: int = 10, sort_by: str = 'memory') -> List[Dict]:
        """Получить информацию о процессах"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
                try:
                    info = proc.info
                    mem_info = info.get('memory_info')
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'][:50] if info['name'] else '',
                        'cpu_percent': info['cpu_percent'] or 0,
                        'memory_percent': info['memory_percent'] or 0,
                        'memory_mb': mem_info.rss / (1024**2) if mem_info else 0,
                        'status': info.get('status', 'unknown')
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Сортировка
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            else:
                processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            return processes[:top_n]
        except Exception as e:
            logging.error(f"Ошибка процессов: {e}")
            return [{'error': str(e)}]
    
    def get_system_info(self) -> Dict:
        """Получить общую информацию о системе"""
        try:
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            return {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'hostname': platform.node(),
                'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
                'uptime_seconds': uptime,
                'uptime_formatted': self._format_uptime(uptime)
            }
        except Exception as e:
            logging.error(f"Ошибка системы: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Форматирование uptime"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{days}д {hours}ч {mins}м"
    
    def collect_all_data(self) -> Dict:
        """Сбор всех данных системы"""
        self.timestamps.append(time.time())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'gpu': self.get_gpu_info(),
            'processes': self.get_processes_info(10)
        }
    
    def start_monitoring(self, interval: float = 1.0):
        """Запуск мониторинга"""
        self.running = True
        
        def loop():
            while self.running:
                try:
                    data = self.collect_all_data()
                    for callback in self.callbacks:
                        callback(data)
                    time.sleep(interval)
                except Exception as e:
                    logging.error(f"Ошибка мониторинга: {e}")
        
        self.monitor_thread = threading.Thread(target=loop, daemon=True)
        self.monitor_thread.start()
        logging.info(f"Мониторинг запущен (интервал: {interval}с)")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
            except:
                pass
        
        logging.info("Мониторинг остановлен")
    
    def export_json(self, filepath: str):
        """Экспорт данных в JSON"""
        data = self.collect_all_data()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logging.info(f"Экспорт JSON: {filepath}")
    
    def export_csv(self, filepath: str):
        """Экспорт данных в CSV"""
        data = self.collect_all_data()
        
        # Основные метрики
        row = {
            'timestamp': data['timestamp'],
            'cpu_percent': data['cpu'].get('total', 0),
            'memory_percent': data['memory'].get('percent', 0),
            'network_sent_kbs': data['network'].get('sent_speed_kbs', 0),
            'network_recv_kbs': data['network'].get('recv_speed_kbs', 0),
        }
        
        # GPU
        gpu = data.get('gpu', {})
        if 'GPU_0' in gpu:
            row['gpu_load'] = gpu['GPU_0'].get('load_percent', 0)
            row['gpu_memory_percent'] = gpu['GPU_0'].get('memory_percent', 0)
            row['gpu_temp'] = gpu['GPU_0'].get('temperature_c', 0)
        
        # Запись в CSV
        file_exists = Path(filepath).exists()
        with open(filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        
        logging.info(f"Экспорт CSV: {filepath}")


def console_display(data: Dict):
    """Вывод данных в консоль"""
    # Очистка
    print('\033[2J\033[H]', end='')
    
    ts = data['timestamp']
    cpu = data['cpu']
    mem = data['memory']
    net = data['network']
    gpu = data.get('gpu', {})
    
    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  SYSTEM MONITOR  |  {ts[:19]}".ljust(62) + "║")
    print(f"╠══════════════════════════════════════════════════════════╣")
    
    # CPU & Memory
    cpu_total = cpu.get('total', 0)
    mem_percent = mem.get('percent', 0)
    mem_used = mem.get('used_gb', 0)
    mem_total = mem.get('total_gb', 0)
    
    cpu_bar = '█' * int(cpu_total / 5) + '░' * (20 - int(cpu_total / 5))
    mem_bar = '█' * int(mem_percent / 5) + '░' * (20 - int(mem_percent / 5))
    
    print(f"║  CPU: [{cpu_bar}] {cpu_total:5.1f}%".ljust(62) + "║")
    print(f"║  RAM: [{mem_bar}] {mem_percent:5.1f}%  {mem_used:5.1f}/{mem_total:5.1f} GB".ljust(62) + "║")
    
    # Network
    sent = net.get('sent_speed_kbs', 0)
    recv = net.get('recv_speed_kbs', 0)
    print(f"║  NET:  ↑ {sent:7.1f} KB/s  ↓ {recv:7.1f} KB/s".ljust(62) + "║")
    
    # GPU
    if 'GPU_0' in gpu:
        g = gpu['GPU_0']
        g_load = g.get('load_percent', 0)
        g_mem = g.get('memory_percent', 0)
        g_temp = g.get('temperature_c', 0)
        g_bar = '█' * int(g_load / 5) + '░' * (20 - int(g_load / 5))
        print(f"║  GPU: [{g_bar}] {g_load:5.1f}%  MEM: {g_mem:5.1f}%  {g_temp}°C".ljust(62) + "║")
    
    # Top processes
    print(f"╠══════════════════════════════════════════════════════════╣")
    print(f"║  TOP PROCESSES (by memory)".ljust(62) + "║")
    print(f"╠══════════════════════════════════════════════════════════╣")
    
    for proc in data['processes'][:5]:
        if 'error' not in proc:
            name = proc['name'][:28]
            mem_mb = proc['memory_mb']
            cpu = proc['cpu_percent']
            print(f"║  {name:28s} {mem_mb:7.1f} MB  CPU: {cpu:5.1f}%".ljust(62) + "║")
    
    print(f"╚══════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description='System Monitor')
    parser.add_argument('--interval', type=float, default=2, help='Интервал обновления (сек)')
    parser.add_argument('--gpu', action='store_true', help='Включить мониторинг GPU')
    parser.add_argument('--export', choices=['json', 'csv'], help='Экспорт данных')
    parser.add_argument('--output', default='system_data', help='Имя выходного файла')
    parser.add_argument('--log', help='Путь к лог-файлу')
    parser.add_argument('--daemon', action='store_true', help='Режим демона')
    parser.add_argument('--once', action='store_true', help='Однократный сбор данных')
    
    args = parser.parse_args()
    
    # Создание монитора
    monitor = SystemMonitor(
        enable_gpu=args.gpu or PYNVML_AVAILABLE,
        log_file=args.log
    )
    
    # Однократный сбор
    if args.once:
        data = monitor.collect_all_data()
        print(json.dumps(data, indent=2, default=str))
        return
    
    # Экспорт
    if args.export:
        if args.export == 'json':
            monitor.export_json(f"{args.output}.json")
        else:
            monitor.export_csv(f"{args.output}.csv")
        return
    
    # Интерактивный режим
    print("Запуск системного монитора...")
    print("Нажмите Ctrl+C для выхода\n")
    
    monitor.add_callback(console_display)
    
    try:
        monitor.start_monitoring(interval=args.interval)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nОстановка...")
    finally:
        monitor.stop_monitoring()


if __name__ == '__main__':
    main()
