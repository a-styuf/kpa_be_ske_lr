import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QBrush
import main_win
import kpa_ske_lr


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
        self.depP30PButt.clicked.connect(self.kpa.dep_p24v_on)
        self.depM30PButt.clicked.connect(self.kpa.dep_m24v_on)
        self.dep0PButt.clicked.connect(self.kpa.dep_0v_on)
        #
        self.DataUpdateTimer = QtCore.QTimer()
        self.DataUpdateTimer.timeout.connect(self.data_update)
        self.DataUpdateTimer.start(500)

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
        self.kpa.get_adc()
        # обновляем таблицу
        self.kpa.parc_data()
        self.table_write()
        # выводим кол-во неответов
        self.nanswKPASBox.setValue(self.kpa.serial.nansw)
        pass

    def table_write(self):
        self.DataTable.setRowCount(len(self.kpa.adc_data))
        for row in range(len(self.kpa.adc_data)):
            try:
                table_item = QtWidgets.QTableWidgetItem(self.kpa.adc_name[row])
                self.DataTable.setItem(row, 0, table_item)
                table_item = QtWidgets.QTableWidgetItem("%d" % self.kpa.adc_data[row])
                table_item.setBackground(QColor(self.kpa.get_adc_data_color_scheme(row)))
                self.DataTable.setItem(row, 1, table_item)
            except IndexError:
                pass
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
