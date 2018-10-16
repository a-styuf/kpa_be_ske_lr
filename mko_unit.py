import sys
from PyQt5 import QtWidgets, QtCore
import mko_unit_widget
import configparser


class Widget(QtWidgets.QFrame, mko_unit_widget.Ui_Frame):
    def __init__(self, parent, **kw):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__(parent)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        # инициаллизация МКО #
        self.num = 0
        self.name = "..."
        for key in sorted(kw):
            if key == "mko":
                self.mko = kw.pop(key)
            elif key == "num":
                self.num = kw.pop(key)
            elif key == "name":
                self.name = kw.pop(key)
            else:
                pass
        #
        # self.ta1_mko = TA1()
        # self.ta1_mko.init()
        # конфигурация
        self.cfg_dict = {"addr": "22",
                         "subaddr": "1",
                         "leng": "32",
                         "data": "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",
                         "name": "Test",
                         "type": "write",
                         }
        self.state = 0
        self.action_state = 0
        self.bus_state = 0
        self.addr = 0
        self.subaddr = 0
        self.leng = 0
        self.data = [0, 0]
        self.table_data = [["Нет данных", ""]]
        #
        self.load_cfg()
        #
        self.label.setText("%d" % self.num)
        self.ActionButton.clicked.connect(self.action)

    def set_num(self, n):
        self.num = n
        self.label.setText("%d" % self.num)

    def load_cfg(self, cfg_dict=None):
        if cfg_dict:
            self.cfg_dict = cfg_dict
        self.name = self.cfg_dict.get("name", "NA")
        self.NameLine.setText(self.name)
        self.addr = self.cfg_dict.get("addr", "1")
        self.AddrSpinBox.setValue(int(self.addr))
        self.subaddr = self.cfg_dict.get("subaddr", "1")
        self.SubaddrSpinBox.setValue(int(self.subaddr))
        self.leng = self.cfg_dict.get("leng", "1")
        self.LengSpinBox.setValue(int(self.leng))
        data = self.cfg_dict.get("data", "0 0 0 0").split(" ")
        self.data = [int(var, 16) for var in data]
        self.insert_data(self.data)
        self.action_state = 0 if self.cfg_dict.get("subaddr", "read") else 1
        if self.action_state == 0:
            self.RWBox.setCurrentText("Чтение")
        else:
            self.RWBox.setCurrentText("Запись")

    def get_cfg(self):
        self.name = self.NameLine.text()
        self.cfg_dict["name"] = self.name
        self.addr = self.AddrSpinBox.value()
        self.cfg_dict["addr"] = "%d" % self.addr
        self.subaddr = self.SubaddrSpinBox.value()
        self.cfg_dict["subaddr"] = "%d" % self.subaddr
        self.leng = self.LengSpinBox.value()
        self.cfg_dict["leng"] = "%d" % self.leng
        self.get_data()
        self.cfg_dict["data"] = " ".join(["%04X" % var for var in self.data])
        self.cfg_dict["type"] = "read" if self.action_state == 0 else "write"
        return self.cfg_dict

    def write(self):
        self.connect()
        self.ta1_mko.SendToRT\
            (int(self.AddrSpinBox.value()), int(self.SubaddrSpinBox.value()),
             self.get_data(), int(self.LengSpinBox.value()))
        self.AWLine.setText("0x{:04X}".format(self.ta1_mko.answer_word))
        self.CWLine.setText("0x{:04X}".format(self.ta1_mko.command_word))
        self.state_check()
        self.ta1_mko.disconnect()
        pass

    def read(self):
        self.connect()
        self.data = self.ta1_mko.ReadFromRT(int(self.AddrSpinBox.value()), int(self.SubaddrSpinBox.value()),
                                            int(self.LengSpinBox.value()))
        self.insert_data(self.data)
        self.AWLine.setText("0x{:04X}".format(self.ta1_mko.answer_word))
        self.CWLine.setText("0x{:04X}".format(self.ta1_mko.command_word))
        self.ta1_mko.disconnect()
        self.state_check()
        pass

    def action(self):
        if self.RWBox.currentText() in "Чтение":  # read
            self.read()
            # self.table_data = luna_data.frame_parcer(self.data)
        else:
            self.write()
        pass

    def state_check(self):
        # print(self.state, self.ta1_mko.bus_state)
        self.state = self.ta1_mko.state
        if self.state == 1:
            self.StatusLabel.setText("TA1-USB")
            self.StatusLabel.setStyleSheet('QLabel {background-color: orangered;}')
        elif self.state == 2:
            self.StatusLabel.setText("Аппаратура")
            self.StatusLabel.setStyleSheet('QLabel {background-color: coral;}')
        elif self.ta1_mko.bus_state == 1:
            self.StatusLabel.setText("Линия 1")
            self.StatusLabel.setStyleSheet('QLabel {background-color: coral;}')
        elif self.ta1_mko.bus_state == 2:
            self.StatusLabel.setText("Линия 2")
            self.StatusLabel.setStyleSheet('QLabel {background-color: coral;}')
        elif self.state == 0:
            self.StatusLabel.setText("Норма")
            self.StatusLabel.setStyleSheet('QLabel {background-color: seagreen;}')
        pass

    def connect(self):
        self.state = self.ta1_mko.init()
        return self.state

    def insert_data(self, data):
        for row in range(self.DataTable.rowCount()):
            for column in range(self.DataTable.columnCount()):
                try:
                    table_item = QtWidgets.QTableWidgetItem("%04X" % data[row*8 + column])
                except IndexError:
                    table_item = QtWidgets.QTableWidgetItem("0000")
                self.DataTable.setItem(row, column, table_item)
        pass

    def get_data(self):
        data = []
        for row in range(self.DataTable.rowCount()):
            for column in range(self.DataTable.columnCount()):
                data.append(int(self.DataTable.item(row, column).text(), 16))
                # print(row, column, int(self.DataTable.item(row, column).text(), 16))
        self.data = data
        return self.data


class Widgets(QtWidgets.QVBoxLayout):
    action = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.unit_list = []
        self.table_data = []
        pass

    def add_unit(self):
        widget_to_add = Widget(self.parent, num=len(self.unit_list))
        self.unit_list.append(widget_to_add)
        self.addWidget(widget_to_add)
        widget_to_add.ActionButton.clicked.connect(self.multi_action)
        pass

    def multi_action(self):
        sender = self.sender().parentWidget()
        self.table_data = sender.table_data
        self.action.emit()

    def delete_unit_by_num(self, n):
        try:
            widget_to_dlt = self.unit_list.pop(n)
            widget_to_dlt.deleteLater()
            # self.unit_layout.removeWidget(widget_to_dlt)
            for i in range(len(self.unit_list)):
                self.unit_list[i].set_num(i)
        except IndexError:
            pass
        self.update()
        pass

    def delete_all_units(self):
        for i in range(self.count()):
            self.itemAt(0).widget().close()
            self.takeAt(0)
        self.unit_list = []
        pass

    def redraw(self):
        self.update()
        pass

    def get_cfg(self, config):
        for i in range(len(self.unit_list)):
            cfg_dict = self.unit_list[i].get_cfg()
            config[str(i)] = cfg_dict
        return config

    def load_cfg(self, config):
        units_cfg = config.sections()
        self.delete_all_units()
        for i in range(len(units_cfg)):
            self.add_unit()
            self.unit_list[-1].load_cfg(config[units_cfg[i]])
        return config


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = Widget()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
