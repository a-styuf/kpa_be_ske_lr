'''
    модуль собирающий в себе стандартизованные функции разбора данных
    Стандарт:
    параметры:
        frame - в виде листа с данными
    возвращает:
        table_list - список подсписков (подсписок - ["Имя", "Значение"])
'''

import crc16
from ctypes import c_int8
import threading

# замок для мультипоточного запроса разбора данных
data_lock = threading.Lock()


def frame_parcer(frame):
    with data_lock:
        data = []
        while len(frame) < 31:
            frame.append(0xFEFE)
            pass
        if frame[0] == 0x0FF1:  # проверка на метку кадра
            if frame[1] == 0x0C6F:  # Системный кадр
                #
                data.append(["Метка кадра", "0x%04X" % frame[0]])
                data.append(["Определитель", "0x%04X" % frame[1]])
                data.append(["Номер кадра, шт", "%d" % frame[2]])
                data.append(["Время кадра, с", "%d" % ((frame[3] << 16) + frame[4])])
                #
                data.append(["Ток ЦМ, мА", "%d" % frame[5]])
                data.append(["Ток МПП1-2, мА", "%d" % frame[6]])
                data.append(["Ток ДРП, ДНП, мА", "%d" % frame[7]])
                data.append(["Ток МДЭП, мА", "%d" % frame[8]])
                #
                data.append(["Указатель чтения", "%d" % frame[9]])
                data.append(["Указатель записи", "%d" % frame[10]])
                #
                data.append(["Ошибки МКО", "%d" % frame[11]])
                data.append(["Счетчик включений", "%d" % frame[12]])
                #
                data.append(["Разность времени, c", "%d" % ((frame[13] << 16) + frame[14])])
                data.append(["Кол-во синхрон., шт", "%d" % (frame[15] & 0xFF)])

                data.append(["Ошибки ВШ", "%d" % ((frame[16] >> 8) & 0xFF)])
                data.append(["Неответы ВШ", "%d" % ((frame[16]) & 0xFF)])
                data.append(["Статус работы ВШ", "0х%02X" % ((frame[17] >> 8) & 0xFF)])
                data.append(["Статус неответов ВШ", "0х%02X" % (frame[17] & 0xFF)])

                data.append(["Температура", "%d" % frame[18]])
                operating_time = (frame[19] << 16) + frame[20]
                data.append(["Время наработки, ч", "%.3f" % (operating_time/3600)])
                data.append(["Интервал измерения", "%d" % frame[21]])

                data.append(["Время синхр., c", "%d" % ((frame[22] << 16) + frame[23])])
                data.append(["Время синхр., с/256", "%d" % ((frame[24] >> 8) & 0xFF)])

                data.append(["СТМ", "%02X" % (frame[24] & 0xFF)])
                #
                data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 32)])
                pass
            elif frame[1] == 0x0C61 or frame[1] == 0x0C62 or frame[1] == 0x0C63 or frame[1] == 0x0C64 or frame[1] == 0x0C65 or frame[1] == 0x0C66:  # МПП1-2 или МПП3-4 или МПП5-6
                # подготовка
                if frame[1] == 0x0C61:
                    mpp_num, a, b = 1, 4.851E-2, -99.26
                elif frame[1] == 0x0C62:
                    mpp_num, a, b = 2, 1.408E-2, -5.986
                elif frame[1] == 0x0C63:
                    mpp_num, a, b = 3, 1.375E-2, -5.349
                elif frame[1] == 0x0C64:
                    mpp_num, a, b = 4, 1.413E-2, -6.334
                elif frame[1] == 0x0C65:
                    mpp_num, a, b = 5, 7.302E-3, -14.89
                elif frame[1] == 0x0C66:
                    mpp_num, a, b = 6, 7.447E-3, -15.23
                else:
                    mpp_num, a, b = 5, 7.447E-3, -15.23
                #
                report_str = "0x "
                for var in frame:
                    report_str += ("%04X " % var)
                # print(report_str)

                #
                data.append(["Метка кадра", "0x%04X" % frame[0]])
                data.append(["Определитель", "0x%04X" % frame[1]])
                data.append(["Номер кадра, шт", "%d" % frame[2]])
                data.append(["Время кадра, с", "%d" % ((frame[3] << 16) + frame[4])])
                #
                data.append(["Кол-во измерений, шт", "%d" % frame[5]])
                data.append(["Уставка, В", "%d" % frame[6]])
                #
                data.append(["Время регистрации, с", "%d" % ((frame[7] << 16) + frame[8])])
                data.append(["Время регистрации, мкс", "%d" % ((frame[9] << 16) + frame[10])])
                data.append(["Длительность, с", "%.3g" % (((frame[11] << 16) + frame[12])*(10**-6)/40)])
                data.append(["Переход через 0, шт", "%d" % frame[13]])
                data.append(["Пиковое значение, В", "%.3g" % (a * frame[14])])
                data.append(["Мощность, В*с", "%.3g" % (a*((frame[15] << 16) + frame[16])*(10**-6)/40)])
                data.append(["Среднее, В", "%.3g" % (a * frame[17] + b)])
                data.append(["Шум, В", "%.3g" % (a * frame[18])])
                #
                data.append(["Время регистрации, с", "%d" % ((frame[19] << 16) + frame[20])])
                data.append(["Время регистрации, мкс", "%d" % ((frame[21] << 16) + frame[22])])
                data.append(["Длительность, с", "%.3g" % (((frame[23] << 16) + frame[24])*(10**-6)/40)])
                data.append(["Переход через 0, шт", "%d" % frame[25]])
                data.append(["Пиковое значение, В", "%.3g" % (a * frame[26])])
                data.append(["Мощность, В*с", "%.3g" % (a*((frame[27] << 16) + frame[28])*(10**-6)/40)])
                data.append(["Среднее, В", "%.3g" % (a * frame[29] + b)])
                data.append(["Шум, В", "%.3g" % (a * frame[30])])
                #
                data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 32)])
                pass
            elif frame[1] == 0x0C67:  # Помеховые матрица
                # подготовка
                mpp_calibr = [  # номер, a, b
                    [1, 4.851E-2, -9.926],
                    [2, 1.408E-2, -5.986],
                    [3, 1.375E-2, -5.349],
                    [4, 1.413E-2, -6.334],
                    [5, 7.302E-3, -14.89],
                    [6, 7.447E-3, -15.23]
                ]
                #
                data.append(["Метка кадра", "0x%04X" % frame[0]])
                data.append(["Определитель", "0x%04X" % frame[1]])
                data.append(["Номер кадра, шт", "%d" % frame[2]])
                data.append(["Время кадра, с", "%d" % ((frame[3] << 16) + frame[4])])
                #
                for i in range(6):
                    for j in range(3):
                        a1, b1 = mpp_calibr[j*2][1], mpp_calibr[j*2][2]
                        a2, b2 = mpp_calibr[j*2+1][1], mpp_calibr[j*2+1][2]
                        max_1 = ((frame[5 + j + 4*i] >> 8) & 0xFF)*(2**4)
                        max_2 = ((frame[5 + j + 4*i] >> 0) & 0xFF)*(2**4)
                        U_max_1 = a1*max_1 if max_1 != 0 else 0
                        U_max_2 = a2*max_2 if max_2 != 0 else 0
                        data.append(["U МПП%d@МПП%d, В" % (i+1, 2*j+1), "%g" % U_max_1])
                        data.append(["U МПП%d@МПП%d, В" % (i+1, 2*j+2), "%g" % U_max_2])
                    data.append(["Время@МПП%d, с" % (i+1), "%d" % frame[8 + 4*i]])
                #
                data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 32)])
                pass
            elif frame[1] == 0x0C68:  # Помеховые окна
                # подготовка
                mpp_calibr = [  # номер, a, b
                    [1, 4.851E-2, -9.926],
                    [2, 1.408E-2, -5.986],
                    [3, 1.375E-3, -5.349],
                    [4, 1.413E-3, -6.334],
                    [5, 7.302E-3, -14.89],
                    [6, 7.447E-3, -15.23]
                ]
                #
                data.append(["Метка кадра", "0x%04X" % frame[0]])
                data.append(["Определитель", "0x%04X" % frame[1]])
                data.append(["Номер кадра, шт", "%d" % frame[2]])
                data.append(["Время кадра, с", "%d" % ((frame[3] << 16) + frame[4])])
                #
                for i in range(6):
                    a, b = mpp_calibr[i][1], mpp_calibr[i][2]
                    max_1 = ((frame[5 + 3*i] >> 0) & 0xFF)*(2**4)
                    max_2 = ((frame[5 + 3*i] >> 8) & 0xFF)*(2**4)
                    max_3 = ((frame[6 + 3*i] >> 0) & 0xFF)*(2**4)
                    U_max_1 = a*max_1 + b if max_1 != 0 else 0
                    U_max_2 = a*max_2 + b if max_2 != 0 else 0
                    U_max_3 = a*max_3 + b if max_3 != 0 else 0
                    data.append(["Граница_1@МПП%d, В" % (i + 1), "%g" % U_max_1])
                    data.append(["Граница_2@МПП%d, В" % (i + 1), "%g" % U_max_2])
                    data.append(["Граница_3@МПП%d, В" % (i + 1), "%g" % U_max_3])
                    num_1_row = ((frame[6 + 3*i] >> 8) & 0xFF)
                    num_2_row = ((frame[7 + 3*i] >> 0) & 0xFF)
                    num_3_row = ((frame[7 + 3*i] >> 8) & 0xFF)
                    num_1 = (num_1_row & 0x0F) * 2**(num_1_row >> 4)
                    num_2 = (num_2_row & 0x0F) * 2**(num_2_row >> 4)
                    num_3 = (num_3_row & 0x0F) * 2**(num_3_row >> 4)
                    data.append(["Кол-во_1@МПП%d, В" % (i + 1), "%g" % num_1])
                    data.append(["Кол-во_2@МПП%d, В" % (i + 1), "%g" % num_2])
                    data.append(["Кол-во_3@МПП%d, В" % (i + 1), "%g" % num_3])
                #
                data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 32)])
                pass
            elif frame[1] == 0x0C69:  # ДЭП
                #
                data.append(["Метка кадра", "0x%04X" % frame[0]])
                data.append(["Определитель", "0x%04X" % frame[1]])
                data.append(["Номер кадра, шт", "%d" % frame[2]])
                data.append(["Время кадра, с", "%d" % ((frame[3] << 16) + frame[4])])
                #
                for i in range(6):
                    # dbg_str = "field: %.3f; 0х%04X;\t" % (dep_field(frame[5 + 4 * i]), frame[5 + 4 * i])
                    # dbg_str += "freq: %.3f; 0х%04X;\t" % (dep_freq((frame[6 + 4 * i] >> 8) & 0xFF), ((frame[6 + 4 * i] >> 8) & 0xFF))
                    # dbg_str += "temp: %.3f; 0х%04X;\t" % (c_int8(((frame[6 + 4 * i] >> 0) & 0xFF)).value, ((frame[6 + 4 * i] >> 0) & 0xFF))
                    # dbg_str += "field: %.3f; 0х%04X;\t" % (dep_field(frame[7 + 4 * i]), frame[5 + 4 * i])
                    # dbg_str += "freq: %.3f; 0х%04X;\t" % (dep_freq((frame[8 + 4 * i] >> 8) & 0xFF), ((frame[8 + 4 * i] >> 8) & 0xFF))
                    # dbg_str += "temp: %.3f; 0х%04X;\t" % (c_int8(((frame[8 + 4 * i] >> 0) & 0xFF)).value, ((frame[8 + 4 * i] >> 0) & 0xFF))
                    # print(dbg_str)
                    data.append(["U%d ДЭП1, кВ/м" % (i+1), "%.2f" % dep_field(frame[5 + 4 * i])])
                    data.append(["F%d ДЭП1, Гц" % (i+1), "%.1f" % dep_freq((frame[6 + 4 * i] >> 8) & 0xFF)])
                    data.append(["T%d ДЭП1, °C" % (i+1), "%d" % c_int8(((frame[6 + 4 * i] >> 0) & 0xFF)).value])
                    #
                    data.append(["U%d ДЭП2, кВ" % (i+1), "%.2f" % dep_field(frame[7 + 4 * i])])
                    data.append(["F%d ДЭП2, Гц" % (i+1), "%.1f" % dep_freq((frame[8 + 4 * i] >> 8) & 0xFF)])
                    data.append(["T%d ДЭП2, °C" % (i+1), "%d" % c_int8(((frame[8 + 4 * i] >> 0) & 0xFF)).value])
                    pass
                #
                data.append(["№ смены интервала", "%d" % frame[29]])
                data.append(["Интервал", "%d" % frame[30]])
                data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 32)])
                pass
            elif frame[1] == 0x0C6A:  # БДЭП
                pass
            else:
                data.append(["Неизвестный определитель", "0"])
        else:
            data.append(["Данные не распознаны", "0"])
        return data


def _int_to_time(sec):
    return [sec//3600, (sec//60) % 60, sec % 60]


def dep_field(data, a=0.1, b=0):
    scale = data >> 15
    mantissa = (data & 0x3FF)
    if (mantissa & 0x200) == 0:
        mantissa = - mantissa
        pass
    else:
        mantissa = (((~mantissa) + 1) & 0x3FF)
    degree = (data >> 10) & 0x1F
    sign = ((data >> 9) & 0x01)
    field = (mantissa * (2 ** (23 - degree)) * (10 ** (-scale)) / (2 ** 18)) * a + b
    return (-1**sign) * field


def dep_freq(data):
        if data > 127:
            data -= 256
        freq = 5e6 / (33333 + (data * (2 ** 7)))
        return freq
