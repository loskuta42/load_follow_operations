from mc2py.zgiw import *
import h5py    # HDF5 support
import numpy as np
from mc2py.h5buf import H5membuf

def save_xen_jod(h5_filename, YMFAST=1):
    """сохранение данных для создание xe jod базиса"""
    soc = getv()
    #soc = Tscript_drv("tcp://localhost:5555")
    soc.YMFAST = YMFAST
    soc.step(4)

    xen= soc.YMRO_XEN
    jod = soc.YMRO_JOD
    neutron = soc.YMFISF
    w = soc.YMINTPOW
    cbor = soc.YMBOR_COR
    temp = soc.YMTMIX_IN_INPUT
    hgrp = soc["#YS#YSHGRP"]
    AO = soc.ymoffset
    RpSum = soc.YMRP_POW
    Rp1 = soc.YMRP_C01
    Rp2 = soc.YMRP_C02
    Rp3 = soc.YMRP_C03
    Rp4 = soc.YMRP_C04
    Rp5 = soc.YMRP_C05
    Rp6 = soc.YMRP_C06
    Rp7 = soc.YMRP_C07
    Rp8 = soc.YMRP_C08
    Rp9 = soc.YMRP_C09
    Rp10 = soc.YMRP_C10
    Rp11 = soc.YMRP_C11
    Rp12 = soc.YMRP_C12
    Rp13 = soc.YMRP_C13
    Rp14 = soc.YMRP_C14
    Zpn1 = soc.YMZPOLD1
    Zpn2 = soc.YMZPOLD2
    Zpn3 = soc.YMZPOLD3
    Zpn4 = soc.YMZPOLD4
    Zpn5 = soc.YMZPOLD5
    Zpn6 = soc.YMZPOLD6
    # Открываем файл
    with h5py.File( h5_filename, "a" ) as f5:
        # При необходимости создадим группу group_name
        # Если структура "datetime" еще не встречалась, то ее надо создать и описать
        grp_dsc = u"jod"
        if grp_dsc not in f5:
            with H5membuf(np.array(jod,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(jod,dtype="d"))
            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"JOD concentration"
        else:
            with H5membuf(np.array(jod,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(jod,dtype="d"))


        grp_dsc = u"xen"
        if grp_dsc not in f5:
            with H5membuf(np.array(xen,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(xen,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"XEN concentration"
        else:
            with H5membuf(np.array(xen,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(xen,dtype="d"))


        grp_dsc = u"neutron"
        if grp_dsc not in f5:
            with H5membuf(np.array(neutron,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(neutron,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Neutron distibution"
        else:
            with H5membuf(np.array(neutron,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(neutron,dtype="d"))



        grp_dsc = u"w"
        if grp_dsc not in f5:
            with H5membuf(np.array(w,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(w,dtype="d"))
            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"power, %"
        else:
            with H5membuf(np.array(w,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(w,dtype="d"))

        grp_dsc = u"RpSum"
        if grp_dsc not in f5:
            with H5membuf(np.array(RpSum,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(RpSum,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power sum, wt"
        else:
            with H5membuf(np.array(RpSum,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(RpSum,dtype="d"))



        grp_dsc = u"Rp1"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp1,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp1,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 1, wt"
        else:
            with H5membuf(np.array(Rp1,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp1,dtype="d"))



        grp_dsc = u"Rp2"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp2,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp2,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 2, wt"
        else:
            with H5membuf(np.array(Rp2,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp2,dtype="d"))

        grp_dsc = u"Rp3"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp3,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp3,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 3, wt"
        else:
            with H5membuf(np.array(Rp3,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp3,dtype="d"))

        grp_dsc = u"Rp4"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp4,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp4,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 4, wt"
        else:
            with H5membuf(np.array(Rp4,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp4,dtype="d"))


        grp_dsc = u"Rp5"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp5,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp5,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 5, wt"
        else:
            with H5membuf(np.array(Rp5,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp5,dtype="d"))





        grp_dsc = u"Rp6"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp6,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp6,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 6, wt"
        else:
            with H5membuf(np.array(Rp6,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp6,dtype="d"))


        grp_dsc = u"Rp7"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp7,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp7,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 7, wt"
        else:
            with H5membuf(np.array(Rp7,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp7,dtype="d"))





        grp_dsc = u"Rp8"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp8,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp8,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 8, wt"
        else:
            with H5membuf(np.array(Rp8,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp8,dtype="d"))


        grp_dsc = u"Rp9"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp9,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp9,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 9, wt"
        else:
            with H5membuf(np.array(Rp9,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp9,dtype="d"))


        grp_dsc = u"Rp10"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp10,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp10,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 10, wt"
        else:
            with H5membuf(np.array(Rp10,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp10,dtype="d"))



        grp_dsc = u"Rp11"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp11,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp11,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 11, wt"
        else:
            with H5membuf(np.array(Rp11,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp11,dtype="d"))


        grp_dsc = u"Rp12"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp12,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp12,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 12, wt"
        else:
            with H5membuf(np.array(Rp12,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp12,dtype="d"))


        grp_dsc = u"Rp13"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp13,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp13,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 13, wt"
        else:
            with H5membuf(np.array(Rp13,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp13,dtype="d"))


        grp_dsc = u"Rp14"
        if grp_dsc not in f5:
            with H5membuf(np.array(Rp14,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp14,dtype="d"))

            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"Residual power 14, wt"
        else:
            with H5membuf(np.array(Rp14,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(Rp14,dtype="d"))































        grp_dsc = u"cbor"
        if grp_dsc not in f5:
            with H5membuf(np.array(cbor,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(cbor,dtype="d"))
            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"cbor, g/kg"
        else:
            with H5membuf(np.array(cbor,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(cbor,dtype="d"))

        grp_dsc = u"hgrp"
        if grp_dsc not in f5:
            with H5membuf(np.array(hgrp,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(hgrp,dtype="d"))
            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"hgrp, o.e."
        else:
            with H5membuf(np.array(hgrp,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(hgrp,dtype="d"))


        grp_dsc = u"temp"
        if grp_dsc not in f5:
            with H5membuf(np.array(temp,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(temp,dtype="d"))
            # записываем комментарий к времени
            g=f5[grp_dsc]
            g.attrs["dsc"]=u"temp, C"
        else:
            with H5membuf(np.array(temp,dtype="d"),f5, grp_dsc,1) as date:
                date.append(np.array(temp, dtype="d"))

        grp_dsc = u"AO"
        if grp_dsc not in f5:
            with H5membuf(np.array(AO, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(AO, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"AO, C"
        else:
            with H5membuf(np.array(AO, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(AO, dtype="d"))

        grp_dsc = u"Zpn1"
        if grp_dsc not in f5:
            with H5membuf(np.array(Zpn1, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn1, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"Zg1, C"
        else:
            with H5membuf(np.array(Zpn1, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn1, dtype="d"))

        grp_dsc = u"Zpn2"
        if grp_dsc not in f5:
            with H5membuf(np.array(Zpn2, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn2, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"Zpn2, C"
        else:
            with H5membuf(np.array(Zpn2, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn2, dtype="d"))

        grp_dsc = u"Zpn3"
        if grp_dsc not in f5:
            with H5membuf(np.array(Zpn3, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn3, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"Zpn3, C"
        else:
            with H5membuf(np.array(Zpn3, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn3, dtype="d"))

        grp_dsc = u"Zpn4"
        if grp_dsc not in f5:
            with H5membuf(np.array(Zpn4, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn4, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"Zpn4, C"
        else:
            with H5membuf(np.array(Zpn4, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn4, dtype="d"))

        grp_dsc = u"Zpn5"
        if grp_dsc not in f5:
            with H5membuf(np.array(Zpn5, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn5, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"Zpn5, C"
        else:
            with H5membuf(np.array(Zpn5, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn5, dtype="d"))

        grp_dsc = u"Zpn6"
        if grp_dsc not in f5:
            with H5membuf(np.array(Zpn6, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn6, dtype="d"))
            # записываем комментарий к времени
            g = f5[grp_dsc]
            g.attrs["dsc"] = u"Zpn6, C"
        else:
            with H5membuf(np.array(Zpn6, dtype="d"), f5, grp_dsc, 1) as date:
                date.append(np.array(Zpn6, dtype="d"))


if __name__ == "__main__":
    save_xen_jod(h5_filename = r"data_for_bgk.h5" )







