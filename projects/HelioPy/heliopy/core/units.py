"""
Специализированные единицы измерения для гелиофизики.
"""

from astropy import units as u
from astropy.units import def_unit


# Определение специализированных единиц
# Солнечные единицы
solar_radius = u.def_unit('R_sun', 6.957e8 * u.m, doc='Solar radius')
solar_mass = u.def_unit('M_sun', 1.989e30 * u.kg, doc='Solar mass')
solar_luminosity = u.def_unit('L_sun', 3.828e26 * u.W, doc='Solar luminosity')

# Астрономические единицы
au = u.def_unit('AU', 1.496e11 * u.m, doc='Astronomical Unit')

# Единицы для космической погоды
# Индексы геомагнитной активности (безразмерные)
kp_index = u.def_unit('Kp', doc='Kp index')
dst_index = u.def_unit('nT', doc='Dst index in nanotesla')

# Единицы для солнечного ветра
proton_flux = u.def_unit('pfu', 1.0 / (u.cm**2 * u.s * u.sr), doc='Proton flux unit')


class SolarUnits:
    """Класс для работы с солнечными единицами измерения."""
    
    # Солнечные единицы
    R_sun = solar_radius
    M_sun = solar_mass
    L_sun = solar_luminosity
    
    # Астрономические единицы
    AU = au
    
    # Единицы для космической погоды
    Kp = kp_index
    nT = dst_index
    pfu = proton_flux
    
    @staticmethod
    def to_solar_radius(distance: u.Quantity) -> u.Quantity:
        """
        Преобразование расстояния в солнечные радиусы.
        
        Parameters
        ----------
        distance : Quantity
            Расстояние в любых единицах.
        
        Returns
        -------
        Quantity
            Расстояние в солнечных радиусах.
        """
        return distance.to(solar_radius)
    
    @staticmethod
    def to_au(distance: u.Quantity) -> u.Quantity:
        """
        Преобразование расстояния в астрономические единицы.
        
        Parameters
        ----------
        distance : Quantity
            Расстояние в любых единицах.
        
        Returns
        -------
        Quantity
            Расстояние в астрономических единицах.
        """
        return distance.to(au)
    
    @staticmethod
    def solar_radius_to_km(radius: u.Quantity) -> u.Quantity:
        """
        Преобразование солнечных радиусов в километры.
        
        Parameters
        ----------
        radius : Quantity
            Радиус в солнечных радиусах.
        
        Returns
        -------
        Quantity
            Радиус в километрах.
        """
        return radius.to(u.km)

