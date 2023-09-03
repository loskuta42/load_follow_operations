"""Класс для расчета эвристик."""
from scipy import interpolate
import numpy as np
from copy import deepcopy
from tools import get_water_discarge, get_cost_by_power


class Evristic:
    def __init__(self, model, load_follow_operations, dt=3600, dw_cbor=0.9, dw_hgrp=0.1, strategy_type=0,
                 optimization_type=0):
        self.model = model
        self.dw_cbor = dw_cbor
        self.dw_hgrp = dw_hgrp
        self.dt = dt

        self.load_follow_time = load_follow_operations.transpose()[0]
        print(self.load_follow_time)
        self.time_beg = self.load_follow_time[0]
        # делаем, чтобы время у нас начиналось с нуля
        self.load_follow_time = self.load_follow_time - self.time_beg
        self.time_beg = self.load_follow_time[0]
        self.time_end = self.load_follow_time[-1]
        # self.time_steps = np.arange(self.time_beg, self.time_end+dt, self.dt)
        self.time_steps = self.load_follow_time

        self.load_follow_power = load_follow_operations.transpose()[1]
        # создание интерполяционной функции для получения значений графика нагрузки в любой момент времени
        self.pow_int_fun = interpolate.interp1d(self.load_follow_time, self.load_follow_power, fill_value="extrapolate")

        self.results = []
        self.model.clear_file('log_evr.txt')

        self.strategy_type = strategy_type  # выбор типа стратегии управления

        self.optimization_type = optimization_type

    def calc_evristic_with_little_step(self):
        time_curr = self.time_beg
        discharge = 0
        total_cost = 0
        kratnost = 4  # кратность чередования управления
        save_info_kratnost = 100  # кратность записи шагов в файл для построения графиков
        istep = 0
        for time in self.time_steps[1:]:
            # start_states = deepcopy(self.model.get_states())
            while time_curr <= time:
                pow_curr = self.pow_int_fun(time_curr)

                start_states = deepcopy(self.model.get_states())

                # через сколько шагов можем двинуться группой
                # if istep % kratnost == 0:
                #     # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.model.come_to_the_desired_power_by_control_grp(w=pow_curr, dw=self.dw_hgrp,
                                                                    strategy_type=self.strategy_type)
                self.model.step()
                time_curr = time_curr + self.model._delt

                self.model.come_to_the_desired_power_by_boric_acid(w=pow_curr, dw=self.dw_cbor)
                self.model.step()
                time_curr = time_curr + self.model._delt

                end_states = deepcopy(self.model.get_states())
                if self.optimization_type == 0:
                    discharge_curr = get_water_discarge(cb_beg=start_states[0].cb, cb_end=end_states[0].cb)
                    discharge = discharge + discharge_curr

                    self.results.append([time_curr, end_states, discharge_curr, discharge])
                elif self.optimization_type == 1:

                    cost = get_cost_by_power(w_nagruzka=self.pow_int_fun(time_curr),
                                             w_current=self.model.get_w_tot())
                    total_cost += cost

                    self.results.append([time_curr, end_states, cost, total_cost])

                # записываем каждый какой-то шаг в файл
                # if istep % save_info_kratnost == 0:
                self.model.print_result_in_file('log_evr.txt')

                istep = istep + 1
            print(f"EV_time: {time}")


if __name__ == '__main__':
    from two_point_model import Model, State

    model = Model(nnodes=2)
    model._delt = 2
    w0 = 50
    st1 = State(
        time=0,
        w=w0,
        h0=0.2,
        h1=0,
        # h2=0,
        cb=7,
        ro=0,
        ci=None,
        jod=None,
        xe=None
    )
    st1.ci = model.calc_static_ci_in_node(w=w0)
    st1.jod, st1.xe = model.calc_ravn_jod_and_xe_in_node(w=w0)
    # print(st1.jod, st1.xe)

    st2 = State(
        time=0,
        w=w0,
        h0=0,
        h1=0,
        # h2=0,
        cb=7,
        ro=0,
        ci=None,
        jod=None,
        xe=None
    )
    st2.ci = model.calc_static_ci_in_node(w=w0)
    st2.jod, st2.xe = model.calc_ravn_jod_and_xe_in_node(w=w0)

    model.set_state(0, st1)
    model.set_state(1, st2)

    load_follow_operations = np.array(
        [[0 * 3600, 100],
         [1 * 3600, 75],
         [2 * 3600, 50],
         [12 * 3600, 50],
         [13 * 3600, 75],
         [14 * 3600, 100],
         [18 * 3600, 100],
         [24 * 3600, 100],
         # [2 * 3600, 70],
         # [3 * 3600, 70],
         # [4 * 3600, 70],
         # [5 * 3600, 70],
         # [6 * 3600, 70],
         # [7 * 3600, 85],
         # [8 * 3600, 100],
         # [9 * 3600, 100],
         # [10 * 3600, 100],
         # [11 * 3600, 100],
         # [12 * 3600, 100],
         # [13 * 3600, 75],
         # [14 * 3600, 70],
         # [15 * 3600, 70],
         # [16 * 3600, 75],
         # [17 * 3600, 80],
         # [18 * 3600, 85],
         # [19 * 3600, 95],
         # [20 * 3600, 100],
         # [21 * 3600, 95],
         # [22 * 3600, 95],
         # [23 * 3600, 100],
         # [24 * 3600, 100],
         ]
    )

    evr_obj = Evristic(model, load_follow_operations, dt=3600, dw_cbor=0.9, dw_hgrp=0.1, strategy_type=0)
    evr_obj.calc_evristic_with_little_step()

    evr_obj.model.build_graph(file_name='log_evr.txt')
    res = np.array(evr_obj.results)
    time_evr = res[:, 0]
    discharge_evr = res[:, -1]

    pow_int_fun = evr_obj.pow_int_fun
    data = np.genfromtxt('log_evr.txt')

    time = data[:, 0]

    nagruzka_graph = [pow_int_fun(t) for t in time]
    total_power = data[:, 1]

    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(2, 1)
    axs[0].plot(time, nagruzka_graph, 'r-', label='Load schedule')
    axs[0].plot(time, total_power, 'g-', label='Power')
    axs[0].grid(True)
    axs[1].plot(time_evr, discharge_evr, 'g-', label='Total Discharge')

    plt.ylabel('Power, %')
    plt.legend()
    axs[1].grid(True)
    plt.legend()

    # axs[1].plot(time, AO_up, 'r-', label='Top limit of\naxial offset')
    # axs[1].plot(time, AO_dn, 'b-', label='Bottom limit of\naxial offset')
    # axs[1].plot(time, AO, 'g-', label='Axial offset')
    # axs[1].set_ylabel('Axial offset, %')
    # axs[1].set_xlabel('Time, h')
    # axs[1].legend()
    # axs[1].grid(True)
    # axs[1].legend()
    plt.show()
