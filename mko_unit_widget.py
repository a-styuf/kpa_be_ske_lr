# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mko_unit_widget.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(750, 160)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Frame.sizePolicy().hasHeightForWidth())
        Frame.setSizePolicy(sizePolicy)
        Frame.setMinimumSize(QtCore.QSize(750, 140))
        Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ActionButton = QtWidgets.QPushButton(Frame)
        self.ActionButton.setGeometry(QtCore.QRect(270, 100, 51, 30))
        self.ActionButton.setMinimumSize(QtCore.QSize(0, 30))
        self.ActionButton.setObjectName("ActionButton")
        self.SubaddrSpinBox = QtWidgets.QSpinBox(Frame)
        self.SubaddrSpinBox.setGeometry(QtCore.QRect(160, 50, 42, 30))
        self.SubaddrSpinBox.setMinimumSize(QtCore.QSize(0, 30))
        self.SubaddrSpinBox.setMinimum(0)
        self.SubaddrSpinBox.setMaximum(32)
        self.SubaddrSpinBox.setProperty("value", 0)
        self.SubaddrSpinBox.setObjectName("SubaddrSpinBox")
        self.AWLabel = QtWidgets.QLabel(Frame)
        self.AWLabel.setGeometry(QtCore.QRect(95, 100, 31, 30))
        self.AWLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.AWLabel.setObjectName("AWLabel")
        self.RWBox = QtWidgets.QComboBox(Frame)
        self.RWBox.setGeometry(QtCore.QRect(190, 100, 71, 30))
        self.RWBox.setMinimumSize(QtCore.QSize(0, 30))
        self.RWBox.setObjectName("RWBox")
        self.RWBox.addItem("")
        self.RWBox.addItem("")
        self.AddrSpinBox = QtWidgets.QSpinBox(Frame)
        self.AddrSpinBox.setGeometry(QtCore.QRect(50, 50, 42, 30))
        self.AddrSpinBox.setMinimumSize(QtCore.QSize(0, 30))
        self.AddrSpinBox.setMinimum(1)
        self.AddrSpinBox.setMaximum(32)
        self.AddrSpinBox.setProperty("value", 22)
        self.AddrSpinBox.setObjectName("AddrSpinBox")
        self.LengLabel = QtWidgets.QLabel(Frame)
        self.LengLabel.setGeometry(QtCore.QRect(220, 50, 60, 30))
        self.LengLabel.setMinimumSize(QtCore.QSize(60, 30))
        self.LengLabel.setObjectName("LengLabel")
        self.StatusLabel = QtWidgets.QLabel(Frame)
        self.StatusLabel.setGeometry(QtCore.QRect(230, 10, 101, 25))
        self.StatusLabel.setMinimumSize(QtCore.QSize(0, 25))
        self.StatusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.StatusLabel.setObjectName("StatusLabel")
        self.CWLine = QtWidgets.QLineEdit(Frame)
        self.CWLine.setGeometry(QtCore.QRect(25, 100, 61, 30))
        self.CWLine.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.CWLine.setFont(font)
        self.CWLine.setReadOnly(False)
        self.CWLine.setObjectName("CWLine")
        self.AWLine = QtWidgets.QLineEdit(Frame)
        self.AWLine.setGeometry(QtCore.QRect(120, 100, 61, 30))
        self.AWLine.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.AWLine.setFont(font)
        self.AWLine.setObjectName("AWLine")
        self.CWLabel = QtWidgets.QLabel(Frame)
        self.CWLabel.setGeometry(QtCore.QRect(0, 100, 31, 30))
        self.CWLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.CWLabel.setObjectName("CWLabel")
        self.NameLine = QtWidgets.QLineEdit(Frame)
        self.NameLine.setGeometry(QtCore.QRect(30, 10, 201, 25))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NameLine.sizePolicy().hasHeightForWidth())
        self.NameLine.setSizePolicy(sizePolicy)
        self.NameLine.setMinimumSize(QtCore.QSize(0, 25))
        self.NameLine.setObjectName("NameLine")
        self.LengSpinBox = QtWidgets.QSpinBox(Frame)
        self.LengSpinBox.setGeometry(QtCore.QRect(280, 50, 42, 30))
        self.LengSpinBox.setMinimumSize(QtCore.QSize(0, 30))
        self.LengSpinBox.setMinimum(1)
        self.LengSpinBox.setMaximum(32)
        self.LengSpinBox.setProperty("value", 32)
        self.LengSpinBox.setObjectName("LengSpinBox")
        self.SubaddrLabel = QtWidgets.QLabel(Frame)
        self.SubaddrLabel.setGeometry(QtCore.QRect(100, 50, 60, 30))
        self.SubaddrLabel.setMinimumSize(QtCore.QSize(60, 30))
        self.SubaddrLabel.setObjectName("SubaddrLabel")
        self.DataTable = QtWidgets.QTableWidget(Frame)
        self.DataTable.setGeometry(QtCore.QRect(330, 0, 421, 151))
        self.DataTable.setMinimumSize(QtCore.QSize(0, 150))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.DataTable.setFont(font)
        self.DataTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.DataTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.DataTable.setObjectName("DataTable")
        self.DataTable.setColumnCount(8)
        self.DataTable.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.DataTable.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.DataTable.setItem(0, 0, item)
        self.DataTable.horizontalHeader().setDefaultSectionSize(47)
        self.DataTable.horizontalHeader().setMinimumSectionSize(47)
        self.DataTable.verticalHeader().setDefaultSectionSize(25)
        self.DataTable.verticalHeader().setMinimumSectionSize(25)
        self.AddresLabel = QtWidgets.QLabel(Frame)
        self.AddresLabel.setGeometry(QtCore.QRect(-1, 50, 61, 30))
        self.AddresLabel.setMinimumSize(QtCore.QSize(50, 30))
        self.AddresLabel.setObjectName("AddresLabel")
        self.label = QtWidgets.QLabel(Frame)
        self.label.setGeometry(QtCore.QRect(0, 10, 31, 25))
        self.label.setMinimumSize(QtCore.QSize(0, 25))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.line = QtWidgets.QFrame(Frame)
        self.line.setGeometry(QtCore.QRect(10, 150, 741, 20))
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)
        Frame.setTabOrder(self.NameLine, self.AddrSpinBox)
        Frame.setTabOrder(self.AddrSpinBox, self.SubaddrSpinBox)
        Frame.setTabOrder(self.SubaddrSpinBox, self.LengSpinBox)
        Frame.setTabOrder(self.LengSpinBox, self.CWLine)
        Frame.setTabOrder(self.CWLine, self.AWLine)
        Frame.setTabOrder(self.AWLine, self.RWBox)
        Frame.setTabOrder(self.RWBox, self.ActionButton)
        Frame.setTabOrder(self.ActionButton, self.DataTable)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.ActionButton.setText(_translate("Frame", "Пуск"))
        self.AWLabel.setText(_translate("Frame", "ОС:"))
        self.RWBox.setItemText(0, _translate("Frame", "Чтение"))
        self.RWBox.setItemText(1, _translate("Frame", "Запись"))
        self.LengLabel.setText(_translate("Frame", "Длина:"))
        self.StatusLabel.setText(_translate("Frame", "Статус"))
        self.CWLabel.setText(_translate("Frame", "КС:"))
        self.SubaddrLabel.setText(_translate("Frame", "Субадр:"))
        item = self.DataTable.verticalHeaderItem(0)
        item.setText(_translate("Frame", "+0"))
        item = self.DataTable.verticalHeaderItem(1)
        item.setText(_translate("Frame", "+8"))
        item = self.DataTable.verticalHeaderItem(2)
        item.setText(_translate("Frame", "+16"))
        item = self.DataTable.verticalHeaderItem(3)
        item.setText(_translate("Frame", "+24"))
        item = self.DataTable.horizontalHeaderItem(0)
        item.setText(_translate("Frame", "0"))
        item = self.DataTable.horizontalHeaderItem(1)
        item.setText(_translate("Frame", "1"))
        item = self.DataTable.horizontalHeaderItem(2)
        item.setText(_translate("Frame", "2"))
        item = self.DataTable.horizontalHeaderItem(3)
        item.setText(_translate("Frame", "3"))
        item = self.DataTable.horizontalHeaderItem(4)
        item.setText(_translate("Frame", "4"))
        item = self.DataTable.horizontalHeaderItem(5)
        item.setText(_translate("Frame", "5"))
        item = self.DataTable.horizontalHeaderItem(6)
        item.setText(_translate("Frame", "6"))
        item = self.DataTable.horizontalHeaderItem(7)
        item.setText(_translate("Frame", "7"))
        __sortingEnabled = self.DataTable.isSortingEnabled()
        self.DataTable.setSortingEnabled(False)
        item = self.DataTable.item(0, 0)
        item.setText(_translate("Frame", "0000"))
        self.DataTable.setSortingEnabled(__sortingEnabled)
        self.AddresLabel.setText(_translate("Frame", "Адрес:"))
        self.label.setText(_translate("Frame", "0"))


