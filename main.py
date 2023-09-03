import multiprocessing
import pickle
from multiprocessing import Queue

import lmdb

from two_point_model import State, Model
from dp_problem_final import DynamicProgrammingProblem
import numpy as np

import time as timer


def model_creation():
    model = Model(nnodes=2)
    model._delt = 1
    w0 = 50
    # установка состояния для верхней части зоны
    st1_beg = State(
        time=0,
        w=w0,
        h0=0.2,
        h1=0.0,
        # h2=0.0,
        cb=7,
        ro=0,
        ci=None,
        jod=None,
        xe=None
    )
    st1_beg.ci = model.calc_static_ci_in_node(w=w0)
    st1_beg.jod, st1_beg.xe = model.calc_ravn_jod_and_xe_in_node(w=w0)
    # установка состояния для нижней части зоны
    st2_beg = State(
        time=0,
        w=w0,
        h0=0.0,
        h1=0.0,
        # h2=0.0,
        cb=7,
        ro=0,
        ci=None,
        jod=None,
        xe=None
    )
    st2_beg.ci = model.calc_static_ci_in_node(w=w0)
    st2_beg.jod, st2_beg.xe = model.calc_ravn_jod_and_xe_in_node(w=w0)

    model.set_state(0, st1_beg)
    model.set_state(1, st2_beg)
    model.set_stable_AO(offset_stable=model.get_AO())

    return model


if __name__ == '__main__':
    start_time = timer.time()
    load_follow_operations = np.array(
        [[0 * 3600, 100],
         [1 * 3600, 75],
         [2 * 3600, 50],
         [6 * 3600, 50],
         [10 * 3600, 75],
         [12 * 3600, 100],
         [14 * 3600, 100],
         # [13 * 3600, 75],
         # [14 * 3600, 100],
         # [16 * 3600, 100],
         # [24 * 3600, 100],
         ]
    )
    models_queue = Queue()
    for i in range(multiprocessing.cpu_count()):
        models_queue.put(model_creation())
    # создание состояние - оно будет начальным и считаем, что оно одинаково для всех моделей
    begin_st = model_creation().get_states()

    # сделать расчет эвристики и передать ее в модель динамического программирования
    # гарфик мощности, концентрации бора и ор суз
    semaphore_size = multiprocessing.cpu_count() - 1
    dyn_prog = DynamicProgrammingProblem(
        models=models_queue,
        begin_st=begin_st,
        load_follow_operations=load_follow_operations,
        optimization_type=0,  # 0- водообмен, 1 -потеря энергвыработки !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        evristic_strategy_type=2,
        # 0:  # индивидуальное управление рабочей группой №12
        # 1:  # индивидуальное управление рабочей группой №11
        # 2:  # перехват на 50% и остановка движения группы на 50% от высоты зоны
        # 3:  # стандартное движение на 50% и остановка движения группы внизу зоны
        semaphore_size=semaphore_size
    )

    t0 = load_follow_operations[0, 0]
    tbeg = load_follow_operations[0, 0] - t0
    tend = load_follow_operations[-1, 0] - t0

    time_lst = load_follow_operations.transpose()[0]

    path = dyn_prog.go_from_start_to_final(time_lst)
    print(f'dyn_prog.l_f_opr:{dyn_prog.discard_by_evrestick}')
    print(path)
    print(time_lst)

    pow_int_fun = dyn_prog.evr_obj.pow_int_fun

    data = np.genfromtxt('log_evr.txt')
    time = data[:, 0]
    nagruzka_graph = [pow_int_fun(t) for t in time[:-1]]

    w_tot = data[:, 1]
    AO = data[:, 2]

    w1 = data[:, 3]
    h10 = data[:, 4]
    h11 = data[:, 5]
    cb1 = data[:, 6]
    ro1 = data[:, 7]
    ci1 = data[:, 8]
    jod1 = data[:, 9]
    xe1 = data[:, 10]

    w2 = data[:, 11]
    h20 = data[:, 12]
    h21 = data[:, 13]
    cb2 = data[:, 14]
    ro2 = data[:, 15]
    ci2 = data[:, 16]
    jod2 = data[:, 17]
    xe2 = data[:, 18]
    h_total0 = h10 + h20
    h_total1 = h11 + h21

    h_total0 = 1 - h_total0
    h_total1 = 1 - h_total1

    print("Количество шагов по этапам: ", dyn_prog.number_of_states_per_stage)
    end_time = timer.time()
    print('work_time', (end_time - start_time))
    # печать с записью промежуточных значений
    time_optimal = []
    hgrp_optimal0 = []
    hgrp_optimal1 = []
    hgrp_optimal2 = []
    cb_optimal = []
    power_optimal = []
    xe1_optimal = []
    xe2_optimal = []
    for ind, track in enumerate(dyn_prog.optimal_path):
        # with lmdb.open('tracks_info', map_size=1099511627776) as env:
        with lmdb.open('tracks_info', map_size=536870912) as env:

            with env.begin() as txn:
                data = txn.get(track.track_id.encode())
                states = pickle.loads(data)
        for model_st in states:
            hgrp_opt_parent0 = 1 - (model_st[0].h[0] + model_st[1].h[0])
            hgrp_opt_parent1 = 1 - (model_st[0].h[1] + model_st[1].h[1])
            hgrp_optimal0.append(hgrp_opt_parent0)
            hgrp_optimal1.append(hgrp_opt_parent1)
            cb_optimal.append(model_st[0].cb)
            power_optimal.append(model_st[0].w + model_st[1].w)
            time_optimal.append(model_st[0].time)
            xe1_optimal.append(model_st[0].xe)
            xe2_optimal.append(model_st[1].xe)

    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(3, 1)
    axs[0].plot(time[:-1] / 3600, nagruzka_graph, 'r-', label='График несения нагрузки')
    axs[0].plot(np.array(time_optimal) / 3600, power_optimal, 'b--', label='ДП Мощность')
    axs[0].plot(time / 3600, w_tot, 'g-', label='ЭВ Мощность')
    axs[0].grid(True)
    axs[0].set_ylabel('Мощность, % Nном')
    axs[0].legend()

    # axs[1].plot(np.array(time_optimal) / 3600, hgrp_optimal1, 'mp-', label='Динамическое программирование2')
    axs[1].plot(time / 3600, h_total0, 'g-', label='ЭВ ОР СУЗ 12')
    axs[1].plot(time / 3600, h_total1, 'k-', label='ЭВ ОР СУЗ 11')
    axs[1].plot(np.array(time_optimal) / 3600, hgrp_optimal0, 'b--', label='ДП ОР СУЗ 12')
    axs[1].plot(np.array(time_optimal) / 3600, hgrp_optimal1, 'c--', label='ДП ОР СУЗ 11')

    axs[1].grid(True)
    axs[1].set_ylim(0, 1.1)
    axs[1].set_ylabel('Группы ОР СУЗ, о.е.')
    axs[1].legend()

    axs[2].plot(time / 3600, cb1, 'g-', label='ЭВ Концентрация борной кислоты')
    axs[2].plot(np.array(time_optimal) / 3600, cb_optimal, 'b--', label='ДП Концентрация борной кислоты')
    axs[2].grid(True)
    axs[2].set_ylabel('Концентрация\nборной кислоты, г/кг')
    axs[2].legend()
    axs[2].set_xlabel('Время, ч')

    plt.show()
