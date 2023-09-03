import numpy as np
import h5py
from STD_function import standard_deviation1,standard_deviation2
import matplotlib.pyplot as plt

def load_from_hdf5(fname):
    # Открываем файл
    res = np.loadtxt(fname)
    w_after_insertion_lst = res[0]
    w_bgk = res[1]
    offset_after_insertion = res[2]
    offset_before_insertion = res[3]

    return np.array(w_after_insertion_lst), np.array(w_bgk), np.array(offset_after_insertion),np.array( offset_before_insertion)


if __name__ == "__main__":
    jod_bgk_len=5
    xe_bgk_len=4
    fname = r"D:\Projects\bober\БГК_VVER1200\data.txt\power_results_300v_jod5_xen4.txt"
    # fname = r"D:\Projects\bober\БГК_VVER1200\data.txt\power_results_300v_jod5_xen4.txt"
    w_after_insertion_lst, w_bgk, offset_after_insertion, offset_before_insertion = load_from_hdf5(fname)
    nstate = 300
    X1 = []
    Y1 = []
    X2 = []
    Y2 = []
    Deviation_W = []
    Deviation_AO = []
    errors_power=[]
    errors_offset=[]

    for state_index in range(nstate):
        X1.append(w_bgk[state_index])
        Y1.append(w_after_insertion_lst[state_index])
        X2.append( offset_before_insertion[state_index])
        Y2.append(offset_after_insertion[state_index])
        # Delta_W.append(w_after_insertion_lst[state_index]- w_bgk[state_index])
        # Delta_AO.append(abs(offset_after_insertion[state_index]) - abs(offset_before_insertion[state_index]))
        errors_power.append(Y1[state_index] - X1[state_index])
        errors_offset.append(Y2[state_index] - X2[state_index])
        Deviation_W.append(100*(errors_power[state_index])/Y1[state_index])
        Deviation_AO.append(errors_offset[state_index] / abs(Y2[state_index]))

    std_X1Y1 = standard_deviation1(X1,Y1)
    std_X2Y2 = standard_deviation1(X2,Y2)

    std_er_PW = standard_deviation2(errors_power)
    std_er_AO = standard_deviation2(errors_offset)

    print('CKO Power :{}'.format(std_X1Y1))
    print('CKO AO:{}'.format(std_X2Y2))
    print('-----------------------------------------------------------------------------')
    print('The standard deviation of errors power:{}'.format(std_er_PW))
    print('The standard deviation of errors axial offset :{}'.format(std_er_AO))

    plt.rc('font', family='serif')
    plt.rc('font', serif='Times New Roman')
    plt.rc('font', size='14')
    plt.rc('figure', figsize=(9, 7))

    fig, ax = plt.subplots()
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(range(nstate), X1, "r", label="Pw_befor/jod:{}, xen:{}".format(jod_bgk_len, xe_bgk_len, std_X1Y1))
    ax1.plot(range(nstate), Y1, "g--", label="Pw_after/jod:{}, xen:{}, std:{}".format(jod_bgk_len, xe_bgk_len, std_X1Y1))
    # lgnd = ax1.legend(loc='upper center', shadow=True)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(40, 130)
    plt.ylabel('Power_before_after_insertion, %')
    plt.xlabel('state_index')
    plt.legend()
    plt.grid(True)
    ax2 = plt.subplot(2, 1, 2)
    # ax2.plot(range(nstate), X2, "r", label="AO_befor/jod:{}, xen:{}".format(jod_bgk_len, xe_bgk_len, std_X2Y2))
    ax2.plot(range(nstate), Y2, "b--", label="AO_after/jod:{}, xen:{}, std:{}".format(jod_bgk_len, xe_bgk_len, std_X2Y2))
    # lgnd = ax2.legend(loc='upper center', shadow=True)
    ax2.set_xlim(0, 300)
    ax2.set_ylim(-45,60)
    plt.ylabel('AO_before_after_insertion, %')
    plt.xlabel('state_index')
    plt.legend()
    plt.grid(True)
    #plt.savefig('power and offset__before_after_jod{}_xen{}.png'.format(jod_bgk_len, xe_bgk_len))
    plt.show()

    fig, ax = plt.subplots()
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(range(nstate), errors_power, "r", label="Delta_power/jod:{}, xen:{}, std:{}".format(jod_bgk_len, xe_bgk_len, std_er_PW))
    # lgnd = ax1.legend(loc='upper right', shadow=True)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(-1.5, 2)
    plt.ylabel('Delta_power_error, MW')
    plt.xlabel('state_index')
    plt.legend()
    plt.grid(True)
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(range(nstate), errors_offset, "b", label="Delta_offset/jod:{}, xen:{}, std:{}".format(jod_bgk_len, xe_bgk_len, std_er_AO))
    # lgnd = ax2.legend(loc='upper right', shadow=True)
    ax2.set_xlim(0, 300)
    ax2.set_ylim(-5, 9)
    plt.ylabel('Delta_offset_error, %')
    plt.xlabel('state_index')
    plt.legend()
    plt.grid(True)
    #plt.savefig('Error_power and offset_jod{}_xen{}_Std_er_PW{}_Std_er_AO{}.png'.format(jod_bgk_len, xe_bgk_len, std_er_PW, std_er_AO))
    plt.show()

    fig, ax = plt.subplots()
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(range(nstate), Deviation_W, "r", label="Power_bef/jod:{}, xen:{}, std:{}".format(jod_bgk_len, xe_bgk_len, std_X1Y1))
    # lgnd = ax1.legend(loc='upper right', shadow=True)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(-2, 2)
    plt.ylabel('Погрешность мощности,%  ')
    plt.xlabel('state_index')
    plt.legend()
    plt.grid(True)
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(range(nstate),Deviation_AO , "b", label="AO_befor/jod:{}, xen:{}, std:{}".format(jod_bgk_len, xe_bgk_len, std_X2Y2))
    # lgnd = ax2.legend(loc='upper right', shadow=True)
    ax2.set_xlim(0, 300)
    ax2.set_ylim(-5, 5)
    plt.ylabel('Погрешность офсета,%')
    plt.xlabel('state_index')
    plt.legend()
    plt.grid(True)
    # plt.savefig('power and offset__before_after_jod{}_xen{}.png'.format(jod_bgk_len, xe_bgk_len))
    plt.show()
    print("errors_offset:", errors_offset)
    print("-----------------------------")
    print("offset_after_insertion:",Y2)
    print("-----------------------------")
    print("errors_offset[170:190]:", errors_offset[170:190])
    print("offset_after_[170:190]:", Y2[170:190])
    print("-----------------------------")
    print("errors_offset[177,181]:", errors_offset[177],errors_offset[181])
    print("offset_after_[177,181]:", Y2[177],Y2[181])
    print("-----------------------------")
    print("Погрешность на 177 состоянии:",errors_offset[177]/Y2[177])
    print("Погрешность на 181 состоянии:", errors_offset[181] / Y2[181])





