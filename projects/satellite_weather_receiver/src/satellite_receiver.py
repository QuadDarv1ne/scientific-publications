"""
Satellite Weather Image Receiver
Приём изображений с NOAA и Meteor M2 спутников

NOAA: 137 MHz (APT)
Meteor M2: 137.1 MHz (LRPT)
"""

import os
import subprocess
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import threading
import sys

logger = logging.getLogger(__name__)


class SatelliteReceiver:
    """
    Класс для приёма изображений с метеоспутников
    """
    
    # Частоты спутников
    SATELLITES = {
        'noaa15': {'name': 'NOAA 15', 'freq': 137.6200, 'mode': 'APT'},
        'noaa18': {'name': 'NOAA 18', 'freq': 137.9125, 'mode': 'APT'},
        'noaa19': {'name': 'NOAA 19', 'freq': 137.1000, 'mode': 'APT'},
        'meteor': {'name': 'Meteor M2', 'freq': 137.1000, 'mode': 'LRPT'},
    }
    
    def __init__(
        self,
        images_dir: str = "images",
        data_dir: str = "data",
        sample_rate: int = 48000,
        gain: int = 40
    ):
        """Инициализация приёмника"""
        self.images_dir = Path(images_dir)
        self.data_dir = Path(data_dir)
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.sample_rate = sample_rate
        self.gain = gain
        
        self.is_receiving = False
        self.process: Optional[subprocess.Popen] = None
        self.receive_thread: Optional[threading.Thread] = None
        
    def check_rtl_sdr(self) -> bool:
        """Проверка RTL-SDR"""
        try:
            result = subprocess.run(
                ['rtl_test', '-t'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def check_dependencies(self) -> List[str]:
        """Проверка зависимостей"""
        missing = []
        
        for cmd in ['rtl_fm', 'sox', 'predict']:
            if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
                missing.append(cmd)
                
        return missing
    
    def get_passes(self, satellite: str, lat: float = 55.75, lon: float = 37.61, 
                   days: int = 3) -> List[Dict]:
        """
        Получение информации о пролётах спутника
        
        Args:
            satellite: Имя спутника (noaa15, noaa18, etc.)
            lat: Широта
            lon: Долгота  
            days: Количество дней
        """
        passes = []
        
        try:
            # Используем predict для получения пролётов
            # predict -p "LAT LON" -q
            result = subprocess.run(
                ['predict', '-t', f'{lat},{lon}', '-h', str(satellite)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            dt = datetime.strptime(parts[0] + ' ' + parts[1], '%Y-%m-%d %H:%M:%S')
                            passes.append({
                                'time': dt,
                                'max_el': float(parts[2]) if len(parts) > 2 else 0,
                                'duration': int(parts[3]) if len(parts) > 3 else 0
                            })
                        except (ValueError, IndexError):
                            continue
                            
        except FileNotFoundError:
            logger.warning("predict не установлен")
        except Exception as e:
            logger.error(f"Ошибка получения пролётов: {e}")
            
        return passes[:days * 3]  # Ограничиваем количество
    
    def receive_apt(
        self,
        satellite: str = 'noaa18',
        duration: int = 300,
        freq: float = None
    ) -> Optional[str]:
        """
        Приём APT изображения с NOAA
        
        Args:
            satellite: Имя спутника
            duration: Длительность в секундах
            freq: Частота (если отличается от стандартной)
        """
        if not self.check_rtl_sdr():
            logger.error("RTL-SDR не найден")
            return None
            
        missing = self.check_dependencies()
        if missing:
            logger.error(f"Отсутствуют: {', '.join(missing)}")
            return None
        
        sat_info = self.SATELLITES.get(satellite, self.SATELLITES['noaa18'])
        if freq is None:
            freq = sat_info['freq']
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        wav_file = self.data_dir / f"{satellite}_{timestamp}.wav"
        png_file = self.images_dir / f"{satellite}_{timestamp}.png"
        
        logger.info(f"Приём {sat_info['name']} на частоте {freq} MHz")
        logger.info(f"Длительность: {duration} секунд")
        
        # Команда для записи APT сигнала
        # Используем rtl_fm с параметрами для APT
        cmd = [
            'rtl_fm',
            '-f', f'{freq}M',
            '-s', '11025',  # APT требует 11025 Hz
            '-g', str(self.gain),
            '-p', '0',
            '-E', 'deemp',
            '-E', 'lowpass',
            str(wav_file)
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.is_receiving = True
            logger.info("Запись началась...")
            
            time.sleep(duration)
            
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                
            self.is_receiving = False
            
            if wav_file.exists() and wav_file.stat().st_size > 1000:
                logger.info(f"WAV записан: {wav_file}")
                
                # Декодирование через sox (базовое)
                decoded = self._decode_apt(str(wav_file), str(png_file))
                if decoded:
                    return decoded
                    
                return str(wav_file)
                
        except Exception as e:
            logger.error(f"Ошибка приёма: {e}")
            if self.process:
                self.process.kill()
                
        return None
    
    def _decode_apt(self, wav_file: str, output_file: str) -> Optional[str]:
        """
        Декодирование APT изображения
        
        Примечание: Для полного декодирования используйте:
        - WXtoImg (Linux/Windows)
        - SDR# + Virtual Audio Cable
        """
        # Пробуем использовать sox для базовой обработки
        try:
            # Конвертируем в изображение (упрощённо)
            result = subprocess.run(
                ['sox', wav_file, '-r', '8000', '-t', 'raw', '-'],
                capture_output=True,
                timeout=60
            )
            
            logger.info("Создан WAV файл. Используйте WXtoImg для декодирования:")
            logger.info(f"  wxtoimg -m {wav_file}")
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка декодирования: {e}")
            return None
    
    def receive_meteor(self, duration: int = 180) -> Optional[str]:
        """
        Приём LRPT изображения с Meteor M2
        
        Требует: meteor_demod (входит в satellite-toolkit)
        """
        if not self.check_rtl_sdr():
            logger.error("RTL-SDR не найден")
            return None
            
        freq = self.SATELLITES['meteor']['freq']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_file = self.data_dir / f"meteor_{timestamp}.raw"
        
        logger.info(f"Приём Meteor M2 на частоте {freq} MHz")
        logger.info("Примечание: Для декодирования LRPT используйте meteor_demod")
        
        # Команда для записи
        cmd = [
            'rtl_fm',
            '-f', f'{freq}M',
            '-s', '288000',  # LRPT требует ~288 kHz
            '-g', str(self.gain),
            '-p', '0',
            str(raw_file)
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.is_receiving = True
            time.sleep(duration)
            
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                
            self.is_receiving = False
            
            if raw_file.exists():
                logger.info(f"Записано: {raw_file}")
                logger.info("Для декодирования используйте:")
                logger.info("  meteor_demod -s -o output.wav input.raw")
                return str(raw_file)
                
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            
        return None
    
    def start_monitoring(self, satellite: str = 'noaa18', callback=None) -> None:
        """
        Мониторинг пролётов спутника
        
        Args:
            satellite: Имя спутника
            callback: Функция обратного вызова
        """
        logger.info(f"Запуск мониторинга {satellite}")
        
        def monitor():
            while self.is_receiving:
                passes = self.get_passes(satellite)
                
                if passes:
                    next_pass = passes[0]
                    wait_time = (next_pass['time'] - datetime.now()).total_seconds() - 60
                    
                    if wait_time > 0:
                        logger.info(f"Следующий пролёт через {wait_time/60:.0f} мин")
                        time.sleep(min(wait_time, 300))
                    else:
                        # Запуск приёма
                        logger.info("Начало пролёта - запуск приёма")
                        
                        if callback:
                            callback(next_pass)
                            
                        self.receive_apt(satellite, duration=next_pass.get('duration', 300))
                
                time.sleep(60)
        
        self.receive_thread = threading.Thread(target=monitor, daemon=True)
        self.receive_thread.start()
    
    def stop(self):
        """Остановка приёмника"""
        self.is_receiving = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
    
    def list_images(self, limit: int = 10) -> List[str]:
        """Список принятых изображений"""
        images = []
        
        for ext in ['*.png', '*.jpg', '*.wav']:
            for f in sorted(self.images_dir.glob(ext), 
                          key=lambda x: x.stat().st_mtime, 
                          reverse=True):
                if f.stat().st_size > 0:
                    images.append(str(f))
                    if len(images) >= limit:
                        break
                        
        return images


def main():
    """Демонстрация работы"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Satellite Weather Receiver')
    parser.add_argument('--satellite', choices=['noaa15', 'noaa18', 'noaa19', 'meteor'],
                       default='noaa18', help='Спутник')
    parser.add_argument('--duration', type=int, default=300, help='Длительность (сек)')
    parser.add_argument('--freq', type=float, help='Частота (MHz)')
    parser.add_argument('--monitor', action='store_true', help='Мониторинг пролётов')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    receiver = SatelliteReceiver()
    
    print("=" * 50)
    print("SATELLITE WEATHER RECEIVER")
    print("=" * 50)
    
    if not receiver.check_rtl_sdr():
        print("❌ RTL-SDR не найден!")
        return 1
    
    missing = receiver.check_dependencies()
    if missing:
        print(f"⚠️ Отсутствуют: {', '.join(missing)}")
        print("   apt-get install rtl-sdr sox predict")
    
    sat_info = receiver.SATELLITES[args.satellite]
    print(f"✓ Готов к приёму {sat_info['name']}")
    print(f"  Частота: {args.freq or sat_info['freq']} MHz")
    print(f"  Режим: {sat_info['mode']}")
    print("=" * 50)
    
    if args.monitor:
        receiver.is_receiving = True
        receiver.start_monitoring(args.satellite)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nОстановка...")
            receiver.stop()
    else:
        if args.satellite == 'meteor':
            result = receiver.receive_meteor(duration=args.duration)
        else:
            result = receiver.receive_apt(args.satellite, args.duration, args.freq)
            
        if result:
            print(f"\n✓ Запись сохранена: {result}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
