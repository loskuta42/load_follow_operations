"""задача этого файла - набор данных для создания базиса главных компонент для данного состояния реактора"""
import numpy as np
from xe_iod_save import save_xen_jod
from set_state import set_state_param, wt
from mc2py.zgiw import *
from random import random


def generate_different_states(h5_filename="data_for_bgk.h5"):
    """Создание всевозможных состояний установки"""
    soc = getv()
    # soc = Tscript_drv("tcp://localhost:5555")
    for isamp in range(60):  # 60
        power = 3200 * (0.5 + 0.5 * (np.cos(isamp) + 1) / 2)
        h_suz_oe = 1.03 * np.ones(12)
        h_suz_oe[-1] = 0.9
        h_suz_oe = np.array(h_suz_oe)
        set_state_param(soc=soc, power=power, h_suz=h_suz_oe, g=87200, temp=296.2, p_nad_az=164)

        save_xen_jod(h5_filename, YMFAST=1)

        # начнем поле с помощью ор суз,
        # чтобы получить неравновесный Xe
        h_suz_oe = 1.03 * np.ones(12)
        h_suz_oe[-1] = 0.9 * (np.cos(2.718281828 * isamp / 2) + 1) / 2
        # h_suz_oe[-1] = random()*1.03
        h_suz_oe[-2] = random() * 1.03
        h_suz_oe = np.array(h_suz_oe)
        soc["#YS#YSHGRP"] = h_suz_oe  # положения групп СУЗ
        # soc["YSHGRPSM"] = h_suz_oe  # положения групп СУЗ
        soc.step(10)
        print("isamp", isamp, "Power: ", power, " hgrp 12 ", h_suz_oe[-1], " hgrp 11 ", h_suz_oe[-2])

        for ind in range(7):  # 7
            save_xen_jod(h5_filename, YMFAST=60)
            wt(600)
            print("isamp", isamp, ind)

    print("Done xe jod AO Rp Zpn den collecting")


if __name__ == "__main__":
    generate_different_states(h5_filename="data_for_bgk.h5")
