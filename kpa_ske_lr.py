import kpa_ske_lr_serial


class Data:
    def __init__(self):
        self.serial = kpa_ske_lr_serial.MySerial(serial_numbers=["AH06VN4D"])
        self.serial.open_id()
        self.adc_name = ["КС", "АМКО", "Норма ЦМ", "КПБЭ",
                         "U БЭ, В", "I БЭ, мА", "Канал 6, кв", "Канал 7, кв",
                         "Канал 8, кв", "Канал 9, кв", "Канал 10, кв", "Канал 11, кв",
                         "Канал 12, кв", "Канал 13, кв", "Канал 14, кв", "Канал 15, кв",]
        self.adc_data = [0 for i in range(len(self.adc_name))]
        self.adc_data_state = [0 for i in range(len(self.adc_name))]
        # ## АЦП ## #
        # границы для определения статуса
        self.adc_data_top = [1700, 2063, 2056, 2064, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0]
        self.adc_data_bot = [1700, 1908, 1901, 1910, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0]
        # калибровка ацп
        self.adc_a = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.adc_b = [0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0]
        # цветовая схема
        self.adc_color = [["lightcoral", "lightcoral", "lightcoral"] for i in range(len(self.adc_name))]
        self.adc_color[0] = ["lightcoral", "lightcoral", "palegreen"]  # KC
        self.adc_color[1] = ["mediumturquoise", "lightcoral", "palegreen"]  # AMKO
        self.adc_color[2] = ["mediumturquoise", "lightcoral", "palegreen"]  # НЦМ
        self.adc_color[3] = ["mediumturquoise", "lightcoral", "palegreen"]  # КПБЭ
        # ## GPIO ## #
        self.gpio_a, self.gpio_b = 0x00, 0x00
        #
        pass

    def get_adc(self):
        self.serial.request(req_type="get_adc")
        pass

    def ku_on(self):
        self.serial.request(req_type="ku_on", data=[0xFF, 0xFF])
        pass

    def ku_off(self):
        self.serial.request(req_type="ku_off", data=[0xFF, 0xFF])
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

    def parc_data(self):
        data = []
        with self.serial.ans_data_lock:
            if self.serial.answer_data:
                data = self.serial.answer_data.pop(0)
        if data:
            if data[0] == 0x04:  # получение данных АЦП
                for i in range(len(data[1])):
                    self.adc_data[i] = self.adc_a[i]*(int.from_bytes(data[1][2*i:2*i+2], signed=False, byteorder='big')
                                                      & 0x0FFF) + self.adc_b[i]
                    self.adc_data_state[i] = bound_calc(self.adc_data[i], self.adc_data_top[i], self.adc_data_bot[i])
        pass

    def get_adc_data_color_scheme(self, channel_num):
        color = self.adc_color[channel_num][self.adc_data_state[channel_num]]
        return color


def bound_calc(val, top, bot):
    result = 2 if val > top else 1
    result = 0 if val < bot else result
    return result
