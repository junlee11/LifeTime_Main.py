import matplotlib.pyplot as plt
from PyQt5 import uic
from PyQt5.QtWidgets import *
import sys

flag_plot_delv = {'plot_btn':False}

form_class = uic.loadUiType("LT_Ui.ui")[0]
class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()              #기반 클래스의 생성자 실행 : QMainWindow의 생성자 호출
        self.setupUi(self)

        global flag_plot_delv
        self.push_LT.clicked.connect(self.fig_plot)  # self.life_path_list

    def fig_plot(self):

        if flag_plot_delv['plot_btn'] == False:
            pass
        else:
            if plt.gcf().number > 1:
                return
            elif plt.gcf().number == 1:
                pass

        self.f = plt.figure()
        x = [1, 2, 3]
        y = [1, 2, 3]
        plt.plot(x, y)
        flag_plot_delv['plot_btn'] = True
        plt.show()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()