import kpa_ske_lr_serial
import copy
import time
import threading


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
        # ## GPIO ## #
        self.gpio_a, self.gpio_b = 0x00, 0x00
        # ## MKO ## #
        self.mko_bus = "mko_a"
        self.mko_cw = 0x0000
        self.mko_aw = 0x0000
        self.mko_data = []
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
        self.gpio_a |= 0x08
        self.serial.request(req_type="set_gpio", data=[self.gpio_a, self.gpio_b])

    def power_off(self):
        self.gpio_a &= ~0x08
        self.serial.request(req_type="set_gpio", data=[self.gpio_a, self.gpio_b])

    def dep_p24v_on(self):
        self.gpio_a &= ~0x04
        self.gpio_a |= 0x03
        self.serial.request(req_type="set_gpio", data=[self.gpio_a, self.gpio_b])

    def dep_m24v_on(self):
        self.gpio_a &= ~0x02
        self.gpio_a |= 0x05
        self.serial.request(req_type="set_gpio", data=[self.gpio_a, self.gpio_b])

    def dep_0v_on(self):
        self.gpio_a &= ~0x07
        self.serial.request(req_type="set_gpio", data=[self.gpio_a, self.gpio_b])

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
                elif var[0] == 0x07 or var[0] == 0x08:
                    self.mko_aw = int.from_bytes(var[1][0:2], signed=False, byteorder='big')
                    if var[1][2:]:
                        self.mko_data = []
                        for i in range(1, len(var[1]) // 2):
                            self.mko_data.append(int.from_bytes(var[1][2*i:2*(i + 1)], signed=False, byteorder='big'))
            if self._close_event.is_set() is True:
                self._close_event.clear()
                return
        pass

    def get_adc_data(self):
        adc_color = []
        with self.serial.ans_data_lock:
            adc_data_tmp = copy.deepcopy(self.adc_data)
        for i in range(len(adc_data_tmp)):
            self._adc_data_state[i] = bound_calc(adc_data_tmp[i], self.adc_data_top[i], self.adc_data_bot[i])
            adc_color.append(self._get_adc_data_color_scheme(i))
        return adc_data_tmp, adc_color

    def get_mko_data(self):
        with self.serial.ans_data_lock:
            mko_data = copy.deepcopy(self.mko_data)
            mko_aw = self.mko_aw
            self.mko_aw = 0x0000
        return self.mko_cw, mko_aw, mko_data

    def get_state_string(self):
        state_str = self.serial.state_string[self.serial.state]
        return state_str

    def _get_adc_data_color_scheme(self, channel_num):
        if self.serial.is_open:
            color = self.adc_color[channel_num][self._adc_data_state[channel_num]]
        else:
            color = self.adc_color[channel_num][3]
        return color


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