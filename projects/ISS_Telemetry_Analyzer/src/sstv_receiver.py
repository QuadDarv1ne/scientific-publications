"""
SSTV Receiver Module for ISS Telemetry Analyzer
Приём изображений с МКС через SSTV (Slow Scan Television)

Частота МКС: 145.800 MHz FM (SSTV передачи)
"""

import os
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import threading
import signal
import sys

logger = logging.getLogger(__name__)


class SSTVReceiver:
    """
    Класс для приёма SSTV сигналов с МКС
    """
    
    # Частоты SSTV
    ISS_SSTV_FREQ = 145.800  # MHz
    ISS_APRS_FREQ = 145.825  # MHz
    
    # Стандарты SSTV
    SSTV_MODES = {
        'Robot': {'mode': 'Robot', 'time': 8},
        'Scottie': {'mode': 'Scottie1', 'time': 36},
        'Martin': {'mode': 'Martin1', 'time': 58},
    }
    
    def __init__(
        self,
        output_dir: str = "results/sstv",
        sample_rate: int = 48000,
        gain: int = 40,
        ppm_error: int = 0
    ):
        """
        Инициализация SSTV приёмника
        
        Args:
            output_dir: Директория для сохранения изображений
            sample_rate: Частота дискретизации
            gain: Усиление (дБ)
            ppm_error: Коррекция частоты (ppm)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.sample_rate = sample_rate
        self.gain = gain
        self.ppm_error = ppm_error
        
        self.is_receiving = False
        self.process: Optional[subprocess.Popen] = None
        self.receive_thread: Optional[threading.Thread] = None
        
    def check_rtl_sdr(self) -> bool:
        """Проверка наличия RTL-SDR и утилит"""
        try:
            # Проверка rtl_sdr
            result = subprocess.run(
                ['rtl_test', '-t'],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("RTL-SDR не найден или занят")
                return False
            return True
        except FileNotFoundError:
            logger.error("Утилиты rtl-sdr не установлены")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при проверке RTL-SDR")
            return False
    
    def check_dependencies(self) -> List[str]:
        """Проверка необходимых зависимостей"""
        missing = []
        
        # Проверка rtl_sdr
        if subprocess.run(['which', 'rtl_fm'], capture_output=True).returncode != 0:
            missing.append('rtl_fm (rtl-sdr-utils)')
            
        # Проверка sox
        if subprocess.run(['which', 'sox'], capture_output=True).returncode != 0:
            missing.append('sox')
            
        return missing
    
    def get_iss_passes(self, lat: float, lon: float) -> dict:
        """
        Получение информации о пролётах МКС
        (упрощённая версия - можно расширить)
        """
        try:
            import requests
            # API Open Notify для пролётов
            url = f"http://api.open-notify.org/iss-pass.json"
            params = {'lat': lat, 'lon': lon, 'n': 5}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                passes = []
                for p in data.get('response', []):
                    passes.append({
                        'duration': p.get('duration', 0),
                        'risetime': datetime.fromtimestamp(p.get('risetime', 0)),
                        'azimuth': p.get('azimuth', 0),
                        'altitude': p.get('altitude', 0)
                    })
                return {'status': 'success', 'passes': passes}
        except Exception as e:
            logger.error(f"Ошибка получения пролётов: {e}")
            
        return {'status': 'error', 'message': 'Не удалось получить данные о пролётах'}
    
    def receive_sstv(
        self,
        duration: int = 120,
        freq: float = ISS_SSTV_FREQ,
        use_pipe: bool = True
    ) -> Optional[str]:
        """
        Приём SSTV сигнала с МКС
        
        Args:
            duration: Длительность приёма в секундах
            freq: Частота в MHz
            use_pipe: Использовать pipe для прямой записи
            
        Returns:
            Путь к записанному файлу или None
        """
        if not self.check_rtl_sdr():
            logger.error("RTL-SDR не доступен")
            return None
            
        missing = self.check_dependencies()
        if missing:
            logger.error(f"Отсутствуют зависимости: {', '.join(missing)}")
            logger.info("Установите: sudo apt-get install rtl-sdr sox")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"iss_sstv_{timestamp}.wav"
        
        logger.info(f"Начало приёма SSTV на частоте {freq} MHz")
        logger.info(f"Длительность: {duration} секунд")
        logger.info(f"Ожидаемое время передачи SSTV: 60-120 секунд")
        
        # Команда rtl_fm для записи FM сигнала
        cmd = [
            'rtl_fm',
            '-f', f'{freq}M',
            '-s', str(self.sample_rate),
            '-g', str(self.gain),
            '-p', str(self.ppm_error),
            '-E', 'deemp',  # FM de-emphasis
            '-w', str(15000),  # Фильтр 15kHz
            str(output_file)
        ]
        
        try:
            # Запускаем rtl_fm в фоне
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.is_receiving = True
            
            # Ждём указанное время
            logger.info(f"Приём начат. Ожидание {duration} секунд...")
            time.sleep(duration)
            
            # Останавливаем процесс
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                
            self.is_receiving = False
            
            if output_file.exists() and output_file.stat().st_size > 0:
                logger.info(f"Сигнал записан: {output_file}")
                
                # Пытаемся декодировать
                decoded = self.decode_sstv(str(output_file))
                if decoded:
                    return decoded
                    
                return str(output_file)
            else:
                logger.warning("Файл не создан или пуст")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при записи")
            if self.process:
                self.process.kill()
            return None
        except Exception as e:
            logger.error(f"Ошибка приёма: {e}")
            return None
    
    def decode_sstv(self, wav_file: str) -> Optional[str]:
        """
        Декодирование SSTV изображения
        
        Требует установки: sudo apt-get install qsstv или использовать RX-SSTV
        
        Args:
            wav_file: Путь к WAV файлу
            
        Returns:
            Путь к декодированному изображению
        """
        # Пробуем использовать rx_sstv если установлен
        try:
            result = subprocess.run(
                ['rx_sstv', '-o', str(self.output_dir), wav_file],
                capture_output=True,
                timeout=120
            )
            if result.returncode == 0:
                # Ищем созданное изображение
                for f in self.output_dir.glob("*.png"):
                    return str(f)
        except FileNotFoundError:
            logger.info("rx_sstv не установлен. Для декодирования используйте RX-SSTV или QSSTV")
        except subprocess.TimeoutExpired:
            logger.warning("Таймаут при декодировании")
            
        return None
    
    def start_monitoring(
        self,
        interval: int = 300,
        callback=None
    ) -> None:
        """
        Запуск мониторинга пролётов МКС
        
        Args:
            interval: Интервал проверки в секундах
            callback: Функция обратного вызова при обнаружении передачи
        """
        logger.info(f"Запуск мониторинга SSTV (интервал: {interval} сек)")
        
        def monitor():
            last_pass_time = None
            
            while self.is_receiving:
                # Проверяем пролёты (используем координаты по умолчанию - Москва)
                passes_info = self.get_iss_passes(55.7558, 37.6173)
                
                if passes_info['status'] == 'success' and passes_info.get('passes'):
                    next_pass = passes_info['passes'][0]
                    pass_time = next_pass['risetime']
                    
                    # Если начался новый пролёт
                    if pass_time != last_pass_time:
                        last_pass_time = pass_time
                        
                        logger.info(f"Следующий пролёт МКС: {pass_time}")
                        logger.info(f"Продолжительность: {next_pass['duration']} сек")
                        
                        # Вызываем callback если передан
                        if callback:
                            callback(next_pass)
                            
                        # Запускаем приём за 30 секунд до пролёта
                        wait_time = (pass_time - datetime.now()).total_seconds() - 30
                        if wait_time > 0:
                            logger.info(f"Ожидание начала пролёта: {wait_time} сек")
                            time.sleep(wait_time)
                            
                        # Запускаем приём
                        self.receive_sstv(duration=next_pass['duration'] + 60)
                
                time.sleep(interval)
        
        self.receive_thread = threading.Thread(target=monitor, daemon=True)
        self.receive_thread.start()
    
    def stop(self) -> None:
        """Остановка приёма"""
        self.is_receiving = False
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                
        logger.info("Приём SSTV остановлен")
    
    def get_recent_images(self, limit: int = 10) -> List[str]:
        """Получение списка недавних изображений"""
        images = []
        
        for f in sorted(self.output_dir.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.stat().st_size > 0:
                images.append(str(f))
                if len(images) >= limit:
                    break
                    
        return images


def main():
    """Демонстрация работы SSTV приёмника"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SSTV Receiver for ISS')
    parser.add_argument('--duration', type=int, default=120, help='Длительность приёма в секундах')
    parser.add_argument('--freq', type=float, default=145.800, help='Частота в MHz')
    parser.add_argument('--monitor', action='store_true', help='Запуск мониторинга пролётов')
    parser.add_argument('--gain', type=int, default=40, help='Усиление в dB')
    
    args = parser.parse_args()
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    receiver = SSTVReceiver(gain=args.gain)
    
    # Проверка оборудования
    print("=" * 50)
    print("Проверка SSTV приёмника")
    print("=" * 50)
    
    if not receiver.check_rtl_sdr():
        print("❌ RTL-SDR не найден!")
        print("   Установите: sudo apt-get install rtl-sdr")
        return 1
        
    missing = receiver.check_dependencies()
    if missing:
        print(f"⚠️ Отсутствуют зависимости: {', '.join(missing)}")
        print("   Установите: sudo apt-get install rtl-sdr-utils sox")
    
    print("✓ RTL-SDR готов к работе")
    print(f"  Частота: {args.freq} MHz")
    print(f"  Усиление: {args.gain} dB")
    print("=" * 50)
    
    # Запуск
    if args.monitor:
        receiver.is_receiving = True
        try:
            receiver.start_monitoring(interval=300)
            # Ожидаем Ctrl+C
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nОстановка...")
            receiver.stop()
    else:
        result = receiver.receive_sstv(duration=args.duration, freq=args.freq)
        if result:
            print(f"\n✓ Запись сохранена: {result}")
            print("  Для декодирования используйте RX-SSTV или QSSTV")
        else:
            print("\n❌ Приём не удался")
            return 1
            
    return 0


if __name__ == '__main__':
    sys.exit(main())
