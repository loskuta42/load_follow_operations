
# -*- coding: cp1251 -*-

import numpy as np
from zag_Xe_Jod_PCA import load_initial_data_from_hdf5
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA


def DefaultDot(a, b):
    u"""dot по умолчанию"""
    return a.dot(b)


def Bgk(vset, nredu, fdot=DefaultDot, linkomb=None, W=None, eltype='d'):
    u"""расчет базиса главных компонент
vset  - исходный набор векторов
nredu - количество векторов в БГК
fdot  - функция для расчета скалярного произведения
если fdot не задана то вместо нее используется x.dot(y)
W - весовая функция для векторов
eltype - вычисления могут производится с двойной или одинарной точностью
"""
    n = len(vset)
    if nredu > n:
        raise Exception(u"n<n")
    A = np.zeros((n, n), eltype)
    if W == None:
        for i in range(n):
            for j in range(i, n):
                fd = fdot(vset[i], vset[j])
                A[i, j] = fd
                A[j, i] = fd
    else:
        for i in range(n):
            for j in range(i, n):
                fd = W[i]*W[j]*fdot(vset[i], vset[j])
                A[i, j] = fd
                A[j, i] = fd
    lam, v = np.linalg.eigh(A)
    lam_v = zip(abs(lam), np.transpose(v))
##    lam_v.sort(reverse=1)
    lam_v = sorted(lam_v, reverse=1, key = lambda x: x[0])
    sr = lam_v[:nredu]
    return lam,v,lam_v,sr

if __name__ == "__main__":
    fileName = r"D:\Projects\bober\БГК_VVER1200\data.h5\xen_jod_AO_Rp_Zpn_den.h5"
    xen, jod, w, cbor, temp, hgrp,AO_before = load_initial_data_from_hdf5(fileName)
    vset1 = xen[:100]
    vset2 = jod[:100]
    Pn_xen = []
    Pn_jod = []
    nredu_lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    for nredu in nredu_lst:

        lam, v, lam_v, sr = Bgk(vset1, nredu = nredu , fdot=DefaultDot, linkomb=None, W=None, eltype='d')
        eigvals = []
        eingvecs = []
        for k, ev in lam_v:
            eigval = k
            eigvals.append(eigval)
            eingvec = ev
            eingvecs.append(eingvec)

        Sn = 0
        Sd = 0
        for i in range(0, nredu):
            Sn += eigvals[i]
        for i in range(0, len(eigvals)):
            Sd += eigvals[i]

        P = (Sn / Sd)
        Pn_xen.append(P)

    for nredu in nredu_lst:

        lam, v, lam_v, sr = Bgk(vset2, nredu=nredu, fdot=DefaultDot, linkomb=None, W=None, eltype='d')
        eigvals = []
        eingvecs = []
        for k, ev in lam_v:
            eigval = k
            eigvals.append(eigval)
            eingvec = ev
            eingvecs.append(eingvec)

        Sn = 0
        Sd = 0
        for i in range(0, nredu):
            Sn += eigvals[i]
        for i in range(0, len(eigvals)):
            Sd += eigvals[i]

        P = (Sn / Sd)
        Pn_jod.append(P)

    #fig, ax = plt.subplots()
    #ax.plot(nredu_lst , Pn_xen,"ro-", label="Набор для построения БГК")
    #ax.grid(True)
    #plt.ylabel("энергетической критерий_xen:(P)")
    #plt.xlabel('Размерность БГК')
    # plt.savefig("mean_error_xe.png")
    #plt.show()
    #fig, ax = plt.subplots()
    #k = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    #ax.plot(nredu_lst, Pn_jod, "b^-", label="Набор для построения БГК")
    #ax.grid(True)
    #plt.ylabel("энергетической критерий_jod:(P)")
    #plt.xlabel('Размерность БГК')
    # plt.savefig("mean_error_xe.png")
    #plt.show()

    host = host_subplot(111, axes_class=AA.Axes)
    par1 = host.twinx()
    host.set_xlabel(u"Размерность БГК")
    host.set_ylabel(u"энергетической критерий_jod")
    par1.set_ylabel(u"энергетической критерий_xen")
    #p1, = host.plot(nredu_lst,Pn_jod , "ro-", label=u"Pn_jod", markersize=5, linewidth=2)
    p2, = par1.plot(nredu_lst, Pn_xen, "y*-", label=u"Pn_xen", markersize=5, linewidth=2)
    host.set_ylim(0, 1)
    host.legend(shadow=True, fancybox=True, loc=5)
    host.grid(True)
    host.set_title(u"извлеченная часть информации ")
    #plt.savefig(r"Pn_xen.png")
    plt.show()



