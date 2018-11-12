import kpa_ske_lr_serial
import copy
import time
import threading
import luna_data
import numpy as np


class Data:
    def __init__(self):
        self.serial = kpa_ske_lr_serial.MySerial(serial_numbers=["AH06VN4D", "AH06VN4E"])
        self.serial.open_id()
        self.adc_name = ["КС, Ом", "АМКО, В", "Норма ЦМ, В", "КПБЭ, В",
                         "U БЭ, В", "I БЭ, мА", "Канал 6, кв", "Канал 7, кв",
                         "Канал 8, кв", "Канал 9, кв", "Канал 10, кв", "Канал 11, кв",
                         "Канал 12, кв", "Канал 13, кв", "Канал 14, кв", "Канал 15, кв",]
        self.adc_data = [0 for i in range(len(self.adc_name))]
        self._adc_data_state = [0 for i in range(len(self.adc_name))]
        # ## АЦП ## #
        # границы для определения статуса
        self.adc_data_top = [10, 3.0, 3.0, 3.0, 32.8, 330, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0]
        self.adc_data_bot = [10, 1.0, 1.0, 1.0, 22.5, 70, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0]
        self.adc_data_nodata = [0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0]
        # калибровка ацп Val = a*x + b
        self.adc_a = [-1.295, 0.0027, 0.0027, 0.0027, 0.0438, 0.4914, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.adc_b = [1647.2, -0.26,  -0.26,  -0.26, -10.926, -128.89, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0]
        # цветовая схема:  ниже нижней границы - между нижней и верхней - выше верхней - нет данных
        self.adc_color = [["lightcoral", "palegreen", "palegreen", "ghostwhite"] for i in range(len(self.adc_name))]
        self.adc_color[0] = ["palegreen", "lightcoral", "lightcoral", "ghostwhite"]  # KC
        self.adc_color[1] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # AMKO
        self.adc_color[2] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # НЦМ
        self.adc_color[3] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # КПБЭ
        # параметры КПА
        self.ske_U = [0, "ghostwhite"]
        self.ske_I = [0, "ghostwhite"]
        self.ske_W = [0, "ghostwhite"]
        self.ske_KPBE = [0, "ghostwhite"]
        self.ske_NormCM = [0, "ghostwhite"]
        self.ske_AMKO = [0, "ghostwhite"]
        # ## GPIO ## #
        self.gpio_a, self.gpio_b = 0x00, 0x00
        # ## MKO ## #
        self.mko_addr = 22  # адрес ОУ для БЭ СКЭ-ЛР
        self.mko_comm_subaddr = 0x11  # подадрес для отправки комманд
        self.mko_bus = "mko_a"
        self.mko_cw = 0x0000
        self.mko_aw = 0x0000
        self.mko_data = []
        # ## TESTS ## #
        self.test_data_name = ["Напряжение, В", "Ток БЭ, мА", "Потребление БЭ, Вт",
                               "КПБЭ, В", "НормЦМ, В", "АМКО, В",
                               "Ток ЦМ, мА", "Ток МПП1-2, мА", "Ток МПП3-4, мА",
                               "Ток МДЭП, мА", "Ошибки ВШ, шт", "Неответы ВШ, шт",
                               "Среднее МПП1, В", "Среднее МПП2, В", "Среднее ДРП, В",
                               "Среднее ДНП, В", "Среднее РП1, В", "Среднее РП2, В",
                               "Поле ДЭП1, кВ", "Частота ДЭП1, Гц", "Температура ДЭП1, °С",
                               "Поле ДЭП2, кВ", "Частота ДЭП2, Гц", "Температура ДЭП2, °С",
                               "Наработка, ч", "Измерительный интервал, с",
                               ]
        self.test_data = [0 for i in range(len(self.test_data_name))]
        self.test_data_top = [32.8, 330, 8,
                              3.0, 3.0, 3.0,
                              75, 75, 75,
                              75, 1, 1,
                              1, 1, 1,
                              1, 1, 1,
                              10, 170, 85,
                              10, 170, 85,
                              1000, 240]
        self.test_data_bot = [23, 70, 1.5,
                              1.0, 1.0, 1.0,
                              50, 50, 50,
                              50, 0, 0,
                              -1, -1, -1,
                              -1, -1, -1,
                              -10, 120, -50,
                              -10, 120, -50,
                              0, 1]
        self.test_color_teamplate = [["lightcoral", "palegreen", "lightcoral", "ghostwhite"] for i in
                                     range(len(self.test_data_name))]
        self.test_color_teamplate[3] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # AMKO
        self.test_color_teamplate[4] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # НЦМ
        self.test_color_teamplate[5] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # КПБЭ
        self.test_color = [color[3] for color in self.test_color_teamplate]
        self.cm_test_status = 0
        self.mpp_test_status = 0
        self.dep_test_status = 0
        #
        self._close_event = threading.Event()
        self.parc_thread = threading.Thread(target=self.parc_data, args=(), daemon=True)
        self.parc_thread.start()
        self.data_lock = threading.Lock()
        pass

    def reconnect(self):
        self.serial.close_id()
        time.sleep(0.05)
        self.serial.open_id()
        pass

    def disconnect(self):
        self.serial.close_id()
        pass

    def get_adc(self):
        self.serial.request(req_type="get_adc")
        pass

    def ku_on(self, time_ms=100):
        self.serial.request(req_type="ku_on", data=[0x00, time_ms])
        pass

    def ku_off(self, time_ms=100):
        self.serial.request(req_type="ku_off", data=[0x00, time_ms])
        pass

    def power_on(self):
        self.serial.request(req_type="power", data=[0x01])

    def power_off(self):
        self.serial.request(req_type="power", data=[0x00])

    def dep_p24v_on(self):
        self.serial.request(req_type="dep_24v", data=[0x01])

    def dep_m24v_on(self):
        self.serial.request(req_type="dep_24v", data=[0x02])

    def dep_0v_on(self):
        self.serial.request(req_type="dep_24v", data=[0x00])

    def send_mko_comm_message(self, c_type="start_mem_read", data=None):  # ВАЖНО! data - list of int16
        if c_type == "init_cm":
            comm_data = [0x0002, 0x0000, 0x0000, 0x0000]
        elif c_type == "meas_interval":
            comm_data = [0x0003, data[0], 0x0000, 0x0000]
        elif c_type == "start_mem_read":
            comm_data = [0x0007, 0x0000, 0x0000, 0x0000]
        else:
            comm_data = [0x0007, 0x0000, 0x0000, 0x0000]
        self.send_to_rt(self.mko_addr, self.mko_comm_subaddr, comm_data, 4)
        pass

    def send_to_rt(self, addr, subaddr, data, leng):
        self.mko_cw = ((addr & 0x1F) << 11) + (0x00 << 10) + ((subaddr & 0x1F) << 5) + (leng & 0x1F)
        rt_data = [(self.mko_cw >> 8) & 0xFF, (self.mko_cw >> 0) & 0xFF]
        self.mko_data = data
        bytes_data = []
        for var in data:
            bytes_data.append(int((var >> 8) & 0xFF))
            bytes_data.append(int((var >> 0) & 0xFF))
        rt_data.extend(bytes_data)
        self.mko_bus = "mko_b" if self.mko_bus == "mko_a" else "mko_a"
        self.serial.request(req_type=self.mko_bus, data=rt_data)
        pass

    def read_from_rt(self, addr, subaddr, leng):
        self.mko_cw = ((addr & 0x1F) << 11) + (0x01 << 10) + ((subaddr & 0x1F) << 5) + (leng & 0x1F)
        rt_data = [(self.mko_cw >> 8) & 0xFF, (self.mko_cw >> 0) & 0xFF]
        self.mko_bus = "mko_b" if self.mko_bus == "mko_a" else "mko_a"
        self.serial.request(req_type=self.mko_bus, data=rt_data)
        pass

    def parc_data(self):
        while True:
            time.sleep(0.01)
            data = []
            with self.serial.ans_data_lock:
                if self.serial.answer_data:
                    data = copy.deepcopy(self.serial.answer_data)
                    self.serial.answer_data = []
            for var in data:
                if var[0] == 0x04:  # получение данных АЦП
                    for i in range(len(var[1]) // 2):
                        self.adc_data[i] = self.adc_a[i]*(int.from_bytes(var[1][2*i:2*i+2], signed=False, byteorder='big')
                                                          & 0x0FFF) + self.adc_b[i]
                elif var[0] == 0x07 or var[0] == 0x08:  # получение данных МКО
                    self.mko_aw = int.from_bytes(var[1][0:2], signed=False, byteorder='big')
                    # print("aw = 0x%04X" % self.mko_aw)
                    if var[1][2:]:
                        self.mko_data = []
                        for i in range(1, len(var[1]) // 2):
                            self.mko_data.append(int.from_bytes(var[1][2*i:2*(i + 1)], signed=False, byteorder='big'))
            if self._close_event.is_set() is True:
                self._close_event.clear()
                return
        pass

    def form_kpa_data(self):  # вызывать для обновление параметров класса kpa
        adc_color = []
        with self.serial.ans_data_lock:
            adc_data_tmp = copy.deepcopy(self.adc_data)
        for i in range(len(adc_data_tmp)):
            self._adc_data_state[i] = bound_calc(adc_data_tmp[i], self.adc_data_top[i], self.adc_data_bot[i])
            adc_color.append(self._get_adc_data_color_scheme(i))
        self.ske_U = [adc_data_tmp[4], adc_color[4]]
        self.ske_I = [adc_data_tmp[5], adc_color[5]]
        power = adc_data_tmp[4] * adc_data_tmp[5] / 1000
        power_color = "palegreen" if 1.8 < power < 8 else "lightcoral"
        self.ske_W = [power, power_color]
        self.ske_KPBE = [adc_data_tmp[3], adc_color[3]]
        self.ske_NormCM = [adc_data_tmp[2], adc_color[2]]
        self.ske_AMKO = [adc_data_tmp[1], adc_color[1]]
        return adc_data_tmp, adc_color

    def reset_mko_data(self):
        with self.serial.ans_data_lock:
            self.mko_aw = 0x0000
        pass

    def get_mko_data(self):
        with self.serial.ans_data_lock:
            mko_data = copy.deepcopy(self.mko_data)
            mko_aw = self.mko_aw
            self.mko_aw = 0x0000
        return self.mko_cw, mko_aw, mko_data

    def get_state_string(self):
        state_str = self.serial.state_string[self.serial.state]
        return state_str

    def mpp_read_algorithm(self):
        # # задаем воздействие с КПА todo: необходимо доделать КПА
        # # читаем 6 кадров с помехами
        # МПП 1-2 - ДРП, ДНП
        for i in range(6):
            subaddr = i + 1
            self.read_from_rt(self.mko_addr, 0x0001 + i, 32)
            time.sleep(0.5)
            table_data = luna_data.frame_parcer(self.get_mko_data()[2])
            for var in table_data:
                if "Среднее" in var[0]:
                    if subaddr == 1: self._set_test_data("Среднее МПП1", var[1])
                    elif subaddr == 2: self._set_test_data("Среднее МПП2", var[1])
                    elif subaddr == 3: self._set_test_data("Среднее ДРП", var[1])
                    elif subaddr == 4: self._set_test_data("Среднее ДНП", var[1])
                    elif subaddr == 5: self._set_test_data("Среднее РП1", var[1])
                    elif subaddr == 6: self._set_test_data("Среднее РП2", var[1])
                    break

    def dep_read_algorithm(self):
        # # задаем воздействие с КПА
        self.dep_0v_on()
        # # читаем показания dep
        time.sleep(10)
        self.read_from_rt(self.mko_addr, 0x0009, 32)
        time.sleep(0.5)
        table_data = luna_data.frame_parcer(self.get_mko_data()[2])
        for var in table_data:
            if "Поле ДЭП1" in var[0]: self._set_test_data("Поле ДЭП1", var[1])
            elif "Частота ДЭП1" in var[0]: self._set_test_data("Частота ДЭП1", var[1])
            elif "Температура ДЭП1" in var[0]: self._set_test_data("Температура ДЭП1", var[1])
            elif "Поле ДЭП2" in var[0]: self._set_test_data("Поле ДЭП2", var[1])
            elif "Частота ДЭП2" in var[0]: self._set_test_data("Частота ДЭП2, Гц", var[1])
            elif "Температура ДЭП2" in var[0]: self._set_test_data("Температура ДЭП2", var[1])

    def sys_cm_read_algorithm(self):
        # # читаем системный кадр
        self.read_from_rt(self.mko_addr, 0x000F, 32)
        time.sleep(0.5)
        try:
            table_data = luna_data.frame_parcer(self.get_mko_data()[2])
        except Exception as error:
            print(error)
        for var in table_data:
            if "Ток ЦМ" in var[0]: self._set_test_data("Ток ЦМ", var[1])
            elif "Ток МПП1-2" in var[0]: self._set_test_data("Ток МПП1-2", var[1])
            elif "Ток ДРП, ДНП" in var[0]: self._set_test_data("Ток МПП3-4", var[1])
            elif "Ток МДЭП" in var[0]: self._set_test_data("Ток МДЭП", var[1])
            elif "Ошибки ВШ" in var[0]: self._set_test_data("Ошибки", var[1])
            elif "Неответы ВШ" in var[0]: self._set_test_data("Неответы", var[1])
            elif "Время наработки" in var[0]: self._set_test_data("Наработка", var[1])
            elif "Интервал измерения" in var[0]: self._set_test_data("Измерительный интервал", var[1])

    def cm_test_algorithm(self):
        # инициализируем ЦМ
        self.send_mko_comm_message(c_type="init_cm")
        time.sleep(20)
        # устанавливаем интервал измерения на 1 сек
        self.send_mko_comm_message(c_type="meas_interval", data=[1])
        time.sleep(0.3)
        # подаем водздействия и читаем данные МПП и ДЭП
        self.mpp_read_algorithm()
        self.dep_read_algorithm()
        # читаем системный кадр ЦМ
        self.sys_cm_read_algorithm()
        # чтение данных АЦП КПА
        self.get_adc()
        time.sleep(0.3)
        self.form_kpa_data()
        try:
            self._set_test_data("Потребление", "%.2f" % self.ske_W[0])
            self._set_test_data("Напряжение", "%.2f" % self.ske_U[0])
            self._set_test_data("Ток БЭ", "%.2f" % self.ske_I[0])
            self._set_test_data("КПБЭ", "%.1f" % self.ske_KPBE[0])
            self._set_test_data("НормЦМ", "%.1f" % self.ske_NormCM[0])
            self._set_test_data("АМКО", "%.1f" % self.ske_AMKO[0])
        except Exception as error:
            print(error)
        # устанавливаем интервал измерения на 10 сек
        self.send_mko_comm_message(c_type="meas_interval", data=[10])
        time.sleep(0.3)

    def _get_adc_data_color_scheme(self, channel_num):
        if self.serial.is_open:
            color = self.adc_color[channel_num][self._adc_data_state[channel_num]]
        else:
            color = self.adc_color[channel_num][3]
        return color

    def _set_test_data(self, name, data):
        for i in range(len(self.test_data_name)):
            if name in self.test_data_name[i]:
                self.test_data[i] = data
                self.test_color[i] = self.test_color_teamplate[i][
                    bound_calc(float(data), self.test_data_top[i], self.test_data_bot[i])]
                pass
        pass


def bound_calc(val, top, bot):
    result = 2 if val > top else 1
    result = 0 if val < bot else result
    return result


def get_time():
    return time.strftime("%H-%M-%S", time.localtime()) + "." + ("%.3f: " % time.clock()).split(".")[1]


def str_to_list(send_str):  # функция, которая из последовательности шестнадцетиричных слов в строке без
    send_list = []  # идентификатора 0x делает лист шестнадцетиричных чисел
    send_str = send_str.split(' ')
    for i, ch in enumerate(send_str):
        send_str[i] = ch
        send_list.append(int(send_str[i], 16))
    return send_list


def bytes_array_to_str(bytes_array):
    bytes_string = ""
    for i, ch in enumerate(bytes_array):
        byte_str = (" %02X" % bytes_array[i])
        bytes_string += byte_str
    return bytes_string