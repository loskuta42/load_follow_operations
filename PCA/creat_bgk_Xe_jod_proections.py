"""задача этого файла - создание проекций векторов Хе и иод в базисе главных компонент для данного состояния реактора"""

from mc2py.h5buf import H5membuf
import numpy as np
import h5py
from mc2py.bgk import Tbgk, NprNorm
import matplotlib.pyplot as plt



def load_from_hdf5( h5_filename):
    u""" Функция для перевода данных из HDF5 в xen, jod"""
    # Открываем файл
    with h5py.File( h5_filename, "a" ) as f5:
        # переберем все поля в hdf5
        xen = f5["xen"][:]
        jod = f5["jod"][:]
        w = f5["w"][:]
        cbor = f5["cbor"][:]
        temp = f5["temp"][:]
        hgrp = f5["hgrp"][:]
        AO=f5["AO"][:]

    return np.array(xen), np.array(jod),np.array(w),np.array(cbor),np.array(temp),np.array(hgrp),np.array(AO)

def proection(vecs, bgk_creation_vecs_amount, nredu_lst):
    """
    Получение проекций векторов через БГК
    :param vecs: начальный набор векторов
    :param bgk_creation_vecs_amount: количесвто векторов, используемых для построения БГК
    :param nredu_lst: количесвто векторов в БГК
    :return:
    возвращаем словарь: количесвто векторов в БКГ - проекции всего начального набора в БГК
    """
    nredu_dic={}
    # выбор начального набора для простроения БГК
    vecs_obrabotka = vecs[:bgk_creation_vecs_amount]
    for nredu in nredu_lst:
        bgk = Tbgk(vset=vecs_obrabotka, nredu=nredu)
        # спроецируем поочередна все вектора из набора KCEHOHA в БГК
        proections = []
        for vec in vecs:
            # получение проекции вектора в БГК
            pr_vec = bgk.proection(vec)
            # сохранение преокции вектора в БГК
            proections.append(pr_vec)
        nredu_dic[nredu] = proections

    return nredu_dic



if __name__=='__main__':
    h5_filename = r"D:\Projects\bober\БГК_VVER1200\data.h5\xen_jod_AO_Rp_Zpn_den.h5"
    xen, jod,w,cbor,temp,hgrp,AO = load_from_hdf5(h5_filename)
    # укорачиваем набор для построения БГК
    #w_short=w[:200]
   # cbor_short=cbor[:200]
    #temp_short=temp[:200]
   # hgrp_short=hgrp[:200]

    #xen_short = xen[:200]
    nredu_xen_lst = [1,2,3,4,5,6,7]
    xen_proections = proection(xen, bgk_creation_vecs_amount=300, nredu_lst=nredu_xen_lst)

    #jod_short = jod[:200]
    nredu_jod_lst = [1,2,3,4,5,6,7,8]
    jod_proections = proection(jod, bgk_creation_vecs_amount=300, nredu_lst=nredu_jod_lst)

def save_xen_jod_bgk(fileName):
    """сохранение данных проекций векторов для загрузки в мфа"""
    xen_bgk = xen_proections
    jod_bgk = jod_proections
    w_bgk = w
    cbor_bgk = cbor
    temp_bgk = temp
    hgrp_bgk = hgrp
    AO_bgk=AO

    # Открываем файл
    with h5py.File(fileName, "a") as f5:
        # При необходимости создадим группу group_name
        # Если структура "datetime" еще не встречалась, то ее надо создать и описать
        grp_dsc = u"hgrp_bgk"
        if grp_dsc not in f5:
            with H5membuf(np.array(hgrp_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(hgrp_bgk, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"hgrp, o.e."
        else:
            with H5membuf(np.array(hgrp_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(hgrp_bgk, dtype="d"))

        for nredu in nredu_jod_lst:
            grp_dsc = u"jod_bgk{}".format(nredu)
            if grp_dsc not in f5:
                with H5membuf(np.array(jod_bgk[nredu], dtype="d"), f5, grp_dsc, 1) as date:
                    date.append(np.array(jod_bgk[nredu], dtype="d"))
                # записываем комментарий к времени
                g = f5[grp_dsc]
                g.attrs["dsc"] = u"JOD concentration"
            else:
                with H5membuf(np.array(jod_bgk[nredu], dtype="d"), f5, grp_dsc, 1) as date:
                    date.append(np.array(jod_bgk[nredu], dtype="d"))

        for nredu in nredu_xen_lst:
            grp_dsc = u"xen_bgk{}".format(nredu)
            if grp_dsc not in f5:
                with H5membuf(np.array(xen_bgk[nredu], dtype="d"), f5, grp_dsc, 1) as date:
                    date.append(np.array(xen_bgk[nredu], dtype="d"))

                # записываем комментарий к времени
                g = f5[grp_dsc]
                g.attrs["dsc"] = u"XEN concentration"
            else:
                with H5membuf(np.array(xen_bgk[nredu], dtype="d"), f5, grp_dsc, 1) as date:
                    date.append(np.array(xen_bgk[nredu], dtype="d"))

        grp_dsc = u"w_bgk"
        if grp_dsc not in f5:
            with H5membuf(np.array(w_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(w_bgk, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"power, %"
        else:
            with H5membuf(np.array(w_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(w_bgk, dtype="d"))

        grp_dsc = u"cbor_bgk"
        if grp_dsc not in f5:
            with H5membuf(np.array(cbor_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(cbor_bgk, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"cbor, g/kg"
        else:
            with H5membuf(np.array(cbor_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(cbor_bgk, dtype="d"))

        grp_dsc = u"temp_bgk"
        if grp_dsc not in f5:
            with H5membuf(np.array(temp_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(temp_bgk, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"temp, C"
        else:
            with H5membuf(np.array(temp_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(temp_bgk, dtype="d"))

        grp_dsc = u"AO_bgk"
        if grp_dsc not in f5:
            with H5membuf(np.array(AO_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(AO_bgk, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"AO_bgk, C"
        else:
            with H5membuf(np.array(AO_bgk, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(AO_bgk, dtype="d"))

if __name__ == "__main__":
    save_xen_jod_bgk(fileName=r"xen_jod_AO_Rp_Zpn_bgk78_den.h5")




#   ax1 = plt.subplot(2, 1, 1)
#    for i in nredu_xen_lst:
#        ax1.plot(range(len(xen_proections[i])), xen_proections[i], label="nredu {}".format(nredu_xen_lst))
#        plt.ylabel('Проекции_векторов_Хе_в БГК')
#        plt.legend()
#        plt.grid(True)
#
#    ax2 = plt.subplot(2, 1, 2)
#    for i in nredu_jod_lst:
#        ax2.plot(range(len(jod_proections[i])), jod_proections[i], label="nredu {}".format(nredu_jod_lst))
#        plt.ylabel('Проекции_векторов_jod_в БГК')
#        plt.legend()
#        plt.grid(True)
#    # plt.savefig("Проекции_векторов_Xe_jod_в БГК1.png")
#    plt.show()
