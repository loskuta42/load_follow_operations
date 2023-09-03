from mc2py.zgiw import *
import h5py  # HDF5 support
import numpy as np
from mc2py.h5buf import H5membuf
import matplotlib.pyplot as plt

def load_proection_data_from_hdf5(fileName_bgk, xe_dimension, jod_dimension):
    u""" Функция для перевода данных из HDF5 в xen, jod"""
    # Открываем файл
    with h5py.File(fileName_bgk, "a" ) as f5:
            xen_bgk = f5["xen_bgk{}".format(xe_dimension)][:]
            jod_bgk = f5["jod_bgk{}".format(jod_dimension)][:]
            w_bgk = f5["w_bgk"][:]
            cbor_bgk = f5["cbor_bgk"][:]
            temp_bgk = f5["temp_bgk"][:]
            hgrp_bgk = f5["hgrp_bgk"][:]
            AO_bgk = f5["AO_bgk"][:]


    return xen_bgk, jod_bgk, w_bgk, cbor_bgk, temp_bgk, hgrp_bgk, AO_bgk

def load_initial_data_from_hdf5(fileName):
    # Открываем файл
    with h5py.File(fileName , "a" ) as f5:
        # переберем все поля в hdf5
        xen = f5["xen"][:]
        jod = f5["jod"][:]
        w = f5["w"][:]
        cbor = f5["cbor"][:]
        temp = f5["temp"][:]
        hgrp = f5["hgrp"][:]
        AO_before=f5["AO"][:]

        return xen, jod, w, cbor, temp, hgrp ,AO_before

def insert_bgk_params_in_model(fileName, fileName_bgk, nstate,xe_dimension, jod_dimension, YMFAST=1):
    """вставим данные из БГК в модель"""
    xen, jod, w, cbor, temp, hgrp,AO_before = load_initial_data_from_hdf5(fileName)
    xen_bgk, jod_bgk, w_bgk, cbor_bgk, temp_bgk, hgrp_bgk, AO_bgk= load_proection_data_from_hdf5(fileName_bgk, xe_dimension=xe_dimension,
                                                                                                 jod_dimension=jod_dimension)

    # укорачиваем набор для построения БГК
    #xen_short=xen[:200]
    #jod_short=jod[:200]
    #w_short = w[:200]
    #cbor_short = cbor[:200]
    #temp_short = temp[:200]
    #hgrp_short = hgrp[:200]

    # soc = Tscript_drv("tcp://localhost:5555")
    # soc = getv()
    # soc.YMFAST = YMFAST
    # soc.step(4)
    # soc.ymflag_xecalc=1
    # soc["#YM#YMFLAGSTAT"]=1
    # soc.YZBORMODE=2
    # soc.step(4)
    #
    # w_before_insertion_lst=[]
    # w_after_insertion_lst=[]
    # offset_before_insertion = []
    # offset_after_insertion=[]
    #
    # for state_index in range(nstate):
    #     w_from_h5 = w_bgk[0][state_index]
    #
    #     soc["#YM#YMFLAGSTAT"] = 1
    #     soc.step(4)
    #     soc.YZBORMODE = 2
    #     soc.step(4)
    #     soc.ymflag_xecalc = 1
    #     soc.step(4)
    #     soc["YSHGRP"] = hgrp_bgk[0][state_index]
    #     soc.YMTMIX_IN_INPUT = temp_bgk[0][state_index]
    #     soc.step(4)
    #     soc.YMINTPOW_SET = w_from_h5  # мощность
    #     soc.YMWSTATN = w_from_h5
    #     soc.step(4)
    #     soc.YM_STROBE_POWSET = 1  # ввод показаний мощности
    #     soc.step(10)
    #     soc["#YM#YMFLAGSTAT"] = 1
    #     soc.YZBORMODE = 2
    #     soc.step(4)
    #     soc.ymflag_xecalc=0
    #     soc.step(4)
    #     soc["#YM#YMRO_XEN"] = xen[state_index]
    #     soc["#YM#YMRO_JOD"] = jod[state_index]
    #     soc.step(100)
    #
    #
    #     w_curr = float(soc.YMINTPOW)
    #     w_up = w_curr + 1
    #     w_dn = w_curr - 1
    #     if (  w_from_h5 < w_dn or w_up < w_from_h5):
    #         print ("ОШИБКА: состояние {} YMINTPOW {} w_from_file {}".format(state_index, w_curr, w_from_h5 ))
    #
    #     soc["#YM#YMFLAGSTAT"] = 0  # отключена статика
    #     soc.YZBORMODE = 1 # бор в дистанции
    #     soc.ymflag_xecalc = 0  # перестаем считать XE
    #     soc.step(4)
    #     soc["#YM#YMRO_XEN"] = xen_bgk[0][state_index]
    #     soc["#YM#YMRO_JOD"] = jod_bgk[0][state_index]
    #     soc.step(50)
    #
    #     AO=float(soc.ymoffset)
    #     w = float(soc.YMINTPOW)
    #     w_up = w + 1
    #     w_dn = w - 1
    #     if ( w_from_h5< w_dn or  w_up< w_from_h5):
    #         print ("Расхождение: состояние {} YMINTPOW {} w_from_file {}".format(state_index, w, w_from_h5 ))
    #
    #     w_before_insertion_lst.append(w_from_h5)
    #     offset_before_insertion.append(AO_bgk[0][state_index])
    #
    #     w_after_insertion_lst.append(w)
    #     offset_after_insertion.append(AO)
    #     print ("state_index {}".format(state_index))
    #
    # return w_after_insertion_lst, w_before_insertion_lst,offset_after_insertion ,offset_before_insertion

