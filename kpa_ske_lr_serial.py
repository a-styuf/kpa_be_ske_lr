import serial
import serial.tools.list_ports
import threading
import time
import crc16
import copy


class MySerial(serial.Serial):
    def __init__(self, **kw):
        serial.Serial.__init__(self)
        self.serial_numbers = []  # это лист возможных серийников!!! (не строка)
        self.baudrate = 115200
        self.timeout = 0.03
        self.port = "COM0"
        self.row_data = b""
        self.read_timeout = 0.3
        for key in sorted(kw):
            if key == "serial_numbers":
                self.serial_numbers = kw.pop(key)
            elif key == "baudrate":
                self.baudrate = kw.pop(key)
            elif key == "timeout":
                self.baudrate = kw.pop(key)
            elif key == "port":
                self.baudrate = kw.pop(key)
            else:
                pass
        # общие переменные
        self.s_addr = 0x00  # self address
        self.d_addr = 0x01  # device address
        self.seq_num = 0
        self.com_queue = []  # очередь отправки
        self.nansw = 0
        self.answer_data = []
        self.com_rec_flag = 0
        self.read_data = b""
        self.read_flag = 0
        self.state_string = {
            -3: "Связь с КПА потеряна",
            -2: "КПА не отвечает",
            -1: "Не удалось установить связь с КПА",
            +0: "Подключите КПА",
            +1: "Связь с КПА в норме",
        }
        self.state = 0
        self.log_buffer = []
        # для работы с потоками
        self.read_write_thread = None
        self._close_event = threading.Event()
        self.read_write_thread = threading.Thread(target=self.thread_function, args=(), daemon=True)
        self.read_write_thread.start()
        self.log_lock = threading.Lock()
        self.com_send_lock = threading.Lock()
        self.ans_data_lock = threading.Lock()

    def open_id(self):  # функция для установки связи с КПА
        com_list = serial.tools.list_ports.comports()
        for com in com_list:
            # print(com)
            for serial_number in self.serial_numbers:
                # print(com.serial_number, serial_number)
                if com.serial_number is not None:
                    if com.serial_number.find(serial_number) >= 0:
                        # print(com.device)
                        self.port = com.device
                        try:
                            self.open()
                            self.state = 1
                            self.nansw = 0
                            return True
                        except serial.serialutil.SerialException as error:
                            return False
        self.state = -1
        return False

    def close_id(self):
        self.close()
        self.state = 0
        pass

    def request(self, req_type="get_time", data=[]):
        data_to_send = []
        if req_type == "get_ser_num":
            data_to_send = self.dts_form(com=0x01)
        elif req_type == "set_gpio":
            data_to_send = self.dts_form(com=0x02, data=data)
        elif req_type == "get_gpio":
            data_to_send = self.dts_form(com=0x03)
        elif req_type == "get_adc":
            data_to_send = self.dts_form(com=0x04)
        elif req_type == "ku_on":
            data_to_send = self.dts_form(com=0x05, data=data)
        elif req_type == "ku_off":
            data_to_send = self.dts_form(com=0x06, data=data)
        elif req_type == "mko_a":
            data_to_send = self.dts_form(com=0x07, data=data)
        elif req_type == "mko_b":
            data_to_send = self.dts_form(com=0x08, data=data)
        elif req_type == "read_ib":
            data_to_send = self.dts_form(com=0x09)
        elif req_type == "dep_24v":
            data_to_send = self.dts_form(com=0x0A, data=data)
        elif req_type == "power":
            data_to_send = self.dts_form(com=0x0B, data=data)
        elif req_type == "gener_sign":
            data_to_send = self.dts_form(com=0x0C, data=data)
        else:
            data_to_send = self.dts_form(com=0x01)
        with self.com_send_lock:
            self.com_queue.append(data_to_send)
        pass

    def dts_form(self, type=0x00, com=0x01, data=None):  # data to send form
        if data:
            leng = len(data) if len(data) < 256 else 255
        else:
            leng = 0
        data_to_send = [self.d_addr, self.s_addr, self.seq_num & 0xFF, type, com, leng]
        if leng > 0:
            data_to_send.extend(data[0:leng])
        com_crc16 = crc16.calc_to_list(data_to_send, len(data_to_send))
        data_to_send.extend(com_crc16)
        self.seq_num += 1
        return data_to_send

    def get_log(self):
        with self.log_lock:
            log = copy.deepcopy(self.log_buffer)
            self.log_buffer = []
        return log

    def thread_function(self):
        try:
            while True:
                nansw = 0
                if self.is_open is True:
                    time.sleep(0.010)
                    # отправка команд
                    if self.com_queue:
                        with self.com_send_lock:
                            data_to_send = self.com_queue.pop(0)
                            comm = data_to_send[4]
                        try:
                            self.write(bytes(data_to_send))
                            nansw = 1
                            # print(bytes_array_to_str(data_to_send))
                        except serial.serialutil.SerialException as error:
                            self.state = -3
                            # print(error)
                            pass
                        with self.log_lock:
                            self.log_buffer.append(get_time() + bytes_array_to_str(bytes(data_to_send)))
                            # print("write: %.3f" % time.clock())
                        # прием ответа: ждем ответа timout ms
                        buf = bytearray(b"")
                        read_data = bytearray(b"")
                        time_start = time.clock()
                        while True:
                            time.sleep(0.01)
                            timeout = time.clock() - time_start
                            # print("%.3f" % timeout)
                            if timeout >= self.read_timeout:
                                break
                            try:
                                read_data = self.read(128)
                                self.read_data = read_data
                            except (TypeError, serial.serialutil.SerialException, AttributeError) as error:
                                self.state = -3
                                # print(error)
                                # read_data = bytearray(b"")
                                pass
                            if read_data:
                                # print(bytes_array_to_str(read_data))
                                with self.log_lock:
                                    self.log_buffer.append(get_time() + bytes_array_to_str(read_data))
                                    # print("read: %.3f" % time.clock())
                                read_data = buf + bytes(read_data)  # прибавляем к новому куску старый кусок
                                # print(bytes_array_to_str(read_data))
                                if len(read_data) >= 8:
                                    if read_data[0] == 0x00:
                                        if len(read_data) >= read_data[5] + 8:  # проверка на запрос
                                            # print(hex(crc16.calc(read_data,  read_data[5] + 6)))
                                            if 1:  # crc16.calc_to_list(read_data,  read_data[5] + 8) == [0, 0]: todo:
                                                if comm == read_data[4]:
                                                    nansw -= 1
                                                    self.state = 1
                                                    with self.ans_data_lock:
                                                        self.answer_data.append([read_data[4], read_data[6:6+read_data[5]]])
                                                        # print(self.answer_data)
                                                    break
                                                else:
                                                    self.state = -3
                                        else:
                                            buf = read_data
                                            read_data = bytearray(b"")
                                    else:
                                        buf = read_data[1:]
                                        read_data = bytearray(b"")
                                else:
                                    buf = read_data
                                    read_data = bytearray(b"")
                                pass
                            else:
                                pass
                else:
                    pass
                if nansw == 1:
                    self.state = -3
                    self.nansw += 1
                if self._close_event.is_set() is True:
                    self._close_event.clear()
                    return
        except Exception as error:
            print(error)
        pass


def get_time():
    return time.strftime("%H-%M-%S", time.localtime()) + "." + ("%.3f:" % time.clock()).split(".")[1]


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
        byte_str = "" if i%2 else " "
        byte_str += ("%02X" % bytes_array[i])
        bytes_string += byte_str
    return bytes_string