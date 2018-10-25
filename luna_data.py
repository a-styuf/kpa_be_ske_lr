'''
    модуль собирающий в себе стандартизованные функции разбора данных
    Стандарт:
    параметры:
        frame - в виде листа с данными
    возвращает:
        table_list - список подсписков (подсписок - ["Имя", "Значение"])
'''

import crc16


def frame_parcer(frame):
    data = []
    if frame[0] == 0x0FF1:  # проверка на метку кадра
        if frame[1] == 0x0C61:  # Системный кадр
            #
            data.append(["Метка кадра", "0x%04X" % frame[0]])
            data.append(["Определитель", "0x%04X" % frame[1]])
            data.append(["Номер кадра, шт", "%d" % frame[2]])
            data.append(["Время кадра, с", "%d" % ((frame[3] << 16) + frame[4])])
            #
            data.append(["Ток 1, мА", "%d" % frame[5]])
            data.append(["Ток 2, мА", "%d" % frame[6]])
            data.append(["Ток 3, мА", "%d" % frame[7]])
            data.append(["Ток 4, мА", "%d" % frame[8]])
            data.append(["Указатель чтения", "%d" % frame[9]])
            data.append(["Указатель записи", "%d" % frame[10]])
            data.append(["Ошибки МКО", "%d" % frame[11]])
            data.append(["Счетчик включений", "%d" % ((frame[12] >> 8) & 0xFF)])
            data.append(["Рабочий комплект", "%d" % (frame[12] & 0xFF)])
            data.append(["Разность времени", "%d" % frame[13]])
            data.append(["Ошибки ВШ", "%d" % ((frame[14] >> 8) & 0xFF)])
            data.append(["Неответы ВШ", "%d" % (frame[14] & 0xFF)])
            data.append(["Статус ВШ", "0х%02X" % frame[15]])
            data.append(["Температура", "%d" % frame[16]])
            #
            data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 32)])
            pass
        elif frame[1] == 0x0C62 or frame[1] == 0x0C63 or frame[1] == 0x0C64 or frame[1] == 0x0C65 or frame[1] == 0x0C66 or frame[1] == 0x0C67:  # МПП1-2 или МПП3-4 или МПП5-6
            # подготовка
            if frame[1] == 0x0C62:
                mpp_num, a, b = 1, 9.86E-3, -2.89
            elif frame[1] == 0x0C63:
                mpp_num, a, b = 3, 9.86E-3, -2.89
            elif frame[1] == 0x0C64:
                mpp_num, a, b = 5, 9.86E-3, -2.89
            elif frame[1] == 0x0C65:
                mpp_num, a, b = 5, 9.86E-3, -2.89
            elif frame[1] == 0x0C66:
                mpp_num, a, b = 5, 9.86E-3, -2.89
            elif frame[1] == 0x0C67:
                mpp_num, a, b = 5, 9.86E-3, -2.89
            else:
                mpp_num, a, b = 5, 9.86E-3, -2.89
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
        elif frame[1] == 0x0C69:  # ДЭП
            pass
        elif frame[1] == 0x0C6A:  # БДЭП
            pass
        elif frame[1] == 0x0C6B:  # Помеховые матрица
            pass
        else:
            data.append(["Неизвестный определитель", "0"])

    else:
        data.append(["Данные не распознаны", "0"])
    return data