if __name__ == "__main__":
    jod_dimension = 5 #5
    xe_dimension = 4 #6
    fileName = r"D:\Projects\bober\БГК_VVER1200\data.h5\xen_jod_AO_Rp_Zpn_den.h5"
    fileName_bgk = r"D:\Projects\bober\БГК_VVER1200\data.h5\xen_jod_AO_Rp_Zpn_bgk_den.h5"
    # fname = "power_results_jod{}_xen{}.txt".format(jod_dimension, xe_dimension)
    fname = r"D:\Projects\bober\БГК_VVER1200\data.txt\power_results_300v_jod5_xen4.txt"
    nstate= 300 #200
    # w_after_insertion_lst, w_bgk,offset_after_insertion,offset_before_insertion = insert_bgk_params_in_model(fileName,fileName_bgk, nstate, xe_dimension, jod_dimension)
    # np.savetxt(fname, [w_after_insertion_lst, w_bgk,offset_after_insertion,offset_before_insertion])

    res =np.loadtxt(fname)
    w_after_insertion_lst = res[0]
    w_bgk=res[1]
    offset_after_insertion=res[2]
    offset_before_insertion=res[3]
    state_index=np.arange(nstate)

    font = {'family': 'serif', 'color': 'black', 'weight': 'normal', 'size': 14, }
    fig, ax1 = plt.subplots()
    ax1.plot(state_index, w_bgk,'r',label="Initial power")
    ax1.plot(state_index, w_after_insertion_lst, 'g--', label="Reproduced power(Iod/POD:{}, Xe/POD:{})".format(jod_dimension, xe_dimension))
    lgnd = ax1.legend(loc='upper right', shadow=False)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.xlabel("State number (vector number)",fontdict=font)
    plt.ylabel("Power (W), %",fontdict=font)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(45, 115)
    main= np.array(w_bgk)
    delta_plus= main + 1
    delta_minus = main - 1
    #ax1.plot(state_index, delta_plus, 'y', label="Ограничение сверху")
    #ax1.plot(state_index, delta_minus, 'm', label = "Ограничение снизу")
    plt.legend()
    # plt.grid(True)
    # plt.savefig('power_line{}_jod{}_xen{}.png'.format(nstate,jod_dimension, xe_dimension))
    plt.show()

    fig, ax1 = plt.subplots()
    ax1.plot(state_index, 100*(w_bgk-w_after_insertion_lst)/w_after_insertion_lst, 'r')
    lgnd = ax1.legend(loc='upper right', shadow=False)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.xlabel("State number (vector number)", fontdict=font)
    plt.ylabel(r'$\frac{\Delta {W}}{ {W}}$, %', fontdict=font)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(-2,2)
    # ax1.plot(state_index, delta_plus, 'y', label="Ограничение сверху")
    # ax1.plot(state_index, delta_minus, 'm', label = "Ограничение снизу")
    # plt.legend()
    plt.grid(True)
    # plt.savefig('power_line{}_jod{}_xen{}.png'.format(nstate,jod_dimension, xe_dimension))
    plt.show()

    ax1 = plt.subplot()
    ax1.plot(state_index, offset_before_insertion, "r-", label="Initial AO")
    ax1.plot(state_index, offset_after_insertion, "g--", label=" Reproduced AO(Iod/POD:{}, Xe/POD:{})".format(jod_dimension, xe_dimension) )
    lgnd = ax1.legend(loc='upper right', shadow=False)
    plt.tick_params(axis='both', which='major', labelsize=12)
    # plt.legend()
    # plt.grid(True)
    plt.xlabel("State number (vector number",fontdict=font)
    plt.ylabel("Axial offset (AO), %",fontdict=font)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(-45, 45)
    # plt.savefig('offset_line{}_jod{}_xen{}.png'.format(nstate,jod_dimension, xe_dimension))
    plt.show()

    fig, ax1 = plt.subplots()
    ax1.plot(state_index, (abs(offset_before_insertion) - abs(offset_after_insertion)), 'b')
    lgnd = ax1.legend(loc='upper right', shadow=False)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.xlabel("State number (vector number", fontdict=font)
    plt.ylabel(r'${\Delta {AO}}$, %', fontdict=font)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(-5, 5)
    # ax1.plot(state_index, delta_plus, 'y', label="Ограничение сверху")
    # ax1.plot(state_index, delta_minus, 'm', label = "Ограничение снизу")
    # plt.legend()
    plt.grid(True)
    # plt.savefig('power_line{}_jod{}_xen{}.png'.format(nstate,jod_dimension, xe_dimension))
    plt.show()
    ax1=plt.subplot()
    ax1.plot(w_after_insertion_lst,w_bgk,  'o-', label="(Iod/POD:{}, Xe/POD:{})".format(jod_dimension, xe_dimension))
    lgnd = ax1.legend(loc='upper left', shadow=False)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.xlabel("Reproduced power, %",fontdict=font)
    plt.ylabel("Initial power, %",fontdict=font)
    # plt.legend()
    # plt.grid(True)
    # plt.savefig('power_after and before{}_jod{}_xen{}.png'.format(nstate,jod_dimension, xe_dimension))
    plt.show()

    ax2 = plt.subplot()
    ax2.plot(offset_after_insertion, offset_before_insertion, 'bp', label="( Iod/POD:{}, Xe/POD:{})".format(jod_dimension, xe_dimension))
    lgnd = ax2.legend(loc='upper left', shadow=False)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.xlabel("Reproduced AO, %",fontdict=font)
    plt.ylabel("Initial AO, %",fontdict=font)
    # plt.legend()
    # plt.grid(True)
    # plt.savefig('offset_after and before{}_jod{}_xen{}.png'.format(nstate,jod_dimension, xe_dimension))
    plt.show()

