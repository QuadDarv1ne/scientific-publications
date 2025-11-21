import psutil
import platform
import time
import threading
from datetime import datetime
import os
import sys

try:
    import GPUtil
except ImportError:
    GPUtil = None

class SimpleSystemMonitor:
    def __init__(self):
        self.running = False
        self.history = []
        self.max_history = 50
        
    def clear_console(self):
        """Очистка консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_cpu_info(self):
        """Информация о процессоре"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_freq = psutil.cpu_freq()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            return {
                'usage': cpu_percent,
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'frequency': f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A",
                'load_avg': load_avg
            }
        except Exception as e:
            return {'usage': 0, 'cores': 'N/A', 'threads': 'N/A', 'frequency': 'N/A', 'error': str(e)}
    
    def get_memory_info(self):
        """Информация о памяти"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total / (1024**3),
                'used': memory.used / (1024**3),
                'available': memory.available / (1024**3),
                'percent': memory.percent,
                'swap_total': swap.total / (1024**3),
                'swap_used': swap.used / (1024**3),
                'swap_percent': swap.percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_disk_info(self):
        """Информация о дисках"""
        try:
            disks = {}
            for partition in psutil.disk_partitions():
                try:
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks[partition.device] = {
                        'mount': partition.mountpoint,
                        'total': usage.total / (1024**3),
                        'used': usage.used / (1024**3),
                        'free': usage.free / (1024**3),
                        'percent': usage.percent,
                        'fstype': partition.fstype
                    }
                except PermissionError:
                    continue
            return disks
        except Exception as e:
            return {'error': str(e)}
    
    def get_network_info(self):
        """Информация о сети"""
        try:
            net_io = psutil.net_io_counters()
            net_if = psutil.net_if_addrs()
            
            # Расчет скорости
            current_time = time.time()
            if hasattr(self, 'last_net_io') and hasattr(self, 'last_net_time'):
                time_diff = current_time - self.last_net_time
                upload_speed = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff / 1024  # KB/s
                download_speed = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff / 1024  # KB/s
            else:
                upload_speed = download_speed = 0
            
            self.last_net_io = net_io
            self.last_net_time = current_time
            
            return {
                'upload_speed': upload_speed,
                'download_speed': download_speed,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'interfaces': list(net_if.keys())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_gpu_info(self):
        """Информация о GPU"""
        gpu_info = {}
        try:
            if GPUtil:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    gpu_info[f'GPU_{i}'] = {
                        'name': gpu.name,
                        'load': gpu.load * 100,
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal,
                        'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                        'temperature': gpu.temperature
                    }
            else:
                # Альтернативный способ для Windows через WMI
                if platform.system() == 'Windows':
                    try:
                        import wmi
                        c = wmi.WMI()
                        for gpu in c.Win32_VideoController():
                            if gpu.Name:
                                gpu_info['GPU_0'] = {
                                    'name': gpu.Name,
                                    'memory': f"{int(gpu.AdapterRAM) / (1024**3):.1f} GB" if gpu.AdapterRAM else "N/A"
                                }
                    except:
                        pass
        except Exception as e:
            gpu_info['error'] = str(e)
        
        return gpu_info if gpu_info else {'message': 'GPU info not available'}
    
    def get_processes_info(self, top_n=10):
        """Информация о процессах"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Сортируем по использованию памяти
            processes.sort(key=lambda x: x.info['memory_info'].rss if x.info['memory_info'] else 0, reverse=True)
            
            top_processes = []
            for proc in processes[:top_n]:
                memory_mb = proc.info['memory_info'].rss / (1024 * 1024) if proc.info['memory_info'] else 0
                top_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'][:30],  # Обрезаем длинные имена
                    'cpu': proc.info['cpu_percent'] or 0,
                    'memory_mb': memory_mb
                })
            
            return top_processes
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_system_info(self):
        """Общая информация о системе"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'hostname': platform.node(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'uptime': time.time() - psutil.boot_time()
        }
    
    def collect_all_data(self):
        """Сбор всех данных"""
        return {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'gpu': self.get_gpu_info(),
            'processes': self.get_processes_info(8)
        }
    
    def display_dashboard(self, data):
        """Отображение информации в консоли"""
        self.clear_console()
        
        print("=" * 80)
        print(f"СИСТЕМНЫЙ МОНИТОРИНГ - {data['timestamp']}")
        print("=" * 80)
        
        # Системная информация
        sys_info = data['system']
        print(f"Система: {sys_info['platform']} {sys_info['platform_release']} ({sys_info['architecture']})")
        print(f"Хост: {sys_info['hostname']}")
        print(f"Аптайм: {int(sys_info['uptime'] // 3600)}ч {int((sys_info['uptime'] % 3600) // 60)}м")
        
        print("\n" + "-" * 40)
        print("ПРОИЗВОДИТЕЛЬНОСТЬ")
        print("-" * 40)
        
        # CPU
        cpu = data['cpu']
        print(f"CPU: {cpu['usage']:5.1f}% | Ядра: {cpu.get('cores', 'N/A')} | Частота: {cpu.get('frequency', 'N/A')}")
        
        # Память
        mem = data['memory']
        if 'error' not in mem:
            print(f"ОЗУ: {mem['percent']:5.1f}% | Используется: {mem['used']:5.1f}GB / {mem['total']:5.1f}GB")
        
        # Сеть
        net = data['network']
        if 'error' not in net:
            print(f"Сеть: ↑{net['upload_speed']:5.1f} KB/s ↓{net['download_speed']:5.1f} KB/s")
        
        # GPU
        gpu = data['gpu']
        if 'GPU_0' in gpu:
            gpu0 = gpu['GPU_0']
            print(f"GPU: {gpu0.get('load', 0):5.1f}% | Память: {gpu0.get('memory_percent', 0):5.1f}% | {gpu0.get('name', 'N/A')}")
        
        print("\n" + "-" * 40)
        print("ДИСКИ")
        print("-" * 40)
        
        # Диски
        disks = data['disk']
        for disk_name, disk_info in list(disks.items())[:3]:  # Показываем первые 3 диска
            if 'error' not in disk_info:
                print(f"{disk_name}: {disk_info['percent']:5.1f}% | {disk_info['used']:5.1f}GB / {disk_info['total']:5.1f}GB")
        
        print("\n" + "-" * 40)
        print("ПРОЦЕССЫ (по памяти)")
        print("-" * 40)
        
        # Процессы
        processes = data['processes']
        for proc in processes:
            if 'error' not in proc:
                print(f"{proc['pid']:6} {proc['name']:30} {proc['memory_mb']:8.1f} MB")
        
        print("\n" + "=" * 80)
        print("Ctrl+C для выхода")
    
    def start_monitoring(self, interval=2):
        """Запуск мониторинга"""
        self.running = True
        
        def monitor_loop():
            while self.running:
                try:
                    data = self.collect_all_data()
                    self.display_dashboard(data)
                    time.sleep(interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.clear_console()
                    print(f"Ошибка: {e}")
                    time.sleep(interval)
        
        monitor_loop()
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.running = False

def main():
    """Основная функция"""
    print("Запуск системного мониторинга...")
    print("Убедитесь, что установлены необходимые библиотеки:")
    print("pip install psutil")
    print("pip install gputil (опционально для GPU)")
    print("\nЗагрузка...")
    time.sleep(2)
    
    monitor = SimpleSystemMonitor()
    
    try:
        monitor.start_monitoring(interval=3)
    except KeyboardInterrupt:
        print("\n\nМониторинг остановлен.")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        print("Попробуйте установить зависимости: pip install psutil")

if __name__ == "__main__":
    main()
