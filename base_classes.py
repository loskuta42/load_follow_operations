"""Базовые классы для работы с методом динамического программирования. """
import uuid


class State:
    """Состояние по модели активной зоны"""

    def __init__(
            self,
            time,
            w,
            h0,
            h1,
            # h2,
            cb,
            ro,
            ci,
            jod,
            xe
    ):
        self.time = time
        self.w = w
        self.h = [
            h0,
            h1,
            # h2
        ]
        self.cb = cb
        self.ro = ro
        self.ci = ci
        self.jod = jod
        self.xe = xe
        self.tin = 295
        self.p_in = 5
        self.id = 0

    def get_params(self):
        """Получить параметры из модели"""
        return self.time, self.w, self.h, self.cb, self.ro, self.ci, self.jod, self.xe

    def set_params(self, time, w, ro, ci, jod, xe):
        """Установить параметры в модель"""
        self.time = time
        self.w = w
        self.ro = ro
        self.ci = ci
        self.jod = jod
        self.xe = xe

    def __repr__(self):
        # return f"{self.time}    {self.w}    {self.h}    {self.cb}    {self.ro}    {self.ci}      {self.jod}      {self.xe}"
        return f"{self.time}    {self.w}    {self.h}    {self.cb} "  # {self.ro}    {self.ci}      {self.jod}      {self.xe}"

    def get_id(self):
        return self.id

    # def is_state_correct(self):
    #     return True

    def is_p_in_correct(self) -> bool:
        # от 5 до 7
        return 5 <= self.p_in <= 7

    def is_delta_p_correct(self) -> bool:
        #
        return True

    def is_hgrp_correct(self, hgrp_num: int = 0):
        """
        Проверка положения групп СУЗ.
        """
        return 0 <= self.h[hgrp_num] <= 0.5

    def is_t_in_correct(self):
        """
        Проверка возможности задания температуры.
        """
        return 292 <= self.tin <= 302

    def is_cb_correct(self):
        """Проверка возможности задания концентрации борной кислоты, концентрация подпитки (0 или 16 г/кг)
        return:"""
        return 0 <= self.cb <= 16

    def is_power_correct(self):
        return 0 <= self.w <= 1200


class Drive:
    """управление"""

    def __init__(self, nhgrp_step=1, tin=0, p_in=0, cb=0):
        """
        Инициализация.
        :param nhgrp_step: скорость движения ОР СУЗ - количество шагов привода за единичный
        отрезок времени, от 1 шага в секунду и более;
        :param cb: концентрация борной кислоты;
        :param tin: температура на входе в активную зону;
        :param p_in: давление на входе в активную зону.
        """
        self.nhgrp_step = nhgrp_step
        self.cb = cb

    # self.tin = tin
    # self.p_in = p_in
    def __repr__(self):
        return f"nhgrp_step:{self.nhgrp_step} cb:{self.cb}"  # \t{self.tin}\t{self.p_in} "

    # def is_drive_correct(self) -> bool:
    #     """
    #     Проверка корректности управления
    #     :return:
    #     """
    #     return self._is_hgrp_correct()

    def _is_hgrp_correct(self) -> bool:
        return True

    def _is_tin_correct(self) -> bool:
        """
        проверка возможности задания температуры
        :return:
        """
        return 292 < self.tin < 302

    def _is_p_in_correct(self) -> bool:
        return True

    def _is_cb_correct(self) -> bool:
        return True


class Track:
    """Путь из одного состояние в другое"""

    def __init__(self, parent_state, state, drive, parent_total_cost=0, cost=0):
        """
        инициализация
        :param parent_id: начальное состояние
        :param state: конечное состояние
        :param drive: управление для перехода из начального в конечное состояние
        :param cost: стоимость перехода
        :param parent_total_cost: стоимость от предыдущей части пути
        :param cost: стоимость за текущий переход, между parent_state и state
        """
        self.track_id = str(uuid.uuid1())
        self.parent_state = parent_state
        self.state = state
        self.drive = drive
        self.cost = cost
        self.total_cost = parent_total_cost + self.cost

        self._states_between_steps = []

    def __repr__(self):
        if self.parent_state is None:
            return f"Предыдущее состояние:{None}           {self.parent_state}\n" \
                   f"Текущее состояние: {self.state[0].id}         {self.state}\n" \
                   f"Управление: {self.drive}\n" \
                   f"Стоимость перехода между состояниями: {self.cost}\n" \
                   f"Стоимость перехода от начала: {self.total_cost} \n" \
                   f"----------------------------------------------------------------\n"
        else:
            return f"Предыдущее состояние:{self.parent_state[0].id}           {self.parent_state}\n" \
                   f"Текущее состояние: {self.state[0].id}         {self.state}\n" \
                   f"Управление: {self.drive}\n" \
                   f"Стоимость перехода между состояниями: {self.cost}\n" \
                   f"Стоимость перехода от начала: {self.total_cost} \n" \
                   f"----------------------------------------------------------------\n"

    def is_start_track(self):
        """Проверка. Является ли данный трек начальным."""
        if self.drive is None:
            return True
        else:
            return False
