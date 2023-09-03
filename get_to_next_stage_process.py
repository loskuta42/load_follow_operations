import pickle
from multiprocessing import Process, Queue, Semaphore
from typing import Callable

import lmdb

from tools import get_water_discarge, get_cost_by_power
from base_classes import Track


class GetNewTracksProcess(Process):
    """Процесс получения новых треков."""
    def __init__(
            self,
            models_queue: Queue,
            semaphore: Semaphore,
            track,
            cur_stage_time,
            next_stage_time,
            result_queue: Queue,
            drive_list: list,
            pow_int_fun: Callable,
            optimize_type: int,
            evr_cost: float,
            evr_states: dict,
            last_lf_op,
    ):
        """

        :param models_queue: очередь моделей, которые будем запускать
        :param semaphore: семафор для синхронизации - кол-во открытий равно количеству моделей
        :param track: трек из которого строятся новые треки
        :param cur_stage_time: время начала текущей стадии
        :param next_stage_time: время конца текущей стадии
        :param result_queue: результирующая очередь - новый список треков (кортеж: список новых полученных треков, сколько всего было рассчитано состояний и сколько отсечено)
        :param drive_list: спсиок возможных стратегий управлений
        :param pow_int_fun: интерполяционная функция графика несения нагрузки
        :param optimize_type: тип оптимизации: водообмен или энерговыбработка
        :param evr_cost: общая стоимость эвристики
        :param evr_states: конечное состояние для эвристики
        :param last_lf_op: конечное значение мощности из графика несения нагрузки
        """
        super().__init__()
        self.models_queue = models_queue
        self.semaphore = semaphore
        self.track = track
        self.cur_stage_time = cur_stage_time
        self.next_stage_time = next_stage_time
        self.result_queue = result_queue
        self.drive_list = drive_list
        self.pow_int_fun = pow_int_fun
        self.optimize_type = optimize_type
        self.discard_by_evristic = 0
        self.evr_cost = evr_cost
        self.evr_states = evr_states
        self.last_lf_op = last_lf_op

    def _get_new_track(self, track, drive, model, cur_stage_time, next_stage_time):
        """Получение нового состояния.
        :param track: предыдущий трек;
        :param drive: управление для построения нового трека"""
        new_st = model.get_states()

        # проверим корректность и осуществимость управления
        track_total_cost = 0

        print(f"\tbegin_state: {track.state[0].cb}")

        # if drive.is_drive_correct():
        # установим в модель в новое состояние
        model.set_global_states(track.state)

        states_between_steps = []  # список состояний между этапами, это нужно для визуализации
        save_info_kratnost = 100  # кратность записи шагов в файл для построения графиков
        istep = 0
        time_curr = cur_stage_time
        while time_curr <= next_stage_time:
            pow_curr = self.pow_int_fun(time_curr)
            cb_start = model.get_cb()
            # # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # self.model.come_to_the_desired_power_by_control_grp(w=pow_curr, dw=0.1)
            # self.model.step()
            # time_curr = time_curr + self.model._delt
            #
            # # устанавливаем скорость движения группы
            # for kratnost in range( drive.nhgrp_step ):
            #     self.model.come_to_the_desired_power_by_boric_acid(w=pow_curr, dw=0.9)
            #     self.model.step()
            #     time_curr = time_curr + self.model._delt
            # cb_end = self.model.get_cb()

            # kratnost = drive.nhgrp_step
            # через сколько шагов можем двинуться группой
            # if istep % kratnost == 0:
            # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            model.come_to_the_desired_power_by_control_grp(w=pow_curr, dw=0.1, strategy_type=drive)
            model.step()
            time_curr = time_curr + model._delt

            model.come_to_the_desired_power_by_boric_acid(w=pow_curr, dw=0.9)
            model.step()
            time_curr = time_curr + model._delt
            cb_end = model.get_cb()

            # оценка расхода на микрошаге
            if self.optimize_type == 0:
                cost = get_water_discarge(cb_beg=cb_start, cb_end=cb_end)
            elif self.optimize_type == 1:
                cost = get_cost_by_power(w_nagruzka=self.pow_int_fun(time_curr),
                                         w_current=model.get_w_tot())
            # оценка расхода за этап
            track_total_cost = track_total_cost + cost

            # записываем каждый какой-то шаг в файл
            # if istep % save_info_kratnost == 0:
            states_between_steps.append(model.get_states())

            istep = istep + 1

            # проверка корректности состояния на текущий момент по ограничениям
            is_state_correct = model.is_state_correct()
            if not is_state_correct:
                print("\t\tdel by AO\n")
                return None

        begin_state = track.state
        end_state = model.get_states()
        # self.id = self.id + 1
        # for node in end_state.values():
        #     node.id = self.id

        track_new = Track(parent_state=begin_state, state=end_state, drive=drive,
                          parent_total_cost=track.total_cost, cost=track_total_cost)
        with lmdb.open('tracks_info', map_size=536870912*2) as env:
            with env.begin(write=True) as txn:
                txn.put(track_new.track_id.encode(), pickle.dumps(states_between_steps))
        # track_new._states_between_steps = states_between_steps

        dp_to_end_total_cost_min = None
        evristik_discard_level = None

        if self.optimize_type == 0:
            # оценка
            # evristic_end_states = self.evr_obj.model.get_states()

            cb_evristic_final = self.evr_states[0].cb

            to_end_cost_min = get_water_discarge(track_new.state[0].cb, cb_evristic_final)
            # сумма затрат по дин прого до текущей точки + оценка до конечной точки
            dp_to_end_total_cost_min = track.total_cost + to_end_cost_min

            evristik_discard_level = self.evr_cost * 1.10  #  # чуть-чуть увеличиваем цену на эвристику
        elif self.optimize_type == 1:
            # оценка
            to_end_cost_min = get_cost_by_power(w_nagruzka=self.last_lf_op[1], w_current=model.get_w_tot())
            # сумма затрат по динамическому программированию до текущей точки + оценка до конечной точки
            dp_to_end_total_cost_min = track.total_cost + to_end_cost_min

            # evristik_discard_level = self.evr_cost * 1.05  # + 10 # чуть-чуть увеличиваем цену на эвристику
            evristik_discard_level = self.evr_cost

        time = track_new.state[0].time
        w = model.get_w_tot()
        hgrps = []
        for i_h in range(len(track.state[0].h)):
            hgrps.append(1 - (track_new.state[0].h[i_h] + track_new.state[1].h[i_h]))
        cb = begin_state[0].cb
        cb_final = end_state[0].cb
        print(
            f"\t\tt:{time / 3600:.2f}, w:{w:.2f}, h:{hgrps}, cb:{cb:.2f}, cb_final:{cb_final:.2f}, "
            f"cost:{track_new.cost:.2f}, total_cost:{track_new.total_cost:.2f}, "
            f"dp_min:{dp_to_end_total_cost_min:.2f}\tevr:{evristik_discard_level:.2f}")

        # подумать в какой момент отключить эвристику, или как изменить
        #  критерии оценки снизу
        end_state = model.get_states()
        if dp_to_end_total_cost_min <= evristik_discard_level:
            return track_new
        else:
            self.discard_by_evristic += 1
            print('\t\tdiscard track by evristic\n')
            return None

    def run(self):
        """Запуск процесса на расчет"""
        print('start_process')
        new_track_list = []
        number_of_states = 0
        # перебираем для текущего состояния все возможные управления
        # для всех управлений - строим новые трэки
        with self.semaphore:
            # модель активируем здесь - тк задейстовать новый процесс будем для пула стратегий управлений
            model = self.models_queue.get()
            # для каждого управления строим новый трэк
            for drive in self.drive_list:

                new_track = self._get_new_track(
                    self.track,
                    drive,
                    model,
                    self.cur_stage_time,
                    self.next_stage_time
                )
                if new_track is None:
                    continue
                #id = new_track.state[0].id # сейчас подсчет id работает не корректно, тк в каждом трэке он свой
                #print(f"     {id}       Strategy - {drive}\n")
                print(f"\t\tStrategy - {drive}\n")
                number_of_states = number_of_states + 1
                new_track_list.append(new_track)
            self.models_queue.put(model)
        self.result_queue.put((new_track_list, number_of_states, self.discard_by_evristic))
        print('end_process\n')
