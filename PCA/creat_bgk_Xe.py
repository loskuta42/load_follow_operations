"""задача этого файла - создание базиса главных компонент для данного состояния реактора"""

import numpy as np
import h5py
from mc2py.bgk import Tbgk, NprNorm
import matplotlib.pyplot as plt
from app_pod import Bgk,DefaultDot
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA


#
# def Bgk(vset, nredu, fdot=DefaultDot, linkomb=None, W=None, eltype='d'):
#     u"""расчет базиса главных компонент
# vset  - исходный набор векторов
# nredu - количество векторов в БГК
# fdot  - функция для расчета скалярного произведения
# если fdot не задана то вместо нее используется x.dot(y)
# W - весовая функция для векторов
# eltype - вычисления могут производится с двойной или одинарной точностью
# """



def load_from_hdf5( h5_filename):
    u""" Функция для перевода данных из HDF5 в xen, jod"""

    # Открываем файл
    with h5py.File( h5_filename, "a" ) as f5:
        # переберем все поля в hdf5
        xen = f5["xen"][:]

    return np.array(xen)


if __name__ == "__main__":
    h5_filename = r"data_for_bgk.h5"
    xen = load_from_hdf5(h5_filename)

    # укорачиваем набор для построения БГК
    xen_short1 = xen[:300]
    xen_short2 = xen[-300:]
    #nredu_lst = [1, 2, 3, 4]
    nredu_lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    vset1 = xen[:300]
    vset2 = xen[-300:]
    Pn_xen1 = []
    Pn_xen2 = []
    for nredu in nredu_lst:

        lam, v, lam_v, sr = Bgk(vset1, nredu=nredu, fdot=DefaultDot, linkomb=None, W=None, eltype='d')
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
        Pn_xen1.append(P)

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
        Pn_xen2.append(P)
    font = {'family': 'serif', 'color': 'black', 'weight': 'normal', 'size': 14, }
    fig, ax = plt.subplots()
    errors_mean1 = [] # средняя ошибка воспроизведения векторов от размера БГК
    errors_mean2=[]
    for nredu in nredu_lst:
        bgk_xen = Tbgk(vset=xen_short1, nredu=nredu)
        # набор спроекцированных в БГК векторов
        xen_proections=[]
        errors1 = []
        # спроецируем поочередна все вектора из набора в БГК
        for vec in xen_short1:
            # получение проекции вектора в БГК
            pr_vec = bgk_xen.proection(vec)
            # сохранение преокции вектора в БГК
            xen_proections.append(pr_vec)
            # получение разницы между вектором и его проекцией
            delta_vec = pr_vec - vec
            # вычисление ошибки воспроизведения вектора с помощью БГК
            err = NprNorm(pr_vec, delta_vec)
            errors1.append(err)
        # оценка средней ошибки воспроизведения вектора через БГК
        errors_mean1.append( np.mean(errors1) )


        ax.plot(range(len(errors1[:300])), errors1[:300], label="Dimension POD:{}".format(nredu))
        lgnd = ax.legend(loc='upper right', shadow=True)
        # lgnd.get_frame().set_facecolor('#E6DAA6')
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.ylabel(r'$\frac{|| \Delta \vec{Xen} ||}{ ||\vec{Xen}|| }$',fontdict=font)
    #plt.xlabel("Номер состояния", fontdict=font)
    plt.xlabel("State number (xenon vectors)", fontdict=font)
    plt.legend()
    # plt.grid(True)
    # plt.savefig("main_state_error_xe.png")
    plt.show()


    fig, ax = plt.subplots()
    for nredu in nredu_lst:
        bgk_xen = Tbgk(vset=xen_short1, nredu=nredu)
        # набор спроекцированных в БГК векторов
        xen_proections = []
        errors2 = []
        for vec in xen_short2:
            # получение проекции вектора в БГК
            pr_vec = bgk_xen.proection(vec)
            # получение разницы между вектором и его проекцией
            delta_vec = pr_vec - vec
            # вычисление ошибки воспроизведения вектора с помощью БГК
            err = NprNorm(pr_vec, delta_vec)
            errors2.append(err)
        # оценка средней ошибки воспроизведения вектора через БГК
        errors_mean2.append( np.mean(errors2) )

        ax.plot(range(len(errors2[:300])), errors2[:300], label="Розмерность БГК:{}".format(nredu))
        lgnd = ax.legend(loc='upper right', shadow=True)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.ylabel(r'$\frac{|| \Delta \vec{Xe} ||}{ ||\vec{Xe}|| }$, о.е.',fontdict=font)
    plt.xlabel("Номер состояния",fontdict=font)
    plt.legend()
    # plt.grid(True)
    # plt.savefig("additional_state_error_xe.png")
    plt.show()

    # plt.rc('font', family='serif')
    # plt.rc('font', serif='Times New Roman')
    # plt.rc('font', size='16')
    # plt.rc('figure', figsize=(8, 6))

    host = host_subplot(111, axes_class=AA.Axes)
    par1 = host.twinx()
    host.set_xlabel(u"Dimension POD for xenon vectors")
    host.set_ylabel(u"mean vector reproduction error (MVR)")
    par1.set_ylabel(u"information extraction parameter (P)")
    p1, = host.plot(nredu_lst,errors_mean1, "ro-", label=u"MVR for vector group ", markersize=5, linewidth=2)
    #p2, = host.plot(nredu_lst, errors_mean2,  "b^-", label=u"СОВ контрольный набор", markersize=5, linewidth=2)
    p3, = par1.plot(nredu_lst, Pn_xen1, "cp-", label=u"P for vector group", markersize=5, linewidth=2)
    #p4, = par1.plot(nredu_lst, Pn_xen2, "gd-", label=u"КИИ контрольный набор", markersize=5, linewidth=2)
    host.set_ylim(0, 0.03)
    host.set_xlim(0, 17)
    host.legend(shadow=False, fancybox=True, loc=5)
    #host.grid(True)
    #host.set_title(u"оценка извлечения информаций")
    # plt.savefig(r"Er_mean_Pn_xen.png")
    plt.show()

    print(xen.shape)

