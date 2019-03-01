import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor, QBrush
import main_win
import kpa_ske_lr
import mko_unit
import time
import configparser
import os
import ske_graph


class MainWindow(QtWidgets.QMainWindow, main_win.Ui_main_win):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        #
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.setWindowIcon(QtGui.QIcon('main_icon.png'))
        # ## КПА ## #
        self.kpa = kpa_ske_lr.Data()
        #
        self.config = None
        self.config_file = None
        self.log_file = None
        self.kpa_adc_log_file = None
        self.mko_log_file = None
        self.recreate_log_files()
        # # buttons
        self.ClearLogPButt.clicked.connect(self.LogTEdit.clear)
        #
        self.powOnPButt.clicked.connect(self.kpa.power_on)
        self.powOffPButt.clicked.connect(self.kpa.power_off)
        #
        self.durationSBox.valueChanged.connect(self.SKE_durationSBox.setValue)  # дублируем значение в поле вкладки СКЭ
        self.onBEPButt.clicked.connect(lambda: self.ku_on_off(mode="on"))
        self.offBEPButt.clicked.connect(lambda: self.ku_on_off(mode="off"))
        #
        self.depP30PButt.clicked.connect(self.kpa.dep_p24v_on)
        self.depM30PButt.clicked.connect(self.kpa.dep_m24v_on)
        self.dep0PButt.clicked.connect(self.kpa.dep_0v_on)
        #
        self.DataUpdateTimer = QtCore.QTimer()
        self.DataUpdateTimer.timeout.connect(self.data_request)
        self.DataUpdateTimer.start(1000)
        #
        self.adcSinglePButt.clicked.connect(self.single_request)
        self.adcTableTimer = QtCore.QTimer()
        self.adcTableTimer.timeout.connect(self.data_gui_update)
        # МКО #
        # контейнеры для вставки юнитов
        self.units_widgets = mko_unit.Widgets(self.scrollAreaWidgetContents, mko=self.kpa)
        self.units_widgets.action.connect(self.data_table_slot)
        self.mkoPollingPBar.setValue(0)
        self.setLayout(self.units_widgets)
        # привязка сигналов к кнопкам
        #
        self.AddUnitPButt.clicked.connect(self.units_widgets.add_unit)
        self.DltUnitPButt.clicked.connect(self.dlt_unit)
        self.DltAllUnitsPButt.clicked.connect(self.units_widgets.delete_all_units)
        #
        self.LoadCfgPButt.clicked.connect(self.load_cfg)
        self.SaveCfgPButt.clicked.connect(self.save_cfg)
        #
        self.mkoPollingPButt.clicked.connect(self.mko_polling)
        #
        self.cycleTimer = QtCore.QTimer()
        self.cycleTimer.timeout.connect(self.start_mko_cycle)
        self.cycle_step_count = 0
        self.cycleStartPButt.clicked.connect(lambda: self.cycleTimer.start(1000))
        self.cycleStopPButt.clicked.connect(self.stop_mko_cycle)
        # СКЭ #
        # Питание, КУa
        self.SKE_powOnPButt.clicked.connect(self.kpa.power_on)
        self.SKE_powOffPButt.clicked.connect(self.kpa.power_off)
        self.SKE_durationSBox.valueChanged.connect(self.durationSBox.setValue)  # дублируем значение в поле вкладки КПА
        self.SKE_onBEPButt.clicked.connect(lambda: self.ku_on_off(mode="on"))
        self.SKE_offBEPButt.clicked.connect(lambda: self.ku_on_off(mode="off"))
        # Тестовые воздействия
        # ДЭП
        self.SKE_depP30PButt.clicked.connect(lambda: self.test_signal_dep(voltage=24))
        self.SKE_depM30PButt.clicked.connect(lambda: self.test_signal_dep(voltage=-24))
        self.SKE_dep0PButt.clicked.connect(lambda: self.test_signal_dep(voltage=0))
        # МПП
        self.SKE_mpp12PButt.clicked.connect(
            lambda: self.kpa.mpp_test_sign(dev="mpp", u_max=10, u_min=0, T=900, t=1, N=20, M=1))
        self.SKE_dnp_drp_PButt.clicked.connect(
            lambda: self.kpa.mpp_test_sign(dev="dnp", u_max=10, u_min=0, T=900, t=1, N=20, M=1))
        self.SKE_rp12PButt.clicked.connect(
            lambda: self.kpa.mpp_test_sign(dev="rp", u_max=10, u_min=0, T=900, t=1, N=20, M=1))
        # Циклическое воздействие
        self.testCycleCBox.stateChanged.connect(self.test_cycle_start_stop)
        self.testCycleTimer = QtCore.QTimer()
        self.testCycleTimer.timeout.connect(self.test_cycle_body)
        self.test_count = 0
        # Управление интервалом измерения

        self.SKE_mInterval60sRButt.clicked.connect(lambda: self.kpa.send_mko_comm_message(c_type="meas_interval",
                                                                                          data=[1]))
        self.SKE_mInterval120sRButt.clicked.connect(lambda: self.kpa.send_mko_comm_message(c_type="meas_interval",
                                                                                           data=[2]))
        self.SKE_mInterval240sRButt.clicked.connect(lambda: self.kpa.send_mko_comm_message(c_type="meas_interval",
                                                                                           data=[3]))
        self.SKE_dbgMIntPbutton.clicked.connect(lambda: self.kpa.send_mko_tech_comm_message(c_type="dbg_int",
                                                                                            data=[10, 10]))
        self.SKE_mInterval1sPButton.clicked.connect(self.speedy_mode)
        # Тестирование СКЭ
        self.SKE_SkeTestStartPButt.clicked.connect(self.ske_test_start)
        self.SKE_SkeTestStopPButt.clicked.connect(self.ske_test_stop)
        self.test_file = None
        # Графики напряжения и мощности
        self.ske_graph_layout = ske_graph.Layout(self.SKE_GrView)
        self.SKE_GrView.setLayout(self.ske_graph_layout)
        # ## Общие ## #
        self.logsUpdatePButt.clicked.connect(self.recreate_log_files)
        self.connectPButt.clicked.connect(self.kpa.reconnect)
        self.disconnectPButt.clicked.connect(self.kpa.disconnect)
        #
        self.load_init_cfg()

    # МКО #
    def mko_polling(self):
        for i in range(len(self.units_widgets.unit_list)):
            time.sleep(0.5)
            if self.units_widgets.unit_list[i].RWBox.currentText():  # read
                self.units_widgets.unit_list[i].action()
                self.mkoPollingPBar.setValue(100 * i / len(self.units_widgets.unit_list))
                QtCore.QCoreApplication.processEvents()
        self.mkoPollingPBar.setValue(100)

    def start_mko_cycle(self):
        period = self.cycleIntervalSBox.value()
        self.cycleTimer.setInterval(period * 1000)
        #
        unit_num = len(self.units_widgets.unit_list)
        if self.cycle_step_count == 0:
            self.cycle_step_count = self.cycleNumSBox.value() * unit_num
            return
        else:
            self.cycle_step_count -= 1
            if self.cycle_step_count == 0:
                self.stop_mko_cycle()
        elapsed_time = period * self.cycle_step_count
        self.cycleElapsedTimeTEdit.setTime(QtCore.QTime(0, 0).addSecs(elapsed_time))
        #
        self.units_widgets.unit_list[(unit_num - 1) - (self.cycle_step_count % unit_num)].action()
        #
        try:
            self.cyclePBar.setValue(100 - ((100 * self.cycle_step_count) / (self.cycleNumSBox.value() * unit_num)))
        except ValueError:
            self.cyclePBar.setValue(100)
        pass

    def stop_mko_cycle(self):
        self.cyclePBar.setValue(0)
        self.cycleTimer.stop()
        self.cycle_step_count = 0
        self.cycleElapsedTimeTEdit.setTime(QtCore.QTime(0, 0))
        pass

    def dlt_unit(self):
        n = self.DltUnitNumSBox.value()
        self.units_widgets.delete_unit_by_num(n)
        pass

    def data_table_slot(self, table_data):
        # на всякий пожарный сохраняем текущую конфигурацию
        self.save_init_cfg()
        #
        # print(table_data)
        self.mkoDataTable.setRowCount(len(table_data))
        for row in range(len(table_data)):
            for column in range(self.mkoDataTable.columnCount()):
                try:
                    table_item = QtWidgets.QTableWidgetItem(table_data[row][column])
                    self.mkoDataTable.setItem(row, column, table_item)
                except IndexError:
                    pass
        pass

    def load_init_cfg(self):
        self.config = configparser.ConfigParser()
        file_name = "init.cfg"
        self.config.read(file_name)
        # print(self.config.sections())
        if self.config.sections():
            self.units_widgets.load_cfg(self.config)
        else:
            self.units_widgets.add_unit()
        pass

    def save_init_cfg(self):
        self.config = configparser.ConfigParser()
        self.config = self.units_widgets.get_cfg(self.config)
        # print(self.config)
        file_name = "init.cfg"
        try:
            with open(file_name, 'w') as configfile:
                self.config.write(configfile)
        except FileNotFoundError:
            pass
        pass

    def load_cfg(self):
        config = configparser.ConfigParser()
        home_dir = os.getcwd()
        try:
            os.mkdir(home_dir + "\\Config")
        except OSError as error:
            print(error)
            pass
        file_name = QtWidgets.QFileDialog.getOpenFileName(self,
                                                          "Открыть файл конфигурации",
                                                          home_dir + "\\Config",
                                                          r"config(*.cfg);;All Files(*)")[0]
        config.read(file_name)
        self.units_widgets.load_cfg(config)
        pass

    def save_cfg(self):
        home_dir = os.getcwd()
        config = configparser.ConfigParser()
        config = self.units_widgets.get_cfg(config)
        try:
            os.mkdir(home_dir + "\\Config")
        except OSError:
            pass
        file_name = QtWidgets.QFileDialog.getSaveFileName(self,
                                                          "Сохранить файл конфигурации",
                                                          home_dir + "\\Config",
                                                          r"config(*.cfg);;All Files(*)")[0]
        try:
            configfile = open(file_name, 'w')
            config.write(configfile)
            configfile.close()
        except FileNotFoundError as error:
            print(error)
            pass
        pass

    # КПА #
    def single_request(self):
        # чтение данных АЦП
        self.kpa.get_adc()
        # обновляем таблицу
        self.adcTableTimer.start(500)
        pass

    def data_request(self):
        self.DataUpdateTimer.start(self.adcPeriodSBox.value() * 1000)
        if self.adcCycleCBox.isChecked():
            if self.kpa.serial.is_open:
                # чтение данных АЦП
                self.single_request()
        pass

    def ku_on_off(self, mode="on"):
        time_ms = int(self.SKE_durationSBox.value())
        if mode in "on":
            self.kpa.ku_on(time_ms=time_ms)
        else:
            self.kpa.ku_off(time_ms=time_ms)
        pass

    # СКЭ #
    def ske_test_start(self):
        try:
            # на всякий пожарный отключаем таймер для подачи тестовых воздействий
            self.test_cycle_stop()
            # узнаем измерительный интервал
            if self.SKE_dbgMIntPbutton.isChecked():
                meas_interval = 10
            elif self.SKE_mInterval60sRButt.isChecked():
                meas_interval = 60
            elif self.SKE_mInterval120sRButt.isChecked():
                meas_interval = 120
            elif self.SKE_mInterval240sRButt.isChecked():
                meas_interval = 240
            else:
                meas_interval = 240
            #
            self.SKE_SkeTestStartPButt.setEnabled(False)
            self.SKE_SkeTestStopPButt.setEnabled(True)
            #
            testing_status, testing_color = "Норма", "palegreen"
            # пишем статус начала проверки
            self.SKE_SkeTestLabel.setText("Тестирование %.1f мин" % ((22 + meas_interval*11)/60))
            self.SKE_SkeTestLabel.setStyleSheet("background-color: " + "gold")
            #
            self.SKE_testResultTWidget.setRowCount(0)
            #
            self.kpa.ske_test_start(meas_interval=meas_interval)  # !! тело теста !!
            while self.kpa.ske_test_status == 0:
                QtCore.QCoreApplication.processEvents()
            test_report_file_str = ""
            self.SKE_testResultTWidget.setRowCount(len(self.kpa.test_data_name))
            for row in range(len(self.kpa.test_data_name)):
                table_item = QtWidgets.QTableWidgetItem(self.kpa.test_data_name[row])
                self.SKE_testResultTWidget.setItem(row, 0, table_item)
                table_item = QtWidgets.QTableWidgetItem(self.kpa.test_data[row])
                table_item.setBackground(QColor(self.kpa.test_color[row]))
                self.SKE_testResultTWidget.setItem(row, 1, table_item)
                decision = "норма"
                if self.kpa.test_color[row] == "lightcoral":
                    decision = "не норма"
                    testing_status, testing_color = "Не норма", "lightcoral"
                test_report_file_str += self.kpa.test_data_name[row] + ";"
                test_report_file_str += self.kpa.test_data[row] + ";"
                test_report_file_str += decision + ";\n"
            if self.kpa.ske_test_status == -1:
                self.SKE_SkeTestLabel.setText("Не норма")
                self.SKE_SkeTestLabel.setStyleSheet("background-color: " + "lightcoral")
                test_report_file_str += "Проблемы с подключением."
            else:
                # пишем статус окончания проверки
                self.SKE_SkeTestLabel.setText(testing_status)
                self.SKE_SkeTestLabel.setStyleSheet("background-color: " + testing_color)
            # Запишем файл с результатом опроса
            self.write_test_data(test_report_file_str)
        except Exception as error:
            testing_status, testing_color = "Ошибка", "lightcoral"
            # пишем статус окончания проверки
            self.SKE_SkeTestLabel.setText(testing_status)
            self.SKE_SkeTestLabel.setStyleSheet("background-color: " + testing_color)
            print(error)
        finally:
            # обновление статуса
            self.SKE_SkeTestStartPButt.setEnabled(True)
            self.SKE_SkeTestStopPButt.setEnabled(False)

    def ske_test_stop(self):
        self.kpa.test_stop_event.set()
        self.SKE_SkeTestStopPButt.setEnabled(False)

    def create_test_file(self):
        dir_name = "Tests"
        sub_dir_name = dir_name + "\\" + "Тест СКЭ-ЛР от " + time.strftime("%Y_%m_%d", time.localtime())
        try:
            os.makedirs(sub_dir_name)
        except (OSError, AttributeError) as error:
            pass
        try:
            if self.test_file:
                self.test_file.close()
        except (OSError, NameError, AttributeError) as error:
            pass
        file_name = sub_dir_name + "\\" + "Тест СКЭ-ЛР от " + time.strftime("%Y_%m_%d %H-%M-%S",
                                                                            time.localtime()) + ".csv"
        self.test_file = open(file_name, 'a')

    def close_test_file(self):
        try:
            self.test_file.close()
        except Exception as error:
            print(error)
        pass

    def write_test_data(self, report_string=""):
        self.create_test_file()
        self.test_file.write(report_string.replace(".", ","))
        self.close_test_file()

    def test_signal_dep(self, voltage=0):
        self.SKE_dep0PButt.setDown(False)
        self.SKE_depP30PButt.setDown(False)
        self.SKE_depM30PButt.setDown(False)
        self.dep0PButt.setDown(False)
        self.depP30PButt.setDown(False)
        self.depM30PButt.setDown(False)
        if voltage == 24:
            self.kpa.dep_p24v_on()
            self.SKE_depP30PButt.setDown(True)
            self.depP30PButt.setDown(True)
        elif voltage == 0:
            self.kpa.dep_0v_on()
            self.SKE_dep0PButt.setDown(True)
            self.dep0PButt.setDown(True)
        elif voltage == -24:
            self.kpa.dep_m24v_on()
            self.SKE_depM30PButt.setDown(True)
            self.depM30PButt.setDown(True)
        else:
            self.kpa.dep_0v_on()
        pass

    def test_cycle_start_stop(self):
        if self.testCycleCBox.isChecked():
            self.testCycleTimer.start(100)
            pass
        else:
            self.test_cycle_stop()
            pass

    def test_cycle_stop(self):
        self.testCycleTimer.stop()
        self.testCycleCBox.setChecked(False)
        self.test_signal_dep()
        pass

    def test_cycle_body(self):
        self.testCycleTimer.setInterval(self.testCyclePeriodSBox.value() * 1000)
        if self.test_count % 3 == 0:
            self.test_signal_dep(voltage=24)
        elif self.test_count % 3 == 1:
            self.test_signal_dep(voltage=-24)
        elif self.test_count % 3 == 2:
            self.test_signal_dep(voltage=0)
        self.kpa.mpp_test_sign(dev="all",
                               u_max=(self.test_count % 200),  # от нуля до 15 В с шагом 1 В
                               u_min=0,  # от нуля до 10 вольт с шагом в 0.1 В
                               T=1000,
                               t=1*(self.test_count % 10),  # частота от 1/200мкс до 1/10мс
                               N=self.test_count % 15,  # от 1-го пика до 15
                               M=1)  # один запуск
        self.test_count += 1
        pass

    def speedy_mode(self):
        frames_choosed = 0x00
        frame_check_boxes = [self.SKE_mpp1speedChBox,
                             self.SKE_mpp2speedChBox,
                             self.SKE_mpp3speedChBox,
                             self.SKE_mpp4speedChBox,
                             self.SKE_mpp5speedChBox,
                             self.SKE_mpp6speedChBox,
                             self.SKE_matrixspeedChBox,
                             self.SKE_windspeedChBox,
                             self.SKE_depspeedChBox,
                             ]
        for i in range(len(frame_check_boxes)):
            if frame_check_boxes[i].isChecked():
                frames_choosed += 1 << i  # устанавливаем 1 для включения определенного типа кадров
        if frames_choosed != 0:
            self.kpa.send_mko_comm_message(c_type="speedy_mode", data=[1, frames_choosed & 0xFFFF])
        else:
            self.kpa.send_mko_comm_message(c_type="speedy_mode", data=[0, 0])

    def dbg_meas_mode(self):
        if self.SKE_dbgMIntPbutton.isChecked():
            self.kpa.send_mko_tech_comm_message(c_type="dbg_int", data=[10, 10])
        else:
            if self.SKE_mInterval60sRButt.isChecked():
                meas_interval_val = 1
            elif self.SKE_mInterval120sRButt.isChecked():
                meas_interval_val = 2
            elif self.SKE_mInterval240sRButt.isChecked():
                meas_interval_val = 3
            else:
                meas_interval_val = 2
            self.kpa.send_mko_comm_message(c_type="meas_interval", data=[meas_interval_val])
        pass

    # LOGs #
    def create_log_file(self, file=None, prefix=""):
        dir_name = "Logs"
        sub_dir_name = dir_name + "\\" + "Лог КПА СКЭ-ЛР от " + time.strftime("%Y_%m_%d", time.localtime())
        sub_sub_dir_name = sub_dir_name + "\\" + "Лог " + prefix + " КПА СКЭ-ЛР от " + time.strftime("%Y_%m_%d",
                                                                                                     time.localtime())
        try:
            os.makedirs(sub_sub_dir_name)
        except (OSError, AttributeError) as error:
            pass
        try:
            if file:
                file.close()
        except (OSError, NameError, AttributeError) as error:
            pass
        file_name = sub_sub_dir_name + "\\" + prefix + " КПА СКЭ-ЛР от " + time.strftime("%Y_%m_%d %H-%M-%S",
                                                                               time.localtime()) + ".txt"
        file = open(file_name, 'a')
        return file

    def close_log_file(self, file=None):
        if file:
            try:
                file.close()
            except (OSError, NameError, AttributeError) as error:
                pass
        pass

    def recreate_log_files(self):
        self.log_file = self.create_log_file(prefix="ВШ")
        self.kpa_adc_log_file = self.create_log_file(prefix="АЦП")
        self.kpa_adc_log_file.write(self.kpa.get_adc_data_title() + "\n")
        self.mko_log_file = self.create_log_file(prefix="МПИ")

        pass

    # Общией функции #
    def data_gui_update(self):
        # обновление статуса
        self.statusTEdit.clear()
        self.statusTEdit.append(self.kpa.get_state_string())
        # обновление лога
        for text in self.kpa.serial.get_log():
            self.log_file.write(text + "\n")
            self.log_file.flush()
            self.LogTEdit.append(text)
        # обновление лога АЦП КПА
        for text in self.kpa.get_adc_log():
            self.kpa_adc_log_file.write(text + "\n")
            self.kpa_adc_log_file.flush()
        # обновление лога МПИ
        for text in self.kpa.get_mko_log():
            self.mko_log_file.write(text + "\n")
            self.mko_log_file.flush()
        #
        all_text = self.LogTEdit.toPlainText()
        if len(all_text) > 100000:
            self.LogTEdit.clear()
        #
        adc_data, adc_color = self.kpa.form_kpa_data()
        # графики
        self.ske_graph_layout.plot_power_data(self.kpa.graph_data[0], self.kpa.graph_data[1], self.kpa.graph_data[2])
        # таблица для вкладки КПА
        self.DataTable.setRowCount(len(adc_data))
        for row in range(len(adc_data)):
            table_item = QtWidgets.QTableWidgetItem(self.kpa.adc_name[row])
            self.DataTable.setItem(row, 0, table_item)
            table_item = QtWidgets.QTableWidgetItem("%.4G" % float(adc_data[row]))
            table_item.setBackground(QColor(adc_color[row]))
            self.DataTable.setItem(row, 1, table_item)
        # Обновление параметров Параметры питания и СТМ-параметры вкладки СКЭ
        self.SKE_powUDSBox.setValue(self.kpa.ske_U[0])
        self.SKE_powUDSBox.setStyleSheet("background-color: " + self.kpa.ske_U[1])
        self.SKE_powIDSBox.setValue(self.kpa.ske_I[0])
        self.SKE_powIDSBox.setStyleSheet("background-color: " + self.kpa.ske_I[1])
        self.SKE_powWDSBox.setValue(self.kpa.ske_W[0])
        self.SKE_powWDSBox.setStyleSheet("background-color: " + self.kpa.ske_W[1])
        self.SKE_stm_KPBE_DSBox.setValue(self.kpa.ske_KPBE[0])
        self.SKE_stm_KPBE_DSBox.setStyleSheet("background-color: " + self.kpa.ske_KPBE[1])
        self.SKE_stm_NormCM_DSBox.setValue(self.kpa.ske_NormCM[0])
        self.SKE_stm_NormCM_DSBox.setStyleSheet("background-color: " + self.kpa.ske_NormCM[1])
        self.SKE_stm_AMKO_DSBox.setValue(self.kpa.ske_AMKO[0])
        self.SKE_stm_AMKO_DSBox.setStyleSheet("background-color: " + self.kpa.ske_AMKO[1])
        #
        self.nanswKPASBox.setValue(self.kpa.serial.nansw)
        pass

    def closeEvent(self, event):
        self.close()
        self.close_log_file(file=self.log_file)
        self.close_log_file(file=self.kpa_adc_log_file)
        self.close_log_file(file=self.mko_log_file)
        self.close_test_file()
        pass


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # os.environ["QT_SCALE_FACTOR"] = "1.0"
    #
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
