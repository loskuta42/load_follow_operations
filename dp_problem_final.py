"""Класс для решения задачи динамического программирования."""
from multiprocessing import Pool, Queue, cpu_count, Semaphore

from base_classes import Track
from scipy import interpolate
from functools import reduce
from copy import deepcopy
from evristik import Evristic
from get_to_next_stage_process import GetNewTracksProcess


class DynamicProgrammingProblem:
    """Решение задачи динамического программирования"""

    def __init__(self, models: Queue, begin_st, load_follow_operations, optimization_type=0, evristic_strategy_type=2, semaphore_size=(cpu_count()-1)):
        """
        :param models: модель, с которой работаем
        :param begin_st: начальная точка
        :param load_follow_operations: график несения нагрузки
        :param optimization_type: тип опитимизируемого функционала:  0- водообмен, 1 -потеря энергвоыработки
        :param evristic_strategy_type:
                    0:  # индивидуальное управление рабочей группой
                    1:  # индивидуальное управление рабочей группой -1
                    2:  # перехват на 50% и остановка движения группы на 50%  от высоты зоны
                    3:  # стандартное движение на 50% и остановка движения группы внизу зоны
        :param semaphore_size: по факту количество ядер процессора, которые мы хотим использовать
        """


        self.models = models
        self.semaphore_size = semaphore_size
        # подключение к полной модели
        # self.soc = soc
        # начальная точка задачи
        self.begin_st = begin_st  # определяется мощностью, выгоранием, концентрацией борной кислоты, положением СУЗ,
        # температура на входе, концентрациями йода и ксенона

        self.load_follow_time = load_follow_operations.transpose()[0]
        self.time_beg = self.load_follow_time[0]
        # делаем, чтобы время у нас начиналось с нуля
        self.load_follow_time = self.load_follow_time - self.time_beg
        self.time_beg = self.load_follow_time[0]

        self.load_follow_power = load_follow_operations.transpose()[1]
        # создание интерполяционной функции для получения значений графика нагрузки в любой момент времени
        self.pow_int_fun = interpolate.interp1d(
            self.load_follow_time,
            self.load_follow_power,
            fill_value="extrapolate"
        )

        # начальное значение мощности
        self.pow_beg = self.load_follow_power[0]

        self.curr_stage_time = self.time_beg
        self.id = 0  # номер текущего состояния
        self.l_f_opr = load_follow_operations
        self.number_of_states_per_stage = []  # количество состояний по этапам

        evr_model = models.get()  # deepcopy(self.models)
        load_follow_operations_evr = load_follow_operations

        print(load_follow_operations_evr)
        self.evristic_strategy_type = evristic_strategy_type
        self.evr_obj = Evristic(evr_model, load_follow_operations_evr, dt=3600, dw_cbor=0.9, dw_hgrp=0.1,
                                strategy_type=evristic_strategy_type, optimization_type=optimization_type)
        self.evr_obj.calc_evristic_with_little_step()
        self.evr_cost = self.evr_obj.results[-1][-1]
        self.last_lf_op = load_follow_operations[-1]
        self.discard_by_evrestick = 0
        self.optimize_type = optimization_type
        self.optimal_path = []
        self.end_minimal_cost_track = None
        self.next_stage_time = None
        self._states_between_steps = []
        self.tracks = None

    def new_process(self, track: Track, queue: Queue, semaphore: Semaphore, cur_stage_time, next_stage_time) -> tuple[list, int]:
        new_track_list = []
        number_of_states = 0
        # перебираем для текущего состояния все возможные управления
        drive_list = self.get_all_drive_for_this_state()
        # для всех управлений - строим новые трэки
        for drive in drive_list:
            with semaphore:
                model = queue.get()
                new_track = self.get_new_track(track, drive, model, cur_stage_time, next_stage_time)
                queue.put(model)
                if new_track is None:
                    continue
            id = new_track.state[0].id
            print(f"     {id}       Strategy - {drive}")
            number_of_states = number_of_states + 1
            new_track_list.append(new_track)
        return new_track_list, number_of_states

    def go_to_next_stage(self, track_list, cur_stage_time, next_stage_time):
        """Переход между этапами"""
        new_track_list = []
        number_of_states = 0
        semaphore = Semaphore(self.semaphore_size)
        # создаем список реальных треков без НАН
        tracks = [track for track in track_list if track]
        # очереди, куда будут пихаться результаты - пол количеству трэков
        result_queues = [Queue() for _ in range(len(tracks))]
        # список объектов процессов
        processes = [
            GetNewTracksProcess(
                models_queue=self.models,
                semaphore=semaphore,
                track=track,
                cur_stage_time=cur_stage_time,
                next_stage_time=next_stage_time,
                result_queue=result_queue,
                drive_list=deepcopy(self.get_all_drive_for_this_state()),
                pow_int_fun=deepcopy(self.pow_int_fun),
                optimize_type=self.optimize_type,
                evr_cost=self.evr_cost,
                evr_states=deepcopy(self.evr_obj.model.get_states()),
                last_lf_op=deepcopy(self.last_lf_op)
            )
            for track, result_queue in zip(tracks, result_queues)
        ]

        # запуск процессов на расчет
        for process in processes:
            process.start()

        # получение результатов работы процессов
        for result_queue in result_queues:
            new_tracks, num_of_states, num_discard_tracks = result_queue.get()
            new_track_list.extend(new_tracks)
            number_of_states += num_of_states
            self.discard_by_evrestick += num_discard_tracks

        self.number_of_states_per_stage.append(number_of_states)
        self.tracks[self.next_stage_time] = new_track_list


    def go_from_start_to_final(self, times_lst):
        """Перебор всех состояний.
        :param times_lst: список времен для состояний
        """
        self.curr_stage_time = times_lst[0]

        self.tracks = {}  # треки, записываем сюда ключ: этап по времени, значение: [треки]
        # zero_track = Track(parent_state=self.begin_st, state=self.begin_st, drive=None)
        zero_track = Track(parent_state=None, state=self.begin_st, drive=None, parent_total_cost=0, cost=0)

        self.tracks[self.curr_stage_time] = [zero_track]
        # Вычитаем минус один, тк не смотрим последние треки ... подумать
        for ind in range(len(times_lst) - 1):
            print(f"{self.curr_stage_time}   ---------------------------------------------------------------")
            self.curr_stage_time = times_lst[ind]
            self.next_stage_time = times_lst[ind + 1]

            track_list = self.tracks[self.curr_stage_time]

            # переход на новый этап
            self.go_to_next_stage(track_list, self.curr_stage_time, self.next_stage_time)

            self.curr_stage_time = self.next_stage_time

        last_tracks = self.tracks[self.curr_stage_time]

        # удаляем состояния, которые не соответствуют конечной точке

        i = 0
        # удаляем из последних треков - пустые ветки
        while i < len(last_tracks):
            track = last_tracks[i]
            if not track:
                del last_tracks[i]
            i += 1

        # Найти состояние с минимальной стоимостью
        self.end_minimal_cost_track = self.find_minimal_cost(last_tracks)

        optimal = self.find_optimal_track(self.end_minimal_cost_track)

        return optimal


    @staticmethod
    def cost_comparison(cur_el, next_el):

        if cur_el.total_cost < next_el.total_cost:
            return cur_el
        else:
            return next_el

    def find_minimal_cost(self, last_tracks):
        """Найти состояние с минимальной стоимостью"""
        return reduce(self.cost_comparison, last_tracks)

    def find_optimal_track(self, final_track_with_minimal_cost):
        """Строим оптимальную траекторию"""
        times = sorted(self.tracks.keys(), reverse=True)
        self.optimal_path = []
        track_on_optimal_path = final_track_with_minimal_cost
        prev_state_id = track_on_optimal_path.parent_state[0].get_id()
        self.optimal_path.append(track_on_optimal_path)
        times.pop(0)
        for time in times:
            track_lst = self.tracks[time]

            for track in track_lst:
                if not track:
                    continue
                if prev_state_id == track.state[0].get_id():
                    track_on_optimal_path = track
                    self.optimal_path.append(track_on_optimal_path)
                    break

            if track_on_optimal_path.parent_state is not None:
                prev_state_id = track_on_optimal_path.parent_state[0].get_id()
            else:
                break

        # выкинем последний трек, поскольку он из первого состояния в первое - лишняя информация
        self.optimal_path.pop()
        # перевернем, чтобы треки были расположены по нормальному течению времени
        self.optimal_path.reverse()
        return self.optimal_path

    @staticmethod
    def get_all_drive_for_this_state():
        """Получение всех возможных управлений для данного состояния"""
        drive_list = []

        for strategy in range(4):
            drive_list.append(strategy)
        return drive_list




