from typing import Optional

import numpy as np
from copy import deepcopy
from base_classes import State


class Model:
    def __init__(self, nnodes=2):
        self._beta = 0.0068  # доля запаздывающих нейтронов
        self._lam = 1 / 13.07  # 13.07 с - среднее время запаздывания при рождении запаздывающих нейтронов
        self._delt = 0.1  # шаг по времени при расчете, с
        self._alfa_w = -2e-5
        self._life_time = 0.0001  # время жизни мгновенных нейтронов, с
        self._sigma_del = 0.3358  # sm-1
        self._const_rasp_xe = 2.1065742176025565e-05  # s-1
        self._const_rasp_jod = 2.93060705462517e-05  # s-1
        self._vihod_xe = 2.68296e-03
        self._vihod_jod = 6.27765e-02
        self._neutron_flow_koef = 1e10  # 1/sm2*s
        self._mcs_xe = 3e-18
        self._alfa_xe = -self._mcs_xe / self._sigma_del
        self._alfa_cb = (-0.00163) / (5.2 - 5.11413) * self._beta
        self.ro_for_all_suz_length = [
            self._beta * (-0.05),
            self._beta * (-0.2),
            # self._beta * (-0.4)
        ]
        self.h_total = [0, 0, 0]  # начальная позиция группы ОР СУЗ

        self._states: dict[Optional[int, State]] = {}
        for ind in range(nnodes):
            self._states[ind] = None

        self.offset_stable = -5  # [%], равновесный офсет на 100 % мощности
        self.AO_up = 0
        self.AO_dn = 0

        self.clear_file()

    def set_stable_AO(self, offset_stable):
        """Установка офсета, при котором блок долго проработал на постоянной мощности."""
        self.offset_stable = offset_stable

    def get_bor_current_concentration(self, c_podpit, c_beg):
        """Получение текущего значения борной кислоты в контуре
        c_podpit - концентрация борной кислоты на линии подпитки (0 или 40), г/кг
        c_beg - текущая концентрация борной кислоты в контуре
        dt - время подпитки в секундах"""
        G = 20  # т/ч
        V = 300  # м3
        Ro = 738  # кг/м3 или 0,738 Т/м3
        dt = 1
        kompl = G * dt / (V * Ro)  # должно быть?(20/3600* 1/300*0.738) =
        c_end = np.exp(-kompl) * (c_podpit * (np.exp(kompl) - 1) + c_beg)
        return c_end

    def set_ro_from_bor(self, bor_conc: list):
        """
        Ввод борной кислоты.
        :param bor_conc: - концентрация бора в нодах 0-16, г/кг
        """
        # установим новое значение борной кислоты в ноды
        nnodes = len(self._states)
        for ind in range(nnodes):
            cb_curr = self._states[ind].cb
            cb_in_node = bor_conc[ind]
            cb_val = cb_in_node

            self._states[ind].cb = cb_val
            delta_ro_cb = self._alfa_cb * (cb_val - cb_curr)
            self._states[ind].ro += delta_ro_cb

    def come_to_the_desired_power_by_boric_acid(self, w, dw=0.9):
        """Приведение блока к желаемой мощности за счет борной кислоты"""
        # if evristick:
        wtot = self.get_w_tot()
        delta_pow = w - wtot
        # for ind in range(nnodes):
        cb_curr = self.get_cb()
        c_end = cb_curr
        if delta_pow > dw:
            c_end = self.get_bor_current_concentration(c_podpit=0, c_beg=cb_curr)
            # self.set_ro_from_bor([c_end, c_end])
        if delta_pow < -dw:
            c_end = self.get_bor_current_concentration(c_podpit=40, c_beg=cb_curr)
            # self.set_ro_from_bor([c_end, c_end])
        self.set_ro_from_bor([c_end, c_end])

    def come_to_the_desired_power_by_control_grp(self, w, dw=0.1, strategy_type=0):
        """Приведение блока к желаемой мощности за счет ОР СУЗ.
        :param dw: величина отклонения от графика нагрузки;
        :param dh: скорость движения групп о.е./с;
        :param strategy_type -тип используемой стратегии управления
        """
        wtot = self.get_w_tot()
        delta_pow = w - wtot
        offset = self.get_AO()

        dh = 0.005  # шаг привода ОР СУЗ: 2см/с

        is_Ao_in_boundaries, dn_boundary, up_boundary = self.AO_in_limit(wtot, offset)
        if is_Ao_in_boundaries:
            if strategy_type == 0:  # индивидуальное управление рабочей группой
                self.individual_grup_move(delta_pow, dw, dh, hgrp_num=0)
            elif strategy_type == 1:  # индивидуальное управление рабочей группой -1
                self.individual_grup_move(delta_pow, dw, dh, hgrp_num=1)
            elif strategy_type == 2:  # перехват на 50% и остановка движения группы на 50%
                self.perexvat_ir(delta_pow, dw, dh)
            elif strategy_type == 3:  # стандартное движение на 50% и остановка движения группы на 10
                self.standart_perexvat(delta_pow, dw, dh)

    def perexvat_ir(self, delta_pow, dw, dh):
        """Ввод положений по ОР СУЗ - стратегия перехвата на 50% и остановка движения группы на 50%,
        или стратегия управления по ИР
        delta_pow - отклонение текущей мощности от графика нагрузки, %
        dw - уставка отклонени текущей мощности от графика нагрузки, %
        dh - шаг по ОР СУЗ, например 2 см/с"""
        if delta_pow > dw:
            self.set_ro_from_h_perexvat(dh * (-1))
        if delta_pow < -dw:
            self.set_ro_from_h_perexvat(dh)

    def standart_perexvat(self, delta_pow, dw, dh):
        """Ввод положений по ОР СУЗ -  штатное регулирование мощностью, начало движения следующей
        группы после пересечения граничного значения в 0.5 о.е. от длины ОР СУЗ
        delta_pow - отклонение текущей мощности от графика нагрузки, %
        dw - уставка отклонени текущей мощности от графика нагрузки, %
        dh - шаг по ОР СУЗ, например 2 см/с"""
        if delta_pow > dw:
            self.set_ro_from_h_standart(dh * (-1))
        if delta_pow < -dw:
            self.set_ro_from_h_standart(dh)

    def individual_grup_move(self, delta_pow, dw, dh, hgrp_num):
        """Ввод положений по ОР СУЗ - индивидуальное движениу группами ОР СУЗ
        delta_pow - отклонение текущей мощности от графика нагрузки, %
        dw - уставка отклонени текущей мощности от графика нагрузки, %
        dh - шаг по ОР СУЗ, например 2 см/с
        hgrp_num - выбор номера группы на управление"""
        if delta_pow > dw:
            self.set_ro_from_h_individual(dh * (-1), hgrp_num)
        if delta_pow < -dw:
            self.set_ro_from_h_individual(dh, hgrp_num)

    def come_to_end_state_by_bodic_acid(self, w):
        wtot = 0
        nnodes = len(self._states)
        for ind in range(nnodes):
            wtot += self._states[ind].w
        c_end = None
        for ind in range(nnodes):
            cb_curr = self._states[ind].cb
            if wtot < w:
                c_end = self.get_bor_current_concentration(c_podpit=0, c_beg=cb_curr)
            elif wtot == w:
                c_end = cb_curr
            else:
                c_end = self.get_bor_current_concentration(c_podpit=40, c_beg=cb_curr)

        self.set_ro_from_bor([c_end, c_end])

    def can_this_cb_be_reached(self, cb_new, cb_curr):
        # получим новое значение борной кислоты на шаге
        # вопрос в ограничении возможности изменения концентрации борной кислоты
        # борная кислоты не может стать какой угодно
        if cb_new < cb_curr:
            c_end = self.get_bor_current_concentration(c_podpit=0, c_beg=cb_curr)
            if cb_new < c_end:
                return False, c_end
            else:
                return True, cb_new
        # elif cb_new == cb_curr:
        #     return True, cb
        else:
            c_end = self.get_bor_current_concentration(c_podpit=40, c_beg=cb_curr)
            if c_end < cb_new:
                return False, c_end
            else:
                return True, cb_new

    def Calc_AO_limits(self, power):
        """Расчет границ офсет-мощностной диаграммы.
        :param power: текущая мощность, [% от Nном]
        """
        AO_cent_curr = -2.6 + (self.offset_stable + 2.6) * power / 100
        #AO_up = -2.6 + (AO_cent_curr + 7.6) * 100 / power
        AO_up = -2.6 + (AO_cent_curr + 7.6 + 5  ) * 100 / power  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! внесли правку по офсету !!!!!!!!!!!!!!!!!!!!!!
        #AO_dn = -2.6 + (AO_cent_curr - 2.4) * 100 / power
        AO_dn = -2.6 + (AO_cent_curr - 2.4 - 5) * 100 / power
        self.AO_up = AO_up
        self.AO_dn = AO_dn
        return AO_up, AO_dn

    def AO_in_limit(self, pow, AO_curr):
        """Определяем - находимся ли мы внутри офсет-мощностной диаграммы
        pow текущая мощность [% от Nном]
        AO_curr текущий офсет, [%]
        """
        AO_up, AO_dn = self.Calc_AO_limits(pow)
        dn_boundary = False
        up_boundary = False

        if AO_dn < AO_curr and AO_curr < AO_up:
            AO_is_in = True
            dn_boundary = False
            up_boundary = False
        else:
            AO_is_in = False
            if AO_curr < AO_dn:
                dn_boundary = True
            if AO_up < AO_curr:
                up_boundary = True
        return AO_is_in, dn_boundary, up_boundary

    def suz_decompoze_individual(self, dh, hgrp_num: int = 0):
        """Установка позиции ОР СУЗ в нодах по прирщению dh"""
        nnodes = len(self._states)
        h_prev_lst = []
        self.h_total = [0] * len(self._states[0].h)
        for ind in range(nnodes):
            self.h_total[hgrp_num] += self._states[ind].h[hgrp_num]
            h_prev_lst.append(self._states[ind].h[hgrp_num])

        h_curr = self.h_total[hgrp_num] + dh

        # учет недохода ор суз до нижнего концевика
        if h_curr > 0.939:
            h_curr = 0.939
        elif h_curr < 0:
            h_curr = 0

        h_node = 1 / nnodes
        h_curr_lst = []

        # расстановка положений ОР СУЗ в каждый нод
        for ind in range(nnodes):
            if 0 < h_curr < h_node:
                h_curr_lst.append(h_curr)
                h_curr -= h_node
            elif h_curr > 0:
                h_curr_lst.append(h_node)
                h_curr -= h_node
            else:
                h_curr_lst.append(0)
        return h_curr_lst, h_prev_lst

    def set_ro_from_h_individual(self, dh, hgrp_num: int = 0):
        """Устанавливаем новую глубину погружения ОР СУЗ за счет ввода приращения в положении dh"""
        h_curr_lst, h_prev_lst = self.suz_decompoze_individual(dh, hgrp_num)

        # у верхней ноды индекс 0
        nnodes = len(self._states)
        ro_h_in_node = np.zeros(nnodes)
        for ind in range(nnodes):
            if h_curr_lst[ind] != 0 or h_prev_lst[ind] != 0:
                delta = h_curr_lst[ind] - h_prev_lst[ind]
                ro_h_in_node[ind] = delta * self.ro_for_all_suz_length[hgrp_num]
                self._states[ind].h[hgrp_num] = h_curr_lst[ind]
                self._states[ind].ro += ro_h_in_node[ind]

        self.h_total[hgrp_num] = sum(h_curr_lst)

    def suz_decompoze_perexvat(self, dh):
        """Установка позиции ОР СУЗ в нодах по прирщению dh"""
        nnodes = len(self._states)
        h_prev_lst = []
        self.h_total = [0] * len(self._states[0].h)
        self.h_up_for_all_groups = deepcopy(self._states[0].h)
        for ind in range(nnodes):
            h_for_node = []
            for indx, hgrp in enumerate(self._states[ind].h):
                self.h_total[indx] += self._states[ind].h[indx]
                h_for_node.append(hgrp)
            h_prev_lst.append(h_for_node)

        max_hgrp_level = 0.5
        if dh >= 0:
            start_index = None
            for indx, hgrp in enumerate(self.h_total):
                if 0 < hgrp < 0.5:
                    start_index = indx
                    break
            # Ввод ОР СУЗ
            if start_index is None:
                h_curr_lst = h_prev_lst
                return h_curr_lst, h_prev_lst
            start_ind = start_index


            temp_dh = dh
            h_curr = deepcopy(self.h_total)
            # перехват
            for ind in range(start_ind, len(self._states[0].h)):
                if temp_dh == 0:
                    h_curr_lst = h_prev_lst
                    return h_curr_lst, h_prev_lst
                h_curr[ind] += temp_dh
                if h_curr[ind] <= max_hgrp_level:
                    break
                else:
                    temp_dh = h_curr[ind] - max_hgrp_level
                    h_curr[ind] = max_hgrp_level
        else:
            # Вывод ОР СУЗ
            start_index = None
            for indx in range(len(self.h_total)-1, -1, -1):
                if 0 < self.h_total[indx] < 0.5:
                    start_index = indx
                    break
            if start_index is None:
                start_ind = len(self.h_total) - 1
            else:
                start_ind = start_index
            temp_dh = dh
            h_curr = deepcopy(self.h_total)

            for ind in range(start_ind, -1, -1):
                h_curr[ind] += temp_dh
                if 0 <= h_curr[ind] <= max_hgrp_level:
                    break
                else:
                    temp_dh = h_curr[ind]
                    h_curr[ind] = 0

        h_node = 1 / nnodes
        h_curr_lst = [[], []]

        for hgrp in range(len(self._states[0].h)):
            for ind in range(nnodes):
                if 0 < h_curr[hgrp] < h_node:
                    h_curr_lst[ind].append(h_curr[hgrp])
                    h_curr[hgrp] -= h_node
                elif h_curr[hgrp] > 0:
                    h_curr_lst[ind].append(h_node)
                    h_curr[hgrp] -= h_node
                else:
                    h_curr_lst[ind].append(0)
        return h_curr_lst, h_prev_lst

    def set_ro_from_h_perexvat(self, dh):
        """Устанавливаем новую глубину погружения ОР СУЗ за счет ввода приращения в положении dh"""
        h_curr_lst, h_prev_lst = self.suz_decompoze_perexvat(dh)

        # у верхней ноды индекс 0
        nnodes = len(self._states)
        ro_h_in_node = [0] * nnodes
        self.h_total = [0] * len(self._states[0].h)
        for hgrp in range(len(self._states[0].h)):
            for ind in range(nnodes):
                if h_curr_lst[ind][hgrp] != 0 or h_prev_lst[ind][hgrp] != 0:
                    delta = h_curr_lst[ind][hgrp] - h_prev_lst[ind][hgrp]
                    ro_h_in_node[ind] += delta * self.ro_for_all_suz_length[hgrp]
                    self._states[ind].h[hgrp] = h_curr_lst[ind][hgrp]
                    self.h_total[hgrp] += h_curr_lst[ind][hgrp]

        for ind in range(nnodes):
            self._states[ind].ro += ro_h_in_node[ind]

    def suz_decompoze_standart(self, dh):
        """Установка позиции ОР СУЗ в нодах по прирщению dh"""
        nnodes = len(self._states)
        h_prev_lst = []
        self.h_total = [0] * len(self._states[0].h)
        for ind in range(nnodes):
            h_for_node = []
            for indx, hgrp in enumerate(self._states[ind].h):
                self.h_total[indx] += self._states[ind].h[indx]
                h_for_node.append(hgrp)
            h_prev_lst.append(h_for_node)
        # Ввод ОР СУЗ
        if dh > 0:
            max_hgrp_level = 0.939
            for indx, hgrp in enumerate(self.h_total):
                if hgrp < max_hgrp_level:
                    start_index = indx
                    break
            next_ind = None
            try:
                start_ind = start_index
                for ind in range(start_ind + 1, len(self.h_total)):
                    if self.h_total[ind] < max_hgrp_level:
                        next_ind = ind
                        break
                # if start_ind + 1 < len(self._states[0].h):
                #     next_ind = start_ind + 1
            except NameError:
                h_curr_lst = h_prev_lst
                return h_curr_lst, h_prev_lst

            h_curr = deepcopy(self.h_total)
            if h_curr[start_ind] > 0.5 and next_ind:
                h_curr[start_ind] += dh
                if (h_curr[next_ind] + dh) > 0.5:
                    h_curr[next_ind] = 0.5
                h_curr[next_ind] += dh
            else:
                h_curr[start_ind] += dh
                if h_curr[start_ind] > 0.5 and next_ind:
                    if (h_curr[next_ind] + (h_curr[start_ind] - 0.5)) > 0.5:
                        h_curr[next_ind] = 0.5
                    h_curr[next_ind] += (h_curr[start_ind] - 0.5)
                    if h_curr[next_ind] > max_hgrp_level:
                        h_curr[next_ind] = max_hgrp_level
            if h_curr[start_ind] > max_hgrp_level:
                h_curr[start_ind] = max_hgrp_level
        # Вывод ОР СУЗ
        elif dh < 0:
            for indx in range(len(self.h_total) - 1, -1, -1):
                if self.h_total[indx] > 0:
                    start_index = indx
                    break
            prev_ind = None
            try:
                start_ind = start_index
                for ind in range(start_ind - 1, -1, -1):
                    if self.h_total[ind] > 0:
                        prev_ind = ind
                        break
            except NameError:
                h_curr_lst = h_prev_lst
                return h_curr_lst, h_prev_lst
            h_curr = deepcopy(self.h_total)
            if h_curr[start_ind] < 0.5 and prev_ind:
                if h_curr[start_ind] > 0 and h_curr[start_ind] > abs(dh):
                    h_curr[start_ind] += dh
                else:
                    h_curr[start_ind] = 0
                if h_curr[prev_ind] > 0 and h_curr[prev_ind] > abs(dh):
                    h_curr[prev_ind] += dh
                else:
                    h_curr[prev_ind] = 0
            else:
                h_curr[start_ind] += dh
                if h_curr[start_ind] < 0.5 and prev_ind:
                    if h_curr[prev_ind] > 0 and (0.5 - h_curr[start_ind]) < h_curr[prev_ind]:
                        h_curr[prev_ind] -= (0.5 - h_curr[start_ind])
                    else:
                        h_curr[prev_ind] = 0
            if h_curr[start_ind] < 0:
                h_curr[start_ind] = 0
        else:
            h_curr_lst = h_prev_lst
            return h_curr_lst, h_prev_lst
        h_node = 1 / nnodes
        h_curr_lst = [[], []]

        for hgrp in range(len(self._states[0].h)):
            for ind in range(nnodes):
                if 0 < h_curr[hgrp] < h_node:
                    h_curr_lst[ind].append(h_curr[hgrp])
                    h_curr[hgrp] -= h_node
                elif h_curr[hgrp] > 0:
                    h_curr_lst[ind].append(h_node)
                    h_curr[hgrp] -= h_node
                else:
                    h_curr_lst[ind].append(0)
        return h_curr_lst, h_prev_lst

    def set_ro_from_h_standart(self, dh):
        """Устанавливаем новую глубину погружения ОР СУЗ за счет ввода приращения в положении dh."""
        h_curr_lst, h_prev_lst = self.suz_decompoze_standart(dh)

        # у верхней ноды индекс 0
        nnodes = len(self._states)
        ro_h_in_node = [0] * nnodes
        self.h_total = [0] * len(self._states[0].h)
        for hgrp in range(len(self._states[0].h)):
            for ind in range(nnodes):
                if h_curr_lst[ind][hgrp] != 0 or h_prev_lst[ind][hgrp] != 0:
                    delta = h_curr_lst[ind][hgrp] - h_prev_lst[ind][hgrp]
                    ro_h_in_node[ind] += delta * self.ro_for_all_suz_length[hgrp]
                    self._states[ind].h[hgrp] = h_curr_lst[ind][hgrp]
                    self.h_total[hgrp] += h_curr_lst[ind][hgrp]

        for ind in range(nnodes):
            self._states[ind].ro += ro_h_in_node[ind]

    def calc_static_ci_in_node(self, w):
        """Расчет равновесной концентрации эммитеров запаздывающих нейтронов"""
        self._beta = 0.0068  # доля запаздывающих нейтронов
        self._lam = 1 / 13.07  # 13.07 с - среднее время запаздывания при рождении запаздывающих нейтронов
        self._life_time = 0.0001  # время жизни мгновенных нейтронов с
        ci = w * self._beta / self._life_time / self._lam
        return ci

    def calc_ravn_jod_and_xe_in_node(self, w):
        """Расчет равновесной концентрации J и Xe"""
        jod_conc = (self._vihod_jod * self._sigma_del * w * self._neutron_flow_koef) / self._const_rasp_jod

        chisl = (self._vihod_xe * self._sigma_del * w * self._neutron_flow_koef) + (self._const_rasp_jod * jod_conc)
        znam = (self._mcs_xe * w * self._neutron_flow_koef) + self._const_rasp_xe
        xe_conc = chisl / znam
        return jod_conc, xe_conc

    def step(self):
        """Шаг модели"""
        for key in self._states.keys():
            state = self._states[key]

            time, w, h, cb, ro, ci, jod, xe = state.get_params()

            # w_next = (w + (self._delt * self._lam * ci) / (1 + self._delt * self._lam)) / (
            #         1 - self._delt / self._life_time * (
            #         ro - self._beta + self._delt * self._lam * self._beta / (
            #         1 + self._delt * self._lam)))  # Наумов ф.2.3.3 без источника

            ci_next = (ci + self._delt * self._beta * w / self._life_time) / (
                    1 + self._delt * self._lam)  # (Наумов ф.2.3.4)

            if ci_next < 0:
                ci_next = 0

            w_next = (w + self._delt * self._lam * ci_next) / (
                    1 - (ro - self._beta) * self._delt / self._life_time)  # Наумов ф.2.3.3 без источника

            if w_next < 0:
                w_next = 0

            jod_next = (jod + self._vihod_jod * self._sigma_del * w_next * self._neutron_flow_koef * self._delt) / (
                    1 + self._const_rasp_jod * self._delt)

            if jod_next < 0:
                jod_next = 0

            xe_next = xe + self._delt * ((self._vihod_xe * self._sigma_del * w_next * self._neutron_flow_koef) +
                                         (jod_next * self._const_rasp_jod) -
                                         (self._mcs_xe * w_next * self._neutron_flow_koef * xe) -
                                         (self._const_rasp_xe * xe))

            if xe_next < 0:
                xe_next = 0

            # self._alfa_xe *(xe_next - 0)  приблизительно 0.0294
            delta_ro_xe = self._alfa_xe * (xe_next - xe)
            # в ro уже утчено изменение реактивности за счет ор суз и за счет борной кислоты
            delta_ro_w = self._alfa_w * (w_next - w)
            ro_next = ro + delta_ro_w + delta_ro_xe

            # Мощностная обратная связь

            time_next = time + self._delt
            state.set_params(time=time_next, w=w_next, ro=ro_next, ci=ci_next, jod=jod_next, xe=xe_next)
            self._states[key] = state

    @staticmethod
    def clear_file(file_name='log.txt'):
        with open(file_name, 'w'):
            pass

    def get_AO(self):
        """Получение офсета мощности"""
        total_power = self.get_total_power() + 1e-15

        AO = (self._states[0].w - self._states[1].w) / total_power * 100
        return AO

    def get_cb(self):
        """Получить концентрацию борной кислоты"""
        return self._states[0].cb

    def get_total_power(self):
        total_power = self._states[0].w + self._states[1].w
        return total_power

    def print_result_in_file(self, file_name='log.txt'):
        total_power = self.get_total_power()
        AO = self.get_AO()

        time1, w1, h1, cb1, ro1, ci1, jod1, xe1 = self._states[0].get_params()
        time2, w2, h2, cb2, ro2, ci2, jod2, xe2 = self._states[1].get_params()
        with open(file_name, 'a') as f:
            f.write(f'{time1}\t{total_power}\t{AO}\t')
            f.write(f'{w1}\t{h1[0]}\t{h1[1]}\t{cb1}\t{ro1}\t{ci1}\t{jod1}\t{xe1}\t')
            f.write(f'{w2}\t{h2[0]}\t{h2[1]}\t{cb2}\t{ro2}\t{ci2}\t{jod2}\t{xe2}\t')
            f.write(f'{self.AO_up}\t{self.AO_dn}\n')

    def get_w_tot(self):
        """Получение полной мощности"""
        w_tot = 0
        nnodes = len(self._states)
        for ind in range(nnodes):
            w_tot += self._states[ind].w
        return w_tot

    def get_states(self):
        return deepcopy(self._states)

    def set_state(self, inode: int, state: Optional[State]):
        """Установка состояния в один расчетный нод"""
        self._states[inode] = state

    def set_global_states(self, states):
        """Установка состояния во все ноды сразу"""
        self._states = deepcopy(states)

    def get_model_time(self):
        return self._states[0].time

    def is_state_correct(self) -> bool:
        """Проверка корректности состояния модели"""
        w_tot = self.get_w_tot()
        AO = self.get_AO()
        if self.AO_in_limit(w_tot, AO)[0]:  # отсечение по офсету
            return True
        else:
            return False

    @staticmethod
    def build_graph(file_name="log.txt"):
        import matplotlib.pyplot as plt

        data = np.genfromtxt(file_name)

        time = data[:, 0]
        w_tot = data[:, 1]
        AO = data[:, 2]

        w1 = data[:, 3]
        h10 = data[:, 4]
        h11 = data[:, 5]
        # h12 = data[:, 6]
        cb1 = data[:, 6]
        ro1 = data[:, 7]
        ci1 = data[:, 8]
        jod1 = data[:, 9]
        xe1 = data[:, 10]

        w2 = data[:, 11]
        h20 = data[:, 12]
        h21 = data[:, 13]
        # h22 = data[:, 15]
        cb2 = data[:, 14]
        ro2 = data[:, 15]
        ci2 = data[:, 16]
        jod2 = data[:, 17]
        xe2 = data[:, 18]
        h_total0 = h10 + h20
        h_total1 = h11 + h21
        # h_total2 = h12 + h22
        h_total0 = 1 - h_total0
        h_total1 = 1 - h_total1
        # h_total2 = 1 - h_total2

        fig, axs = plt.subplots(4, 1)
        axs[0].plot(time, w_tot, "r-")
        # axs[0].set_xlabel('Время, с')
        axs[0].set_ylabel('Power, %')
        # axs[0].legend()
        axs[0].grid(True)

        axs[2].plot(time, h_total0, "g-", label="h0")
        axs[2].plot(time, h_total1, "b-", label="h1")
        # axs[2].plot(time, h_total2, "m-", label="h2")
        # axs[2].plot(time, h_total2, "r-")
        axs[2].set_xlabel('Time, h')
        axs[2].set_ylabel('control rod hgrp\nimmersion rate')
        axs[2].legend()
        axs[2].grid(True)

        axs[1].plot(time, cb1, "b-")
        # axs[1].set_xlabel('Время, с')
        axs[1].set_ylabel('Boric acid\nconcentration, g/kg')
        # axs[1].legend()
        axs[1].grid(True)

        axs[3].plot(time / 3600, xe1, "g-", label="xe1")
        axs[3].plot(time / 3600, xe2, "b-", label="xe2")
        axs[3].set_ylabel('xe')
        axs[3].legend()
        axs[3].grid(True)

        plt.show()


