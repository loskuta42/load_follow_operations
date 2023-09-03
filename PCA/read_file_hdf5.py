from mc2py.zgiw import *
import h5py  # HDF5 support
import numpy as np
from mc2py.h5buf import H5membuf
import matplotlib.pyplot as plt

def load_proection_data_from_hdf5( h5_filename_bgk, xe_bgk_len=4, jod_bgk_len=5):
    u""" Функция для перевода данных из HDF5 в xen, jod"""
    # Открываем файл
    with h5py.File( h5_filename_bgk, "a" ) as f5:
            xen_bgk = f5["xen_bgk{}".format(xe_bgk_len)][:]
            jod_bgk = f5["jod_bgk{}".format(jod_bgk_len)][:]
            w_bgk = f5["w_bgk"][:]
            cbor_bgk = f5["cbor_bgk"][:]
            temp_bgk = f5["temp_bgk"][:]
            hgrp_bgk = f5["hgrp_bgk"][:]
            AO_bgk = f5["AO_bgk"][:]
            Rp_bgk = f5["Rp_bgk"][:]



    return xen_bgk, jod_bgk, w_bgk, cbor_bgk, temp_bgk, hgrp_bgk,AO_bgk,Rp_bgk


def load_initial_data_from_hdf5(h5_filename):
    # Открываем файл
    with h5py.File(h5_filename, "a" ) as f5:
        # переберем все поля в hdf5
        xen = f5["xen"][:]
        jod = f5["jod"][:]
        w = f5["w"][:]
        cbor = f5["cbor"][:]
        temp = f5["temp"][:]
        hgrp = f5["hgrp"][:]
        AO_before=f5["AO"][:]
        Rp = f5["Rp"][:]
    return xen, jod, w, cbor, temp, hgrp,AO_before,Rp

if __name__ == "__main__":
    h5_filename = r"D:\Projects\bober\БГК_VVER1200\data.h5\xen_jod_AO_Rp_Zpn_den.h5"
    #h5_filename_bgk = r"D:\Projects\bober\БГК\xen_jod_AO_bgk_den.h5"
    #jod_bgk_len = 5
    #xe_bgk_len = 4
    xen, jod, w, cbor, temp, hgrp,AO_before,Rp = load_initial_data_from_hdf5(h5_filename)
    #xen_bgk, jod_bgk, w_bgk, cbor_bgk, temp_bgk, hgrp_bgk,AO_bgk= load_proection_data_from_hdf5(h5_filename_bgk,xe_bgk_len=xe_bgk_len,jod_bgk_len=jod_bgk_len)

    #print(xen.shape),print(xen[1])
    #print("------------------------------------------------------------------")
    #print(jod.shape), print(jod[1])
    #print("------------------------------------------------------------------")
    print(w.shape),print(w)
    print("-------------------------------------------------------------------")
    #print(cbor.shape), print(cbor)
    #print("-------------------------------------------------------------------")
    #print(temp.shape), print(temp)
    #print("-------------------------------------------------------------------")
    #print(hgrp.shape), print(hgrp)
    #print("-------------------------------------------------------------------")
    #print(AO_before.shape), print(AO_before)
    print("-------------------------------------------------------------------")
    print(Rp.shape), print(Rp)


    a=[sum(Rp[el]) for el in range(len(Rp))]

    import os, sys, shutil
    import numpy as np

    # решение проблемы с выводом на график русских шрифтов
    import matplotlib.pyplot as plt

    plt.rc('font', family='serif')
    plt.rc('font', serif='Times New Roman')
    plt.rc('font', size='20')
    plt.rc('figure', figsize=(11, 7))

    from mpl_toolkits.axes_grid1 import host_subplot
    import mpl_toolkits.axisartist as AA

    host = host_subplot(111, axes_class=AA.Axes)
    par1 = host.twinx()
    host.set_xlabel(u"номер состояния")
    host.set_ylabel(u"Residual power (Rp), о.е.")
    par1.set_ylabel(u"Neutron power(Np), о.е.")
    p1, = host.plot(range(len(a)), a, "ro-", label = u"Rp",markersize=5, linewidth = 2 )
    p2, = par1.plot(range(len(a)), w , "y*-", label=u"Np", markersize=5, linewidth=2)
    host.legend(shadow=True, fancybox=True, loc=5)
    host.grid(True)
    #plt.savefig(r"evolution of the neutron and residual power_.png")
    plt.show()

    #cc=1