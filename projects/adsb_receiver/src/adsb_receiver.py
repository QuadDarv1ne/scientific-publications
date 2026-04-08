"""
ADS-B Receiver Module
Приём и декодирование данных ADS-B с самолётов

Частота: 1090 MHz
"""

import os
import subprocess
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import threading
import socket
import sys

logger = logging.getLogger(__name__)


class ADSBreceiver:
    """
    Класс для приёма ADS-B данных
    """
    
    FREQUENCY = 1090  # MHz
    
    def __init__(
        self,
        data_dir: str = "data",
        results_dir: str = "results"
    ):
        """Инициализация ADS-B приёмника"""
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_receiving = False
        self.process: Optional[subprocess.Popen] = None
        self.aircraft_data: Dict[str, dict] = {}
        self.receive_thread: Optional[threading.Thread] = None
        
        self.stats = {
            'total_messages': 0,
            'total_aircraft': 0,
            'start_time': None
        }
    
    def check_rtl_sdr(self) -> bool:
        """Проверка наличия RTL-SDR"""
        try:
            result = subprocess.run(
                ['rtl_test', '-t'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("rtl_test не найден")
            return False
        except subprocess.TimeoutExpired:
            return False
    
    def check_dump1090(self) -> bool:
        """Проверка наличия dump1090"""
        result = subprocess.run(
            ['which', 'dump1090'],
            capture_output=True
        )
        if result.returncode == 0:
            return True
        
        # Проверка dump1090-mutability
        result = subprocess.run(
            ['which', 'dump1090-mutability'],
            capture_output=True
        )
        return result.returncode == 0
    
    def get_dump1090_command(self) -> List[str]:
        """Получение команды dump1090"""
        # Пробуем разные варианты
        for cmd in ['dump1090-mutability', 'dump1090']:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True
            )
            if result.returncode == 0:
                return [cmd, '--interactive', '--net']
        
        return []
    
    def start_receiver(self, use_net: bool = True) -> bool:
        """
        Запуск ADS-B приёмника
        
        Args:
            use_net: Использовать сетевой режим (просмотр через браузер)
        """
        if not self.check_rtl_sdr():
            logger.error("RTL-SDR не найден")
            return False
        
        cmd = self.get_dump1090_command()
        if not cmd:
            logger.error("dump1090 не установлен")
            logger.info("Установите: sudo apt-get install dump1090-mutability")
            return False
        
        logger.info(f"Запуск ADS-B приёмника на частоте {self.FREQUENCY} MHz")
        
        if use_net:
            cmd.extend(['--net', '--net-http-port', '8080'])
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.is_receiving = True
            self.stats['start_time'] = datetime.now()
            
            logger.info("ADS-B приёмник запущен")
            
            # Запуск потока мониторинга
            self.receive_thread = threading.Thread(target=self._monitor_output, daemon=True)
            self.receive_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска: {e}")
            return False
    
    def _monitor_output(self):
        """Мониторинг вывода dump1090"""
        if not self.process:
            return
            
        # Читаем из stdout если доступно
        try:
            if self.process.stdout:
                for line in self.process.stdout:
                    line = line.decode('utf-8', errors='ignore').strip()
                    if line:
                        self._parse_message(line)
        except Exception as e:
            logger.error(f"Ошибка мониторинга: {e}")
    
    def _parse_message(self, message: str):
        """Парсинг сообщения ADS-B"""
        self.stats['total_messages'] += 1
        
        # Формат dump1090: ICAO,Callsign,Lat,Lon,Alt,Track,Speed,Vertical
        # Пример: *5A7D8D,UAL123,45.123,37.456,35000,090,450,0
        
        if message.startswith('*') and message.endswith(';'):
            parts = message[1:-1].split(',')
            if len(parts) >= 8:
                icao = parts[0]
                callsign = parts[1] if parts[1] else ''
                lat = float(parts[2]) if parts[2] else 0
                lon = float(parts[3]) if parts[3] else 0
                alt = int(parts[4]) if parts[4] else 0
                track = int(parts[5]) if parts[5] else 0
                speed = int(parts[6]) if parts[6] else 0
                vertical = int(parts[7]) if parts[7] else 0
                
                self.aircraft_data[icao] = {
                    'icao': icao,
                    'callsign': callsign,
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': alt,
                    'track': track,
                    'speed': speed,
                    'vertical_speed': vertical,
                    'last_update': datetime.now().isoformat()
                }
                
                self.stats['total_aircraft'] = len(self.aircraft_data)
    
    def get_aircraft(self) -> List[dict]:
        """Получение списка видимых самолётов"""
        return list(self.aircraft_data.values())
    
    def export_data(self, format: str = 'json') -> Optional[str]:
        """
        Экспорт данных
        
        Args:
            format: Формат (json, csv)
        """
        aircraft = self.get_aircraft()
        
        if not aircraft:
            logger.warning("Нет данных для экспорта")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            output_file = self.results_dir / f"aircraft_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'count': len(aircraft),
                    'aircraft': aircraft,
                    'stats': self.stats
                }, f, indent=2)
            return str(output_file)
        
        elif format == 'csv':
            output_file = self.results_dir / f"aircraft_{timestamp}.csv"
            import csv
            keys = aircraft[0].keys()
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(aircraft)
            return str(output_file)
        
        return None
    
    def get_stats(self) -> dict:
        """Получение статистики"""
        runtime = 0
        if self.stats['start_time']:
            runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'runtime_seconds': runtime,
            'total_messages': self.stats['total_messages'],
            'total_aircraft': self.stats['total_aircraft'],
            'current_aircraft': len(self.aircraft_data)
        }
    
    def stop(self):
        """Остановка приёмника"""
        self.is_receiving = False
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        logger.info("ADS-B приёмник остановлен")


