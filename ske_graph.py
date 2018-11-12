# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QTableWidgetItem

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class Layout(QVBoxLayout):
    def __init__(self, root):
        super().__init__()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.canvas, root)
        # self.addWidget(self.toolbar)
        self.addWidget(self.canvas)

    def plot_power_data(self, time, voltage, power):
        try:
            # отрисуем график
            self.figure.clear()
            # create an axis
            axes = self.figure.add_subplot(111)
            # plot data
            axes.plot(time, voltage, line_type_from_index(0), label=u"Напряжение")
            axes.plot(time, power, line_type_from_index(1), label=u"Мощность")
            axes.set_title("Данные потреблеия БЭ СКЭ-ЛР")
            axes.set_ylabel("Напряжение, В / Мощность, Вт")
            axes.set_xlabel("Время, с")
            axes.set_ylim(bottom=0)
            axes.legend(loc=0)
            axes.grid()
            # refresh canvas
            self.canvas.draw()
        except Exception as error:
            print(error)
        pass


def line_type_from_index(n):
    color_line = ["b", "r", "g", "c", "m", "y", "k"]
    style_line = ["-", "--", "-.", ":"]
    try:
        color = color_line[n % len(color_line)]
        style = style_line[n // len(color_line)]
        return style + color
    except IndexError:
        return "-r"
