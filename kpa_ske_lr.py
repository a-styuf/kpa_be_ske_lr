import kpa_ske_lr_serial
import copy
import time
import threading
import luna_data
import crc16
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
        self.adc_log_buffer = []
        self.graph_data = [[], [], []]
        self.max_point = 10000
        # ## GPIO ## #
        self.gpio_a, self.gpio_b = 0x00, 0x00
        # ## MKO ## #
        self.mko_addr = 13  # адрес ОУ для БЭ СКЭ-ЛР
        self.mko_comm_subaddr = 0x11  # подадрес для отправки комманд
        self.mko_bus = "mko_a"
        self.mko_cw = 0x0000
        self.mko_aw = 0x0000
        self.mko_data = []
        self.mko_log_buffer = []
        # ## TESTS ## #
        self.test_data_name = ["Напряжение, В", "Ток БЭ, мА", "Потребление БЭ, Вт",
                               "КПБЭ, В", "НормЦМ, В", "АМКО, В",
                               "Ток ЦМ, мА", "Ток МПП1-2, мА", "Ток МПП3-4, мА",
                               "Ток МДЭП, мА", "Ошибки ВШ, шт", "Неответы ВШ, шт",
                               "Максимум Uизм2, В", "Максимум Uизм3, В", "Максимум ДРП, В",
                               "Максимум ДНП, В", "Максимум РП1, В", "Максимум РП2, В",
                               "U ДЭП1@+24V, кВ", "F ДЭП1@+24V, Гц", "T ДЭП1@+24V, °С",
                               "U ДЭП2@+24V, кВ", "F ДЭП2@+24V, Гц", "T ДЭП2@+24V, °С",
                               "U ДЭП1@0V, кВ", "F ДЭП1@0V, Гц", "T ДЭП1@0V, °С",
                               "U ДЭП2@0V, кВ", "F ДЭП2@0V, Гц", "T ДЭП2@0V, °С",
                               "U ДЭП1@-24V, кВ", "F ДЭП1@-24V, Гц", "T ДЭП1@-24V, °С",
                               "U ДЭП2@-24V, кВ", "F ДЭП2@-24V, Гц", "T ДЭП2@-24V, °С",
                               "Наработка, ч", "Измерительный интервал, с",
                               ]
        self.test_data = ["0" for i in range(len(self.test_data_name))]
        self.test_data_top = [32.8, 330, 8,
                              3.0, 3.0, 3.0,
                              75, 75, 75,
                              75, 1, 1,
                              13, 13, 1,
                              13, 13, 13,
                              10, 170, 85,
                              10, 170, 85,
                              10, 170, 85,
                              10, 170, 85,
                              10, 170, 85,
                              10, 170, 85,
                              1000, 240]
        self.test_data_bot = [23, 70, 1.5,
                              1.0, 1.0, 1.0,
                              40, 40, 40,
                              40, 0, 0,
                              7, 7, -1,
                              7, 7, 7,
                              -10, 120, -50,
                              -10, 120, -50,
                              -10, 120, -50,
                              -10, 120, -50,
                              -10, 120, -50,
                              -10, 120, -50,
                              0, 9]
        self.test_color_teamplate = [["lightcoral", "palegreen", "lightcoral", "ghostwhite"] for i in
                                     range(len(self.test_data_name))]
        self.test_color_teamplate[3] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # AMKO
        self.test_color_teamplate[4] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # НЦМ
        self.test_color_teamplate[5] = ["palegreen", "lightcoral", "mediumturquoise", "ghostwhite"]  # КПБЭ
        self.test_color = [color[3] for color in self.test_color_teamplate]
        self.ske_test_status = 0
        #
        self.test_stop_event = threading.Event()
        self.test_thread = threading.Thread(target=self.cm_test_algorithm)
        self.test_lock = threading.Lock()
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

    def mpp_test_sign(self, dev="all", u_max=0, u_min=0, T=0, t=0, N=0, M=0):
        # T-период повторения пачки (ms), t-период миандра (200 us), N-кол-во периодов миандра, М-кол-во пачек
        if dev in "mpp":
            dev_type = 0x01 << 0
        elif dev in "rp":
            dev_type = 0x01 << 1
        elif dev in "dnp":
            dev_type = 0x01 << 2
        elif dev in "all":
            dev_type = 0x07
        else:
            dev_type = 0x07
        data = [dev_type, t & 0xFF,
                ((int(u_max * 256)) >> 8) & 0xFF, ((int(u_max * 256)) >> 0) & 0xFF,
                ((int(u_min * 256)) >> 8) & 0xFF, ((int(u_min * 256)) >> 0) & 0xFF,
                ((int(N)) >> 8) & 0xFF, ((int(N)) >> 0) & 0xFF,
                ((int(T)) >> 8) & 0xFF, ((int(T)) >> 0) & 0xFF,
                M & 0xFF]
        self.serial.request(req_type="gener_sign", data=data)

    def send_mko_comm_message(self, c_type="start_mem_read", data=None):  # ВАЖНО! data - list of int16
        self.mko_addr, self.mko_comm_subaddr = 13, 17
        if c_type == "init_cm":
            comm_data = [0x0002, 0x0000, 0x0000, 0x0000]
        elif c_type == "meas_interval":
            comm_data = [0x0003, data[0], 0x0000, 0x0000]
        elif c_type == "speedy_mode":
            comm_data = [0x000B, data[0], data[1], 0x0000]
        elif c_type == "start_mem_read":
            comm_data = [0x0007, 0x0000, 0x0000, 0x0000]
        else:
            comm_data = [0x0007, 0x0000, 0x0000, 0x0000]
        self.send_to_rt(self.mko_addr, self.mko_comm_subaddr, comm_data, 4)
        pass

    def send_mko_tech_comm_message(self, c_type="cm_param", data=None):  # ВАЖНО! data - list of int16
        self.mko_addr, self.mko_comm_subaddr = 13, 30
        if c_type == "cm_param":
            comm_data = [0x0001, 0x0000, 0x0000, 0x0000]
        elif c_type == "mirror":
            comm_data = [0x0002, data[0], data[1], data[2]]
        elif c_type == "dbg_int":
            comm_data = [0x0003, data[0], data[1], 0x0000]
        else:
            comm_data = [0x0001, 0x0000, 0x0000, 0x0000]
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
                    with self.serial.ans_data_lock:
                        self.adc_log_buffer.append(self.get_adc_data_str())
                elif var[0] == 0x07 or var[0] == 0x08:  # получение данных МКО
                    self.mko_aw = int.from_bytes(var[1][0:2], signed=False, byteorder='big')
                    # print("aw = 0x%04X" % self.mko_aw)
                    if var[1][2:]:
                        self.mko_data = []
                        for i in range(1, len(var[1]) // 2):
                            self.mko_data.append(int.from_bytes(var[1][2*i:2*(i + 1)], signed=False, byteorder='big'))
                    with self.serial.ans_data_lock:
                        self.mko_log_buffer.append(self.get_mko_data_title())
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
        self.form_graph_data()
        return adc_data_tmp, adc_color

    def get_adc_data_str(self):
        adc_data_str = get_date_time() + ";"
        for i in range(len(self.adc_data)):
            adc_data_str += ("%.3f" % self.adc_data[i]).replace(".", ",") + ";"
        return adc_data_str

    def get_adc_data_title(self):
        adc_data_str = "Время;"
        for i in range(len(self.adc_name)):
            adc_data_str += ("%s" % self.adc_name[i]).replace(".", ",") + ";"
        return adc_data_str

    def get_mko_data_title(self):
        mko_data_str = ""
        mko_str = ""
        for var in self.mko_data:
            mko_data_str += "%04X " % var
        crc16_result = crc16.calc_str(mko_data_str[:-5], endian="big")
        crc16_state = crc16.calc_str(mko_data_str[:], endian="big")
        crc16_result_str = "OK" if crc16_state == 0 else "BAD - 0x%04X" % crc16_result
        mko_str += get_date_time() + ";" + \
                   " CW:%04X" % self.mko_cw + "; " + \
                   " AW:%04X" % self.mko_aw + "; " + \
                   " D:" + mko_data_str + ";" + \
                   " CRC16:" + crc16_result_str + ";"
        return mko_str

    def get_mko_log(self):
        with self.serial.ans_data_lock:
            buffer = self.mko_log_buffer
            self.mko_log_buffer = []
        return buffer

    def get_adc_log(self):
        with self.serial.ans_data_lock:
            buffer = self.adc_log_buffer
            self.adc_log_buffer = []
        return buffer

    def form_graph_data(self):
        try:
            self.graph_data[0].append(time.clock())
            self.graph_data[1].append(self.ske_U[0])
            self.graph_data[2].append(self.ske_W[0])
            while len(self.graph_data[0]) > 10000:
                self.graph_data[0].pop(0)
                self.graph_data[1].pop(0)
                self.graph_data[2].pop(0)
        except Exception as error:
            print(error)

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

    def mpp_read_algorithm(self, meas_interval=1):
        try:
            # # задаем воздействие с КПА
            self.mpp_test_sign(dev="all", u_max=10, u_min=0, T=5000, t=1, N=20, M=meas_interval)
            # # читаем кадры с матрицей
            self.test_stop_event.wait(meas_interval*2)
            if self.test_stop_event.isSet():
                raise Exception('Принудительное завершение работы')
            self.read_from_rt(self.mko_addr, 7, 32)
            time.sleep(0.5)
            cw, aw, data = self.get_mko_data()
            table_data = luna_data.frame_parcer(data)
            if aw == cw & 0xF800:
                for report in table_data:
                    if "МПП3@МПП3" in report[0]: self._set_test_data("Максимум Uизм2, В", report[1])
                    elif "МПП4@МПП4" in report[0]: self._set_test_data("Максимум Uизм3, В", report[1])
                    elif "МПП1@МПП1" in report[0]: self._set_test_data("Максимум ДРП, В", report[1])
                    elif "МПП2@МПП2" in report[0]: self._set_test_data("Максимум ДНП, В", report[1])
                    elif "МПП5@МПП5" in report[0]: self._set_test_data("Максимум РП1, В", report[1])
                    elif "МПП6@МПП6" in report[0]: self._set_test_data("Максимум РП2, В", report[1])
            else:
                return -1
            return 1
        except Exception as error:
            print(error)

    def dep_read_algorithm(self, test_voltage=0, meas_interval=1):
        # # задаем воздействие с КПА
        if test_voltage == 24:
            self.dep_p24v_on()
            t_v_str = "@+24"
        elif test_voltage == 0:
            self.dep_0v_on()
            t_v_str = "@0"
        elif test_voltage == -24:
            self.dep_m24v_on()
            t_v_str = "@-24"
        else:
            self.dep_0v_on()
            t_v_str = "@0"
        # читаем показания dep
        self.test_stop_event.wait(meas_interval*7)
        if self.test_stop_event.isSet():
            raise Exception('Принудительное завершение работы')
        self.read_from_rt(self.mko_addr, 0x0009, 32)
        time.sleep(0.5)
        cw, aw, data = self.get_mko_data()
        table_data = luna_data.frame_parcer(data)
        self.dep_0v_on()  # отключаем тестовые воздействия на ДЭП
        if aw == cw & 0xF800:
            for var in table_data:
                if "U6 ДЭП1" in var[0]: self._set_test_data("U ДЭП1" + t_v_str, var[1])
                elif "F6 ДЭП1" in var[0]: self._set_test_data("F ДЭП1" + t_v_str, var[1])
                elif "T6 ДЭП1" in var[0]: self._set_test_data("T ДЭП1" + t_v_str, var[1])
                elif "U6 ДЭП2" in var[0]: self._set_test_data("U ДЭП2" + t_v_str, var[1])
                elif "F6 ДЭП2" in var[0]: self._set_test_data("F ДЭП2" + t_v_str, var[1])
                elif "T6 ДЭП2" in var[0]: self._set_test_data("T ДЭП2" + t_v_str, var[1])
            return 1
        else:
            return -1

    def sys_cm_read_algorithm(self, meas_interval=1):
        # # читаем системный кадр
        self.read_from_rt(self.mko_addr, 0x000F, 32)
        time.sleep(0.5)
        cw, aw, data = self.get_mko_data()
        table_data = luna_data.frame_parcer(data)
        if aw == cw & 0xF800:
            for var in table_data:
                if "Ток ЦМ" in var[0]: self._set_test_data("Ток ЦМ", var[1])
                elif "Ток МПП1-2" in var[0]: self._set_test_data("Ток МПП1-2", var[1])
                elif "Ток ДРП, ДНП" in var[0]: self._set_test_data("Ток МПП3-4", var[1])
                elif "Ток МДЭП" in var[0]: self._set_test_data("Ток МДЭП", var[1])
                elif "Ошибки ВШ" in var[0]: self._set_test_data("Ошибки", var[1])
                elif "Неответы ВШ" in var[0]: self._set_test_data("Неответы", var[1])
                elif "Время наработки" in var[0]: self._set_test_data("Наработка", var[1])
                elif "Интервал измерения" in var[0]: self._set_test_data("Измерительный интервал", var[1])
            return 1
        else:
            return -1

    def cm_test_algorithm(self, meas_interval=1):
        try:
            if self.serial.state != 1:
                self.ske_test_status = -1
                raise Exception('Тест не закончен')
            # инициализируем ЦМ
            self.send_mko_comm_message(c_type="init_cm")
            self.test_stop_event.wait(15)
            if self.test_stop_event.isSet():
                raise Exception('Принудительная остановка')
            # устанавливаем интервал измерения на meas_interval сек
            if meas_interval >= 60:
                self.send_mko_comm_message(c_type="meas_interval", data=[meas_interval//60])
            else:
                self.send_mko_tech_comm_message(c_type="dbg_int", data=[meas_interval, 10])
            self.test_stop_event.wait(meas_interval + 5)
            if self.test_stop_event.isSet():
                raise Exception('Принудительная остановка')
            # подаем водздействия и читаем данные МПП и ДЭП
            if self.mpp_read_algorithm(meas_interval=meas_interval) < 0:
                self.ske_test_status = -1
                raise Exception('Тест МПП не пройден')
            if self.dep_read_algorithm(test_voltage=24, meas_interval=meas_interval) < 0:
                self.ske_test_status = -1
                raise Exception('Тест ДЭП не пройден')
            if self.dep_read_algorithm(test_voltage=0, meas_interval=meas_interval) < 0:
                self.ske_test_status = -1
                raise Exception('Тест ДЭП не пройден')
            if self.dep_read_algorithm(test_voltage=-24, meas_interval=meas_interval) < 0:
                self.ske_test_status = -1
                raise Exception('Тест ДЭП не пройден')
            # читаем системный кадр ЦМ
            if self.sys_cm_read_algorithm() < 0:
                self.ske_test_status = -1
                raise Exception('Системный кадр не прочитан')
            # чтение данных АЦП КПА
            if self.serial.state != 1:
                self.ske_test_status = -1
                raise Exception('COM-порт не подключен')
            self.get_adc()
            time.sleep(0.3)
            self.form_kpa_data()
            self._set_test_data("Потребление", "%.2f" % self.ske_W[0])
            self._set_test_data("Напряжение", "%.2f" % self.ske_U[0])
            self._set_test_data("Ток БЭ", "%.2f" % self.ske_I[0])
            self._set_test_data("КПБЭ", "%.1f" % self.ske_KPBE[0])
            self._set_test_data("НормЦМ", "%.1f" % self.ske_NormCM[0])
            self._set_test_data("АМКО", "%.1f" % self.ske_AMKO[0])
            # проверяем на принудительность остановки
            if self.test_stop_event.isSet():
                raise Exception('Принудительная остановка')
            # устанавливаем интервал измерения на meas_interval сек
            if meas_interval >= 60:
                self.send_mko_comm_message(c_type="meas_interval", data=[meas_interval//60])
            else:
                self.send_mko_tech_comm_message(c_type="dbg_int", data=[10, 10])
            time.sleep(0.3)
            self.ske_test_status = 1
        except Exception as error:
            print(error)
            self.ske_test_status = -1
        finally:
            # устанавливаем интервал измерения на 10 сек
            self.test_stop_event.clear()
            self.send_mko_comm_message(c_type="meas_interval", data=[10])
            time.sleep(0.3)

    def ske_test_start(self, meas_interval=1):
        if self.test_thread.is_alive():
            self.ske_test_status = -1
            return
        else:
            self.test_thread = threading.Thread(target=self.cm_test_algorithm, kwargs={"meas_interval": meas_interval})
            self.test_thread.start()
            self.test_stop_event.clear()
            self.ske_test_status = 0
            return
        pass

    def _get_adc_data_color_scheme(self, channel_num):
        if self.serial.is_open:
            color = self.adc_color[channel_num][self._adc_data_state[channel_num]]
        else:
            color = self.adc_color[channel_num][3]
        return color

    def _set_test_data(self, name, data):
        # print(len(self.test_data_name), len(self.test_data_bot), len(self.test_data_top))
        for i in range(len(self.test_data_name)):
            if name in self.test_data_name[i]:
                self.test_data[i] = data
                self.test_color[i] = self.test_color_teamplate[i][
                    bound_calc(float(data), self.test_data_top[i], self.test_data_bot[i])]
                # print(name, data, self.test_color[i], self.test_data_top[i], self.test_data_bot[i])
                pass
        pass


def bound_calc(val, top, bot):
    result = 2 if val > top else 1
    result = 0 if val < bot else result
    return result


def get_time():
    return time.strftime("%H-%M-%S", time.localtime()) + "." + ("%.3f: " % time.clock()).split(".")[1]

def get_date_time():
    return time.strftime("%Y.%M.%d %H:%M:%S", time.localtime())

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

