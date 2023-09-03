from mc2py.zgiw import *
import numpy as np


def set_state(plant_name = "kaln",blk=3,kamp=1,teff=1):
    soc = getv()
    #soc = Tscript_drv("tcp://localhost:5555")
    for step, letter in enumerate( plant_name[:4] ):
        soc.plant_name[step]= letter

    print("input ", kamp,teff)
    # обрабатываем исключительную ситуацию, когда номер произошла течь в кассете и перегрузка внутри кампании
    # в мфа кампания разбита на две части
    if plant_name == "kaln" and blk == 3:
        if (kamp == 1 and  96.58 < teff) or kamp>1 :
            kamp = kamp + 1
            if kamp == 2:
                teff = teff - 96.58      
    print("output ", kamp,teff)

    soc.syncro(1)
    if (soc.YMFLAG_NKS==0):
        soc.YZKEYLINK2 = 0 #НКС
    soc.step(2)

    soc.YMBLOCKNUMBER_TO_LOAD = blk
    soc.step(2)
    print ("1")
    soc.YM_N_KAMP_TO_LOAD = kamp

    soc.YMINTPOW_SET = 100   # мощность
    soc.YMWSTATN = 100
    soc.step(4)
    soc.YM_STROBE_POWSET = 1 # ввод показаний мощности
    soc.step(4)

    print ("3")
    soc.YMFLAGSTAT = 1 # статика
    soc.step(2)
    print ("4")
    soc.YZBORREG = 1 # борный регулятор
    soc.step(2)
    print ("5")
    soc.YZBORMODE = 2 # автомат по бору
    soc.step(4)
    print ("6")
    soc.YM_XIPI_LDBRNBEG = 1
    soc.step(50)
    print ("7")
    soc.YZBORMODE = 2
    soc.YM_N_KAMP_END = -1
    soc.step(50)
    print ("8")

    # выгорание по графику несения нагрузки
#    soc.YM_XIPI_GLBSIM = 1
#    soc.YMMAXDT_BURNSIM = 30000
#    soc.ym_autostpsize_flag = 3
#    soc.step(4)
#    print ("9")
#    while float(soc.YMTIME_BRN) < teff:
#        soc.step(1)

    print ("10")
    soc.YM_XIPI_GLBSIM = 0 # выгорание по данным АЭС
    soc.step(20)
    soc.syncro(0)


    xen = soc.YMRO_XEN
    jod = soc.YMRO_JOD

    print ("done burn")

def set_state_param(soc = getv(), power=3200,h_suz=1.03*np.ones(12),g=87200,temp=296.2,p_nad_az=164):
    """Установка параметров активной зоны
    power мощность, МВт
    h_suz положения групп суз, %
    g расчход через зону, м3/ч
    temp температура на входе, С
    p_nad_az давление над зоной, кгс/см2
    """
    soc.YMFAST =1 # ускорение расчета модели зоны

    if (soc.YMFLAG_NKS==0):
        soc.YZKEYLINK2 = 0 #НКС
    soc.step(1)
    soc["#YM#YMFLAGSTAT"] = 1 # статика
    soc.step(1)
    soc.YZBORREG = 1 # борный регулятор
    soc.step(1)
    soc.YZBORMODE = 2 # автомат по бору
    soc.step(1)

    soc.Pzona_pr= p_nad_az # давление над АЗ
    soc.step(1)
    soc.YMGMIX_IN_INPUT = g #расход через АЗ
    soc.step(1)
    soc.YMGMIX_IN_INPUT_USE = 1
    soc.step(4)
    soc.YMTMIX_IN_INPUT = temp # температура на входе в зону
    soc.step(1)
    soc.YMTMIX_IN_INPUT_USE = 1 # ввод положения в АЗ
    soc.step(8)
    soc.YZREGRPINS_KEY = 1 # ввод положения групп в процентах
    soc.step(10)
    h_suz_oe = np.array(h_suz)
    soc["#YS#YSHGRP"] = h_suz_oe # положения групп СУЗ
    soc.step(10)

    # установка мощности
    power_proc  = power/ float(soc.YMWNOM) * 1.e8
    soc.YMINTPOW_SET = power_proc   # мощность
    soc.YMWSTATN = power_proc
    soc.step(4)
    soc.YM_STROBE_POWSET = 1 # ввод показаний мощности
    soc.step(10)

    soc.YZBORREG = 1 # борный регулятор
    soc.step(4)
    soc.YZBORMODE = 2 # автомат по бору
    soc.step(50)

    soc["#YM#YMFLAGSTAT"] = 0  # статика
    soc.step(2)
    print ("done set suz and temp")


def wt(nstep = 1):
    """сохранение данных для создание xe jod базиса"""
    soc = getv()
    soc.step(nstep)


if __name__ == "__main__": 
    #set_state(plant_name = "kaln",blk=4,kamp=1,teff=1)
    set_state_param(power=3200,h_suz=1.03*np.ones(12),g=87200,temp=296.2,p_nad_az=164)
    #print (field1)

