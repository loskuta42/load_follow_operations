import numpy as np


def get_water_discarge(cb_beg, cb_end):
    """Масса жидкости, удаляемой из превого контура в результате водообмена
    cb_beg - начальное значение конентрации борной кислоты в 1 контуре
    cb_end - концентрация борной кислоты в 1 контуре на момент завершения подпитки"""
    V = 300  # м3
    Ro = 0.738  # т/м3
    mass = 0
    # c_podpit - концентрация борной кислоты на линии подпитки (0 или 40), г / кг
    if cb_beg < cb_end:
        # заливаем бор в зону
        c_podpit = 40
        delta = (c_podpit - cb_beg) / (c_podpit - cb_end)
        mass = V * Ro * np.log(delta)
        return mass
    if cb_beg > cb_end:
        # закачиваем в зону дистиллят
        c_podpit = 0
        delta = (c_podpit - cb_beg) / (c_podpit - cb_end)
        mass = V * Ro * np.log(delta)
        return mass

    return mass


def get_cost_by_power(w_nagruzka, w_current):
    """Потеря энерговыдработки
    w_nagruzka - мощность по графику несения нагрузки
    w_current - текущая мощность модели"""
    return abs(w_nagruzka - w_current)
