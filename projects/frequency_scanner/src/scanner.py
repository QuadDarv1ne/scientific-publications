"""
Frequency Scanner and Spectrum Analyzer
Сканер радиочастот и анализатор спектра

Использует RTL-SDR для сканирования эфира
"""

import os
import subprocess
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import threading
import sys
import numpy as np

logger = logging.getLogger(__name__)


class FrequencyScanner:
    """
    Класс для сканирования частот и анализа спектра
    """
    
    # Диапазоны частот
    BANDS = {
        'fm': (88, 108, 'FM радио'),
        'air': (108, 136, 'Авиация'),
        'vhf': (136, 174, 'VHF'),
        'uhf': (400, 470, 'UHF'),
        'pmr': (446, 446, 'PMR'),
        'lpd': (433, 433, 'LPD'),
        'ism': (433, 435, 'ISM'),
        'noaa': (137, 138, 'NOAA'),
        'meteo': (168, 170, 'Метео'),
    }
    
    def __init__(
        self,
        results_dir: str = "results",
        data_dir: str = "data",
        gain: int = 40,
        sample_rate: int = 2400000
    ):
        """Инициализация сканера"""
        self.results_dir = Path(results_dir)
        self.data_dir = Path(data_dir)
        
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.gain = gain
        self.sample_rate = sample_rate
        
        self.is_scanning = False
        self.detected_frequencies: List[Dict] = []
        
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
    
    def scan_range(
        self,
        start_mhz: float,
        end_mhz: float,
        step_mhz: float = 1.0,
        dwell_seconds: float = 0.5
    ) -> List[Dict]:
        """
        Сканирование диапазона частот
        
        Args:
            start_mhz: Начальная частота (MHz)
            end_mhz: Конечная частота (MHz)
            step_mhz: Шаг сканирования (MHz)
            dwell_seconds: Время задержки на каждой частоте
            
        Returns:
            Список обнаруженных частот с уровнями
        """
        if not self.check_rtl_sdr():
            logger.error("RTL-SDR не найден")
            return []
        
        logger.info(f"Сканирование: {start_mhz}-{end_mhz} MHz")
        
        self.detected_frequencies = []
        self.is_scanning = True
        
        current_mhz = start_mhz
        scan_points = []
        
        while current_mhz <= end_mhz and self.is_scanning:
            # Пробуем получить уровень сигнала
            level = self._measure_signal_level(current_mhz)
            
            if level > -50:  # Порог обнаружения
                self.detected_frequencies.append({
                    'frequency': current_mhz,
                    'level': level,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"  Обнаружено: {current_mhz:.3f} MHz ({level:.1f} dB)")
            
            scan_points.append({
                'frequency': current_mhz,
                'level': level
            })
            
            current_mhz += step_mhz
            time.sleep(dwell_seconds)
        
        self.is_scanning = False
        
        # Сохраняем результаты
        self._save_scan_results(scan_points)
        
        logger.info(f"Сканирование завершено. Найдено: {len(self.detected_frequencies)} частот")
        
        return self.detected_frequencies
    
    def _measure_signal_level(self, freq_mhz: float) -> float:
        """
        Измерение уровня сигнала на частоте
        
        Использует rtl_power для быстрого измерения
        """
        try:
            # Используем rtl_power для измерения
            cmd = [
                'rtl_power',
                '-f', f'{freq_mhz}M',
                '-d', '0',
                '-g', str(self.gain),
                '-i', '1',
                '-1',  # Одиночное измерение
                '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=3,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                # Парсим вывод rtl_power
                # Формат: freq,time,db,db,db...
                lines = result.stdout.strip().split('\n')
                if lines:
                    # Берем среднее значение
                    values = []
                    for line in lines[1:]:  # Пропускаем заголовок
                        parts = line.split(',')
                        if len(parts) >= 4:
                            try:
                                db_values = [float(x) for x in parts[3:] if x]
                                if db_values:
                                    values.append(np.mean(db_values))
                            except ValueError:
                                continue
                    
                    if values:
                        return float(np.mean(values))
                        
        except Exception as e:
            logger.debug(f"Ошибка измерения {freq_mhz} MHz: {e}")
        
        return -100  # Нет сигнала
    
    def scan_preset(self, preset: str = 'all', dwell: float = 0.3) -> List[Dict]:
        """
        Сканирование предустановленного диапазона
        
        Args:
            preset: Имя предустановки ('all', 'fm', 'air', etc.)
            dwell: Время задержки
        """
        results = []
        
        if preset == 'all':
            bands = self.BANDS.keys()
        else:
            bands = [preset]
            
        for band in bands:
            if band in self.BANDS:
                start, end, name = self.BANDS[band]
                logger.info(f"Сканирование: {name} ({start}-{end} MHz)")
                
                results.extend(
                    self.scan_range(start, end, step_mhz=0.5, dwell_seconds=dwell)
                )
        
        return results
    
    def record_frequency(
        self,
        freq_mhz: float,
        duration: int = 30,
        output_format: str = 'wav'
    ) -> Optional[str]:
        """
        Запись сигнала с конкретной частоты
        
        Args:
            freq_mhz: Частота в MHz
            duration: Длительность в секундах
            output_format: Формат (wav, raw, iq)
        """
        if not self.check_rtl_sdr():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == 'wav':
            output_file = self.data_dir / f"rec_{freq_mhz}_{timestamp}.wav"
            cmd = [
                'rtl_fm',
                '-f', f'{freq_mhz}M',
                '-s', '48000',
                '-g', str(self.gain),
                '-E', 'deemp',
                str(output_file)
            ]
        elif output_format == 'iq':
            output_file = self.data_dir / f"rec_{freq_mhz}_{timestamp}.iq"
            cmd = [
                'rtl_sdr',
                '-f', f'{freq_mhz}M',
                '-s', str(self.sample_rate),
                '-g', str(self.gain),
                '-',  # stdout
            ]
            # Для IQ нужно перенаправление в файл
            cmd = None  # Реализация требует доп. обработки
        else:
            output_file = self.data_dir / f"rec_{freq_mhz}_{timestamp}.raw"
            cmd = [
                'rtl_fm',
                '-f', f'{freq_mhz}M',
                '-s', str(self.sample_rate),
                '-g', str(self.gain),
                str(output_file)
            ]
        
        if cmd:
            try:
                logger.info(f"Запись {freq_mhz} MHz ({duration} сек)...")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                time.sleep(duration)
                process.terminate()
                process.wait(timeout=5)
                
                if output_file.exists():
                    logger.info(f"Записано: {output_file}")
                    return str(output_file)
                    
            except Exception as e:
                logger.error(f"Ошибка записи: {e}")
                
        return None
    
    def get_scanner_summary(self) -> Dict:
        """Получить краткую информацию о сканере"""
        return {
            'available_bands': list(self.BANDS.keys()),
            'gain': self.gain,
            'sample_rate': self.sample_rate,
            'rtl_sdr_connected': self.check_rtl_sdr()
        }
    
    def _save_scan_results(self, data: List[Dict]) -> str:
        """Сохранение результатов сканирования"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"scan_{timestamp}.json"
        
        result = {
            'timestamp': timestamp,
            'scan_data': data,
            'detected_count': len(self.detected_frequencies),
            'detected_frequencies': self.detected_frequencies
        }
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        logger.info(f"Результаты сохранены: {output_file}")
        return str(output_file)
    
    def stop(self):
        """Остановка сканирования"""
        self.is_scanning = False


def main():
    """Демонстрация работы"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Frequency Scanner')
    parser.add_argument('--range', nargs=2, type=float, metavar=('START', 'END'),
                       help='Диапазон в MHz')
    parser.add_argument('--freq', type=float, help='Конкретная частота')
    parser.add_argument('--duration', type=int, default=30, help='Длительность записи')
    parser.add_argument('--preset', choices=['all', 'fm', 'air', 'vhf', 'uhf', 'pmr', 'lpd'],
                       help='Предустановленный диапазон')
    parser.add_argument('--band', action='store_true', help='Показать доступные диапазоны')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    scanner = FrequencyScanner()
    
    print("=" * 50)
    print("FREQUENCY SCANNER")
    print("=" * 50)
    
    if args.band:
        print("\nДоступные диапазоны:")
        for name, (start, end, desc) in scanner.BANDS.items():
            print(f"  {name:8s}: {start:3.0f}-{end:3.0f} MHz  ({desc})")
        return 0
    
    if not scanner.check_rtl_sdr():
        print("❌ RTL-SDR не найден!")
        return 1
    
    print("✓ RTL-SDR готов")
    print("=" * 50)
    
    if args.range:
        start, end = args.range
        scanner.scan_range(start, end)
        
    elif args.preset:
        scanner.scan_preset(args.preset)
        
    elif args.freq:
        scanner.record_frequency(args.freq, args.duration)
        
    else:
        print("Используйте:")
        print("  --range 88 108      # Сканирование диапазона")
        print("  --preset fm        # FM диапазон")
        print("  --freq 145.800     # Запись частоты")
        print("  --band             # Показать диапазоны")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
