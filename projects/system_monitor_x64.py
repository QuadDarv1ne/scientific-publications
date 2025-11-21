# pip install psutil GPUtil matplotlib pandas numpy

import psutil
import GPUtil
import platform
import time
import threading
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class SystemMonitor:
    def __init__(self, history_size=100):
        self.history_size = history_size
        self.setup_data_structures()
        self.running = False
        self.monitor_thread = None
        
    def setup_data_structures(self):
        """Инициализация структур данных для хранения истории"""
        self.timestamps = deque(maxlen=self.history_size)
        
        # CPU данные
        self.cpu_percent = deque(maxlen=self.history_size)
        self.cpu_cores = {}
        
        # Память
        self.memory_percent = deque(maxlen=self.history_size)
        self.memory_used = deque(maxlen=self.history_size)
        
        # Диски
        self.disk_usage = {}
        
        # Сеть
        self.network_sent = deque(maxlen=self.history_size)
        self.network_recv = deque(maxlen=self.history_size)
        
        # GPU
        self.gpu_data = {}
        
    def get_cpu_info(self):
        """Получение информации о процессоре"""
        try:
            # Общая загрузка CPU
            cpu_total = psutil.cpu_percent(interval=0.1)
            self.cpu_percent.append(cpu_total)
            
            # Загрузка по ядрам
            cores = psutil.cpu_percent(interval=0.1, percpu=True)
            for i, core in enumerate(cores):
                if f'core_{i}' not in self.cpu_cores:
                    self.cpu_cores[f'core_{i}'] = deque(maxlen=self.history_size)
                self.cpu_cores[f'core_{i}'].append(core)
                
            return {
                'total': cpu_total,
                'cores': cores,
                'count': psutil.cpu_count(logical=False),
                'logical_count': psutil.cpu_count(logical=True),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A'
            }
        except Exception as e:
            return {'error': f'CPU error: {e}'}

    def get_memory_info(self):
        """Получение информации о памяти"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            self.memory_percent.append(memory.percent)
            self.memory_used.append(memory.used / (1024**3))  # GB
            
            return {
                'total': memory.total / (1024**3),  # GB
                'available': memory.available / (1024**3),  # GB
                'used': memory.used / (1024**3),  # GB
                'percent': memory.percent,
                'swap_total': swap.total / (1024**3),  # GB
                'swap_used': swap.used / (1024**3),  # GB
                'swap_percent': swap.percent
            }
        except Exception as e:
            return {'error': f'Memory error: {e}'}

    def get_disk_info(self):
        """Получение информации о дисках"""
        try:
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_name = partition.device.split('\\')[-1] if '\\' in partition.device else partition.mountpoint
                    
                    if disk_name not in self.disk_usage:
                        self.disk_usage[disk_name] = deque(maxlen=self.history_size)
                    
                    self.disk_usage[disk_name].append(usage.percent)
                    
                    disk_info[disk_name] = {
                        'total': usage.total / (1024**3),  # GB
                        'used': usage.used / (1024**3),  # GB
                        'free': usage.free / (1024**3),  # GB
                        'percent': usage.percent,
                        'fstype': partition.fstype,
                        'mountpoint': partition.mountpoint
                    }
                except PermissionError:
                    continue
            return disk_info
        except Exception as e:
            return {'error': f'Disk error: {e}'}

    def get_network_info(self):
        """Получение информации о сети"""
        try:
            net_io = psutil.net_io_counters()
            
            # Рассчитываем скорость (байт/сек)
            if hasattr(self, 'last_net_io'):
                time_diff = time.time() - self.last_net_time
                sent_speed = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
                recv_speed = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
                
                self.network_sent.append(sent_speed / 1024)  # KB/s
                self.network_recv.append(recv_speed / 1024)  # KB/s
            else:
                self.network_sent.append(0)
                self.network_recv.append(0)
            
            self.last_net_io = net_io
            self.last_net_time = time.time()
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'sent_speed': self.network_sent[-1] if self.network_sent else 0,
                'recv_speed': self.network_recv[-1] if self.network_recv else 0
            }
        except Exception as e:
            return {'error': f'Network error: {e}'}

    def get_gpu_info(self):
        """Получение информации о GPU"""
        try:
            gpus = GPUtil.getGPUs()
            gpu_info = {}
            
            for i, gpu in enumerate(gpus):
                gpu_name = f'GPU_{i}'
                if gpu_name not in self.gpu_data:
                    self.gpu_data[gpu_name] = {
                        'load': deque(maxlen=self.history_size),
                        'memory': deque(maxlen=self.history_size),
                        'temperature': deque(maxlen=self.history_size)
                    }
                
                self.gpu_data[gpu_name]['load'].append(gpu.load * 100)
                self.gpu_data[gpu_name]['memory'].append(gpu.memoryUtil * 100)
                self.gpu_data[gpu_name]['temperature'].append(gpu.temperature)
                
                gpu_info[gpu_name] = {
                    'name': gpu.name,
                    'load': gpu.load * 100,
                    'memory_total': gpu.memoryTotal,
                    'memory_used': gpu.memoryUsed,
                    'memory_free': gpu.memoryFree,
                    'memory_percent': gpu.memoryUtil * 100,
                    'temperature': gpu.temperature,
                    'driver': gpu.driver
                }
            
            return gpu_info if gpu_info else {'message': 'No GPUs detected'}
        except Exception as e:
            return {'error': f'GPU error: {e}'}

    def get_process_info(self, top_n=10):
        """Получение информации о процессах"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Сортируем по использованию CPU
            processes.sort(key=lambda x: x.info['cpu_percent'] or 0, reverse=True)
            
            top_processes = []
            for proc in processes[:top_n]:
                memory_mb = proc.info['memory_info'].rss / (1024 * 1024) if proc.info['memory_info'] else 0
                top_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'] or 0,
                    'memory_percent': proc.info['memory_percent'] or 0,
                    'memory_mb': memory_mb
                })
            
            return top_processes
        except Exception as e:
            return {'error': f'Process error: {e}'}

    def get_system_info(self):
        """Получение общей информации о системе"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'hostname': platform.node(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def collect_all_data(self):
        """Сбор всех данных системы"""
        current_time = time.time()
        self.timestamps.append(current_time)
        
        data = {
            'timestamp': current_time,
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'gpu': self.get_gpu_info(),
            'processes': self.get_process_info()
        }
        
        return data

    def start_monitoring(self, callback=None, interval=1):
        """Запуск мониторинга в отдельном потоке"""
        self.running = True
        
        def monitor_loop():
            while self.running:
                data = self.collect_all_data()
                if callback:
                    callback(data)
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def generate_report(self):
        """Генерация отчета о системе"""
        data = self.collect_all_data()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'system_info': data['system'],
            'current_status': {
                'cpu_usage': data['cpu'].get('total', 0),
                'memory_usage': data['memory'].get('percent', 0),
                'disk_usage': {k: v['percent'] for k, v in data['disk'].items()},
                'network_activity': {
                    'upload_speed': data['network'].get('sent_speed', 0),
                    'download_speed': data['network'].get('recv_speed', 0)
                }
            },
            'top_processes': data['processes']
        }
        
        return report

# Пример использования
def print_monitor_data(data):
    """Простая функция для вывода данных в консоль"""
    print("\033[H\033[J", end="")  # Очистка консоли
    print(f"=== СИСТЕМНЫЙ МОНИТОРИНГ ===")
    print(f"Время: {datetime.now().strftime('%H:%M:%S')}")
    print(f"CPU: {data['cpu'].get('total', 0):.1f}%")
    print(f"Память: {data['memory'].get('percent', 0):.1f}%")
    
    if 'gpu' in data and 'GPU_0' in data['gpu']:
        gpu = data['gpu']['GPU_0']
        print(f"GPU: {gpu.get('load', 0):.1f}% (Память: {gpu.get('memory_percent', 0):.1f}%)")
    
    print(f"Сеть: ↑{data['network'].get('sent_speed', 0):.1f} KB/s ↓{data['network'].get('recv_speed', 0):.1f} KB/s")

if __name__ == "__main__":
    monitor = SystemMonitor()
    
    try:
        print("Запуск системного мониторинга... (Ctrl+C для остановки)")
        monitor.start_monitoring(callback=print_monitor_data, interval=2)
        
        # Держим программу активной
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка мониторинга...")
        monitor.stop_monitoring()