if __name__ == '__main__':
    model = Model(nnodes=2)
    model._delt = 1
    w0 = 50
    st1 = State(
        time=0,
        w=w0,
        h0=0.2,
        h1=0.2,
        # h2=0.3,
        cb=7,
        ro=0,
        ci=None,
        jod=None,
        xe=None
    )
    st1.ci = model.calc_static_ci_in_node(w=w0)
    st1.jod, st1.xe = model.calc_ravn_jod_and_xe_in_node(w=w0)
    print(st1.jod, st1.xe)

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

    # model.heuristic(90, 0, 10000)
    # model.set_ro_from_bor(bor_conc=[7.3, 7.3])

    for el in range(7200):
        # for el in range(400):
        model.step()
        model.print_result_in_file()
        if el % 10000 == 0:
            print(el)

    model.set_ro_from_h_perexvat(dh=0.2)

    # model.print_result_in_file()
    for el in range(7200):
        # for el in range(400):
        model.step()
        model.print_result_in_file()
        if el % 10000 == 0:
            print(el)

    model.set_ro_from_h_perexvat(dh=0.7)
    # model.set_ro_from_bor(bor_conc=[7, 7])

    for el in range(7200):
        # for el in range(400):
        model.step()
        model.print_result_in_file()
        if el % 10000 == 0:
            print(el)

    model.set_ro_from_h_perexvat(dh=-0.2)

    for el in range(15000):
        # for el in range(400):
        model.step()
        model.print_result_in_file()
        if el % 10000 == 0:
            print(el)

    model.build_graph()