def main():
    """Демонстрация работы"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ADS-B Receiver')
    parser.add_argument('--duration', type=int, default=60, help='Длительность в секундах')
    parser.add_argument('--export', choices=['json', 'csv'], default='json', help='Формат экспорта')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    receiver = ADSBreceiver()
    
    print("=" * 50)
    print("ADS-B RECEIVER")
    print("=" * 50)
    
    # Проверка
    if not receiver.check_rtl_sdr():
        print("❌ RTL-SDR не найден!")
        return 1
    
    if not receiver.check_dump1090():
        print("❌ dump1090 не установлен!")
        print("   Установите: sudo apt-get install dump1090-mutability")
        return 1
    
    print("✓ RTL-SDR и dump1090 готовы")
    print(f"  Частота: {receiver.FREQUENCY} MHz")
    print("=" * 50)
    
    # Запуск
    if receiver.start_receiver(use_net=True):
        print("\n📡 Приём данных ADS-B...")
        print(f"   Веб-интерфейс: http://localhost:8080")
        print(f"   Длительность: {args.duration} сек")
        
        try:
            while args.duration > 0:
                time.sleep(10)
                args.duration -= 10
                
                stats = receiver.get_stats()
                print(f"   Сообщений: {stats['total_messages']}, "
                      f"Самолётов: {stats['current_aircraft']}")
                
        except KeyboardInterrupt:
            print("\nОстановка...")
        
        # Экспорт
        result = receiver.export_data(format=args.export)
        if result:
            print(f"\n✓ Данные сохранены: {result}")
        
        stats = receiver.get_stats()
        print(f"\n📊 Статистика:")
        print(f"   Время работы: {stats['runtime_seconds']:.0f} сек")
        print(f"   Всего сообщений: {stats['total_messages']}")
        print(f"   Уникальных самолётов: {stats['total_aircraft']}")
        
        receiver.stop()
    else:
        print("❌ Не удалось запустить приёмник")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
