import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QBrush
import main_win
import kpa_ske_lr
import mko_unit
import time
import configparser
import os


class MainWindow(QtWidgets.QMainWindow, main_win.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        #
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        #
        self.config = None
        self.config_file = None
        # ## КПА ## #
        self.kpa = kpa_ske_lr.Data()
        # # buttons
        self.ClearLogPButt.clicked.connect(self.LogTEdit.clear)
        #
        self.powOnPButt.clicked.connect(self.kpa.power_on)
        self.powOffPButt.clicked.connect(self.kpa.power_off)
        #
        self.onBEPButt.clicked.connect(lambda: self.ku_on_off(mode="on"))
        self.offBEPButt.clicked.connect(lambda: self.ku_on_off(mode="off"))
        #
        self.depP30PButt.clicked.connect(self.kpa.dep_p24v_on)
        self.depM30PButt.clicked.connect(self.kpa.dep_m24v_on)
        self.dep0PButt.clicked.connect(self.kpa.dep_0v_on)
        #
        self.DataUpdateTimer = QtCore.QTimer()
        self.DataUpdateTimer.timeout.connect(self.data_update)
        self.DataUpdateTimer.start(1000)
        # МКО #
        # контейнеры для вставки юнитов
        self.units_widgets = mko_unit.Widgets(self.scrollAreaWidgetContents, mko=self.kpa)
        self.units_widgets.action.connect(self.data_table_slot)
        self.mkoPollingPBar.setValue(0)
        self.setLayout(self.units_widgets)
        # привязка сигналов к кнопкам
        self.AddUnitPButt.clicked.connect(self.units_widgets.add_unit)
        self.DltUnitPButt.clicked.connect(self.dlt_unit)
        self.DltAllUnitsPButt.clicked.connect(self.units_widgets.delete_all_units)
        self.mkoPollingPButt.clicked.connect(self.mko_polling)
        self.LoadCfgPButt.clicked.connect(self.load_cfg)
        self.SaveCfgPButt.clicked.connect(self.save_cfg)

    # МКО #
    def mko_polling(self):
        for i in range(len(self.units_widgets.unit_list)):
            time.sleep(0.25)
            if self.units_widgets.unit_list[i].RWBox.currentText() in "Чтение":  # read
                self.units_widgets.unit_list[i].action()
                self.mkoPollingPBar.setValue(100 * i / len(self.units_widgets.unit_list))
                QtCore.QCoreApplication.processEvents()
        self.mkoPollingPBar.setValue(100)

    def dlt_unit(self):
        n = self.DltUnitNumSBox.value()
        self.units_widgets.delete_unit_by_num(n)
        pass

    def data_table_slot(self):
        # на всякий пожарный сохраняем текущую конфигурацию
        self.save_init_cfg()
        #
        table_data = self.units_widgets.table_data
        self.DataTable.setRowCount(len(table_data))
        for row in range(len(table_data)):
            for column in range(self.DataTable.columnCount()):
                try:
                    table_item = QtWidgets.QTableWidgetItem(table_data[row][column])
                    self.DataTable.setItem(row, column, table_item)
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
        except OSError:
            pass
        file_name = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Открыть файл конфигурации",
            home_dir + "\\Config",
            r"config(*.cfg);;All Files(*)"
        )[0]
        config.read(file_name)
        self.units_widgets.load_cfg(config)
        pass

    def save_cfg(self):
        home_dir = os.getcwd()
        config = configparser.ConfigParser()
        config = self.units_widgets.get_cfg(self.config)
        try:
            os.mkdir(home_dir + "\\Config")
        except OSError:
            pass
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Сохранить файл конфигурации",
            home_dir + "\\Config",
            r"config(*.cfg);;All Files(*)"
        )[0]
        try:
            with open(file_name, 'w') as configfile:
                config.write(configfile)
        except FileNotFoundError:
            pass
        pass

    # КПА #
    def data_update(self):
        # обновление лога
        for text in self.kpa.serial.get_log():
            self.LogTEdit.append(text)
        all_text = self.LogTEdit.toPlainText()
        if len(all_text) > 100000:
            self.LogTEdit.clear()
        # обновление статуса
        self.statusTEdit.clear()
        self.statusTEdit.append(self.kpa.serial.error_string)
        # чтение данных АЦП
        # self.kpa.get_adc()
        # обновляем таблицу
        self.table_write()
        # выводим кол-во неответов
        self.nanswKPASBox.setValue(self.kpa.serial.nansw)
        pass

    def table_write(self):
        adc_data, adc_color = self.kpa.get_adc_data()
        self.DataTable.setRowCount(len(adc_data))
        for row in range(len(adc_data)):
            try:
                table_item = QtWidgets.QTableWidgetItem(self.kpa.adc_name[row])
                self.DataTable.setItem(row, 0, table_item)
                table_item = QtWidgets.QTableWidgetItem("%.4G" % float(adc_data[row]))
                table_item.setBackground(QColor(adc_color[row]))
                self.DataTable.setItem(row, 1, table_item)
            except IndexError:
                pass
        pass

    def ku_on_off(self, mode="on"):
        time_ms = int(self.durationSBox.value())
        if mode in "on":
            self.kpa.ku_on(time_ms=time_ms)
        else:
            self.kpa.ku_off(time_ms=time_ms)
        pass

    #
    def closeEvent(self, event):
        self.close()
        pass


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
