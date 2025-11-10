"""
Основные функции для построения графиков.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List, Dict
from astropy.time import Time
from heliopy.events.flare_detector import Flare
from heliopy.events.cme_detector import CME


class Plotter:
    """Класс для построения графиков."""
    
    def __init__(self):
        """Инициализация построителя графиков."""
        pass
    
    @staticmethod
    def plot_time_series(time: np.ndarray,
                        data: np.ndarray,
                        xlabel: str = 'Time',
                        ylabel: str = 'Value',
                        title: Optional[str] = None,
                        save_path: Optional[str] = None,
                        **kwargs) -> plt.Figure:
        """
        Построение графика временного ряда.
        
        Parameters
        ----------
        time : array
            Временные метки.
        data : array
            Данные.
        xlabel, ylabel : str
            Подписи осей.
        title : str, optional
            Заголовок.
        save_path : str, optional
            Путь для сохранения.
        **kwargs
            Дополнительные параметры для matplotlib.
        
        Returns
        -------
        Figure
            Объект matplotlib Figure.
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(time, data, **kwargs)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        if title:
            ax.set_title(title, fontsize=14)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    @staticmethod
    def plot_flare_lightcurve(goes_data, flares: List[Flare],
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Построение кривой блеска вспышек.
        
        Parameters
        ----------
        goes_data : GOESData
            Данные GOES.
        flares : list
            Список вспышек.
        save_path : str, optional
            Путь для сохранения.
        
        Returns
        -------
        Figure
            Объект matplotlib Figure.
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Построение данных GOES
        if len(goes_data.xrsb) > 0:
            ax.plot(goes_data.time, goes_data.xrsb, label='XRS-B', linewidth=1.5)
        
        # Отметка вспышек
        for flare in flares:
            ax.axvline(flare.peak_time.datetime, color='red', linestyle='--', alpha=0.7)
            ax.text(flare.peak_time.datetime, ax.get_ylim()[1] * 0.9,
                   f"{flare.class_}", rotation=90, ha='right', va='top')
        
        ax.set_yscale('log')
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('X-ray Flux (W/m²)', fontsize=12)
        ax.set_title('GOES X-ray Flux and Detected Flares', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    @staticmethod
    def plot_cme_trajectory(cme: CME,
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        Построение траектории CME.
        
        Parameters
        ----------
        cme : CME
            Объект CME.
        save_path : str, optional
            Путь для сохранения.
        
        Returns
        -------
        Figure
            Объект matplotlib Figure.
        """
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Упрощенная визуализация траектории
        if cme.trajectory:
            r = [point[0] for point in cme.trajectory]
            theta = [point[1] for point in cme.trajectory]
            ax.plot(theta, r, 'b-', linewidth=2, label='CME Trajectory')
        
        # Направление CME
        direction_rad = np.radians(cme.direction['lon'])
        ax.arrow(direction_rad, 0.5, 0, 0.3, head_width=0.1, head_length=0.1,
                fc='red', ec='red', label='CME Direction')
        
        ax.set_title(f'CME Trajectory\nSpeed: {cme.speed:.1f} km/s', fontsize=14)
        ax.legend()
        ax.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig

