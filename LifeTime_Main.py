#210810 event 걸어야함

#수명 프로그램
import csv
import sys
import os
import re
import pandas as pd
from cycler import cycler
import openpyxl
import win32com.client as win32
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from pptx import Presentation
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

#설정
set_picker_line = None
set_picker_legend = None
set_thick_line = None
set_import_MinLT = None
set_title_font_size = None
plt.rc('axes', prop_cycle=cycler(color=[
    [0,0,0],
    [1,0,0],
    [0,1,0],
    [0,0,1],
    [1,0,1],
    [0,1,1],
    [0.5,0,0],
    [0,0.5,0],
    [0,0,0.5],
    [0.5,0.5,0],
    [0.5,0,0.5],
    [0,0.5,0.5],
    [0.75,0.75,0.75],
    [0.5,0.5,0.5],
    [0.6,0.6,1],
    [0.6,0.2,0.4],
    [0.2,1,0.8],
    [0.8,1,1],
    [0.4,0,0.4],
    [1,0.5,0.5],
    [0,0.4,0.8],
    [0.8,0.8,1],
    [0,0,0.5],
    [0.5,0,1],
    [1,1,0]
]))

flag_plot_delv = {'plotMax':False, 'delV':False, 'merge':False, 'plotMax_btn':False, 'delV_btn':False, 'path_find':0, 'plot_btn':False, 'LT_table_btn':False}
lot_f_list = []
dic_Lot_row = {}

#Setting.txt를 Dict로 가져오기
with open('Setting.txt', 'r') as f:
    reader = csv.reader(f)
    set_dic = {rows[0]:rows[1].lstrip() for rows in reader}

##증착기, 수명호기 경로 지정하기########################################
#file_pc_path = open("pc_path.txt","rt",encoding = "UTF8")
file_pc_path = pd.read_csv('pc_path.txt')

try:
    path_depo1 = file_pc_path.query('EQP=="증착1호기"')['Path'][0] + '/'
    path_depo2 = file_pc_path.query('EQP=="증착2호기"')['Path'][1] + '/'
    df_life_path = file_pc_path.loc[file_pc_path['EQP'].isin(['수명1호기', '수명2호기', '수명3호기', '수명4호기', '수명5호기', '수명6호기', '수명7호기'])]
    df_life_path = df_life_path.loc[~df_life_path['Path'].isnull()]
except:
    pass

def replace_special(s):
  # add more characters to regex, as required
  return re.sub('[★]', ' ', s)

def isNumber(s):
    if np.isnan(float(s)):
        return s != s
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False

def arr_path(f_path):
    #1. 숨김 파일 삭제
    #2. 엑셀 파일 모으고
    #3. 폴더, 엑셀 리스트 각각 오름차순 정렬
    #4. Merge
    f_path_list = os.listdir(f_path)
    excel_list = []
    powerpoint_list = []
    folder_list =[]

    for i in f_path_list[:]:

        #숨김 파일 리스트에서 삭제
        if '$' in i:
            f_path_list.remove(i)

        elif os.path.isdir(f_path+i):
            folder_list.append(i)
            f_path_list.remove(i)

        elif 'xls' in os.path.splitext(f_path+i)[1]:
            excel_list.append(i)
            f_path_list.remove(i)

        elif 'ppt' in os.path.splitext(f_path+i)[1]:
            powerpoint_list.append(i)
            f_path_list.remove(i)

    folder_list.sort()
    excel_list.sort()
    powerpoint_list.sort()
    f_path_list.sort()

    folder_list = sorted(folder_list, key=replace_special)
    excel_list = sorted(excel_list, key=replace_special)
    powerpoint_list = sorted(powerpoint_list, key=replace_special)
    f_path_list = sorted(f_path_list, key=replace_special)

    return folder_list + excel_list + powerpoint_list + f_path_list

#해당 경로 폴더 열때 os.startfile(path_depo1)

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("LT_Ui.ui")[0]
form_class_set = uic.loadUiType("Setting_Ui.ui")[0]
form_class_LT_table = uic.loadUiType("LT_Table.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
#QMainWindow Class를 상속
class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()              #기반 클래스의 생성자 실행 : QMainWindow의 생성자 호출
        self.setupUi(self)

        global set_dic
        global flag_plot_delv
        global lot_f_list
        global dic_lot_row
        self.list1_path = ""
        self.list2_path = ""
        self.list3_path = ""
        self.list4_path = ""
        self.list5_path = ""
        self.basic_list_arr = [self.list1, self.list2, self.list3, self.list4, self.list5, self.Lot_list]
        self.basic_path_arr = [self.list1_path, self.list2_path, self.list3_path, self.list4_path, self.list5_path]
        self.basic_list_arr[0].addItem("증착 1호기")
        self.basic_list_arr[0].addItem("증착 2호기")
        self.all_path.setReadOnly(True)

        #경로 생성
        self.list1.itemClicked.connect(self.path_list_1)
        self.list2.itemClicked.connect(self.path_list_2)
        self.list3.itemClicked.connect(self.path_list_3)
        self.list4.itemClicked.connect(self.path_list_4)
        
        #경로(파일) 열기
        self.list1.itemDoubleClicked.connect(self.dbclk_list_1)
        self.list2.itemDoubleClicked.connect(self.dbclk_list_2)
        self.list3.itemDoubleClicked.connect(self.dbclk_list_3)
        self.list4.itemDoubleClicked.connect(self.dbclk_list_4)
        self.list5.itemDoubleClicked.connect(self.dbclk_list_5)

        #Lot 열기
        self.push_LT.clicked.connect(self.lifetime_path_list)       #self.life_path_list
        self.push_LT_table.clicked.connect(self.load_LT_table)
        self.Lot_list.itemDoubleClicked.connect(self.Lot_list_del)

        #설정하기
        self.push_set.clicked.connect(self.set_up)

    #################################################################경로생성
    def path_list_1(self):
        if self.list1.currentItem().text() == "증착 1호기":
            self.list2.clear()      #list2에 변화가 가면 위의 함수가 실행되는듯
            self.list3.clear()
            self.list4.clear()
            self.list5.clear()
            self.list_to_target(path_depo1,self.list2)
            self.basic_path_arr[0] = path_depo1
            self.all_path.setPlainText(self.basic_path_arr[0])

        else:
            self.list2.clear()
            self.list3.clear()
            self.list4.clear()
            self.list5.clear()
            self.list_to_target(path_depo2,self.list2)
            self.basic_path_arr[0] = path_depo2
            self.all_path.setPlainText(self.basic_path_arr[0])

    def path_list_2(self):
        self.path_function(2)

    def path_list_3(self):
        self.path_function(3)

    def path_list_4(self):
        self.path_function(4)

    def path_function(self,n):
        if not os.path.isfile(self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text()):
            self.basic_path_arr[n-1] = self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text() + '/'

            m = n
            while m<=4:
                self.basic_list_arr[m].clear()
                m += 1

            self.list_to_target(self.basic_path_arr[n-1], self.basic_list_arr[n])
            self.all_path.setPlainText(self.basic_path_arr[n-1])

    def list_to_target(self,source_path,target_listbox):

        for i in range(len(arr_path(source_path))):
            if os.path.isdir(source_path + arr_path(source_path)[i]):
                icon = QIcon("Icon_folder.png")
            elif 'xls' in os.path.splitext(source_path + arr_path(source_path)[i])[1]:
                icon = QIcon('Icon_excel.png')
            elif 'ppt' in os.path.splitext(source_path + arr_path(source_path)[i])[1]:
                icon = QIcon('Icon_ppt.png')
            else:
                icon = QIcon('Icon_apeach.png')

            icon_item = QListWidgetItem(icon, arr_path(source_path)[i])
            target_listbox.addItem(icon_item)
    ##############################################################################################경로 생성 끝

    #####################################################################경로(파일) 열기
    def dbclk_list_1(self):
        if self.list1.currentItem().text() == "증착 1호기":
            os.startfile(path_depo1)
        else:
            os.startfile(path_depo2)

    def dbclk_list_2(self):
        self.path_open_function(2)

    def dbclk_list_3(self):
        self.path_open_function(3)

    def dbclk_list_4(self):
        self.path_open_function(4)

    def dbclk_list_5(self):
        self.path_open_function(5)

    def path_open_function(self,n):
        if os.path.isdir(self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text() + '/'):
            os.startfile(self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text() + '/')
        elif 'xls' in os.path.splitext(self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text())[1]:
            excel = win32.Dispatch("Excel.Application")
            excel.Visible = True
            excel.Workbooks.Open(self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text())
        elif 'ppt' in os.path.splitext(self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text())[1]:
            powerpoint = win32.Dispatch("Powerpoint.Application")
            powerpoint.Visible = True
            powerpoint.Presentations.Open(self.basic_path_arr[n-2] + self.basic_list_arr[n-1].currentItem().text())

    ########################################################################################경로(파일)열기 끝

    def Lot_list_del(self):
        self.Lot_list.takeItem(self.Lot_list.currentRow())

    #수명 경로 DF : df_life_path
    def lifetime_path_list(self):

        #최초 plot
        if flag_plot_delv['plot_btn'] == False: pass        #plot 그림
        else:
            #껐다가 켰을 때
            if '640x480' in str(plt.figure(1)):
                plt.close(1)
                pass
            #이미 fig 존재 할때 : Interlock
            else:
                QMessageBox.warning(self, "Path Interlock", "Plot이 있는 상태에서 추가 Plot 불가")
                return

        flag_plot_delv['delV'] = False
        flag_plot_delv['plotMax'] = False
        flag_plot_delv['merge'] = False
        flag_plot_delv['plot_btn'] = True
        flag_plot_delv['path_find'] = 0

        ##########################################################변수 초기화

        # 딕셔너리 선언 : fig - axlist - df

        self.dic_fig_ax_dfhourpassraw = {}
        self.dic_fig_ax_dfhourpassplot = {}
        self.dic_fig_ax_dfVraw = {}
        self.dic_fig_ax_dfVplot = {}
        self.dic_fig_ax_dfLTraw = {}
        self.dic_fig_ax_dfLTplot = {}
        self.dic_fig_ax_delVraw = {}
        self.dic_fig_ax_delVplot = {}
        self.dic_fig_ax_dflegend = {}
        self.dic_fig_ax_dfdelVraw = {}
        self.dic_fig_ax_dfdelVplot = {}

        self.dic_ax_dfhourpassraw = {}
        self.dic_ax_dfhourpassplot = {}
        self.dic_ax_dfVraw = {}
        self.dic_ax_dfVplot = {}
        self.dic_ax_dfLTraw = {}
        self.dic_ax_dfLTplot = {}
        self.dic_ax_dfdelVraw = {}
        self.dic_ax_dfdelVplot = {}
        self.dic_ax_dflegend = {}

        self.dic_fig_leg_LT = {}
        self.dic_fig_leg_V = {}
        self.dic_fig_LT_leg = {}
        self.dic_fig_LT_V = {}
        self.dic_fig_V_LT = {}
        self.dic_fig_V_leg = {}
        self.dic_fig_ax = {}
        self.dic_fig_on_press_line = {}
        self.dic_fig_on_press_legend = {}

        # merge
        self.dic_fig_dfhourpassraw = {}
        self.dic_fig_dfhourpassplot = {}
        self.dic_fig_dfVraw = {}
        self.dic_fig_dfVplot = {}
        self.dic_fig_dfdelVraw = {}
        self.dic_fig_dfdelVplot = {}
        self.dic_fig_dflegend = {}
        self.dic_fig_dfLTraw = {}
        self.dic_fig_dfLTplot = {}

        self.dic_fig_line_dfhourpassraw = {}
        self.dic_fig_line_dfhourpassplot = {}
        self.dic_fig_line_dfVraw = {}
        self.dic_fig_line_dfVplot = {}
        self.dic_fig_line_dfdelVraw = {}
        self.dic_fig_line_dfdelVplot = {}
        self.dic_fig_line_dfLTraw = {}
        self.dic_fig_line_dfLTplot = {}
        self.dic_fig_line_dflegend = {}

        # 리스트 선언
        self.list_fig = []
        self.list_ax = []

        # Merge용
        self.dic_fig_ax_line = {}
        self.dic_ax_line = {}

        self.flag_merge = 0 if flag_plot_delv['merge'] == False else 1

        self.lot_final_list = []

        #Lot_list 있는 만큼 반복
        self.not_find_path=[]

        for i in range(self.Lot_list.count()):
            self.Lot_name = self.Lot_list.item(i).text()[:7]
            self.Lot_year = '20' + self.Lot_name[:2]
            self.Lot_month = self.Lot_name[2:4]
            p_flag = 0

            #수명 호기 접근
            for life_eqp_path in df_life_path['Path']:
                #Lot 년도
                y_flag = 0
                for life_year in arr_path(life_eqp_path):
                    if self.Lot_year in life_year:
                        self.life_path = life_eqp_path + '\\' + life_year + '\\'
                        y_flag = 1
                        break
                #Lot 월
                m_flag = 0
                if self.Lot_month[0] == '1' and y_flag == 1:
                    for life_month in arr_path(self.life_path):
                        if self.Lot_month in life_month:
                            self.life_path = self.life_path + life_month + '\\'
                            m_flag = 1
                            break
                elif self.Lot_month[0] == '0' and y_flag == 1:
                    for life_month in arr_path(self.life_path):
                        if self.Lot_month[-1] in life_month and self.Lot_month[0] == '0':
                            self.life_path = self.life_path + life_month + '\\'
                            m_flag = 1
                            break
                #증착호기
                d_flag = 0
                if '1호기' in self.basic_list_arr[0].currentItem().text() and m_flag == 1:
                    self.life_path = self.life_path + '증착1호기' + '\\'
                    d_flag = 1
                elif '2호기' in self.basic_list_arr[0].currentItem().text() and m_flag == 1:
                    self.life_path = self.life_path + '증착2호기' + '\\'
                    d_flag = 1
                #Lot
                for life_lot in arr_path(self.life_path):
                    if self.Lot_name in life_lot and d_flag == 1:
                        self.life_path = self.life_path + life_lot + '\\'
                        self.lot_final_list.append(self.life_path)
                        flag_plot_delv['path_find'] += 1
                        p_flag = 1
                        break

            if p_flag == 0:
                self.not_find_path.append(self.Lot_name)

        total_not_find_str = ""
        if flag_plot_delv['path_find'] != self.Lot_list.count():
            for i in range(len(self.not_find_path)):
                if i == len(self.not_find_path)-1:
                    total_not_find_str = total_not_find_str + self.not_find_path[i]
                else:
                    total_not_find_str = total_not_find_str + self.not_find_path[i] + ', '
            QMessageBox.warning(self, "Path Interlock", "수명 경로를 찾을 수 없습니다.\n" + total_not_find_str)
            return
        self.plotLT(self.lot_final_list)

    
    #그래프 그리기 시작
    def plotLT(self, LT_list):                  #LT_list는 Main화면에서 추출한 경로 리스트

        # flag / idx
        self.flag_V = 0 if self.chk_V.isChecked() == False else 1

        #event용 리스트, 딕셔너리 선언
        self.picker_lines = []
        self.picker_lined = []
        self.picker_leg = []
        self.on_press_temp = []
        self.lined = {}
        self.lined_V = {}
        self.plotlined = {}
        self.plotlined_V = {}
        self.plotlined_V_torig = {}
        self.lined_V_torig = {}
        self.on_press_line = {}
        self.on_press_legend = {}
        self.xs = []
        self.ys = []
        self.list_ax = []

        #merge
        self.dic_line_dfhourpassraw = {}
        self.dic_line_dfhourpassplot = {}
        self.dic_line_dfVraw = {}
        self.dic_line_dfVplot = {}
        self.dic_line_dfdelVraw = {}
        self.dic_line_dfdelVplot = {}
        self.dic_line_dfLTraw = {}
        self.dic_line_dfLTplot = {}
        self.dic_line_dflegend = {}

        self.dic_ax_line = {}

        #merge 할때는 fig생성해서 넘어옴
        if flag_plot_delv['merge'] == False:
            self.fig = plt.figure(figsize=(float(set_dic['fig_width']), float(set_dic['fig_length'])))
            self.fig.set_facecolor('white')

        if flag_plot_delv['plotMax_btn'] == True or flag_plot_delv['delV_btn'] == True:
            plt.close(self.list_fig[self.idx_fig])

        if flag_plot_delv['merge'] == False:
            self.idx_fig = plt.gcf().number - 1
            self.list_fig.append(self.fig)

        if flag_plot_delv['merge'] == False:
            gs = self.list_fig[self.idx_fig].add_gridspec(2, len(LT_list), height_ratios=[3, 1]) if self.chk_V.isChecked()==True else self.list_fig[self.idx_fig].add_gridspec(1, len(LT_list))
        else:
            gs = self.list_fig[self.idx_fig].add_gridspec(2, 1, height_ratios=[3, 1]) if self.chk_V.isChecked()==True else self.list_fig[self.idx_fig].add_gridspec(1, 1)

        i_cnt = 0
        #Lot에 대한 반복을 진행
        for i in LT_list:

            self.df_hourpass_raw = []
            self.df_V_raw = []
            self.df_LT_raw = []
            self.df_legend = []
            self.df_delV_raw = []
            self.df_hourpass_plot = []
            self.df_LT_plot = []
            self.del_index = []
            self.df_V_plot = []
            self.df_delV_plot = []

            self.dic_ax_LTlinelist = {}
            self.dic_ax_Vlinelist = {}
            self.dic_rawline_dfhourpass = {}
            self.dic_plotline_dfhourpass = {}
            self.dic_rawline_dfV = {}
            self.dic_rawline_dfdelV = {}
            self.dic_plotline_dfV = {}
            self.dic_plotline_dfdelV = {}
            self.dic_rawline_dfLT = {}
            self.dic_plotline_dfLT = {}
            self.visible_LTline_list = []
            self.visible_Vline_list = []

            if i_cnt == 1 and flag_plot_delv['merge'] == True:
                break

            kk = 0
########################################################################################################################
##############################################1개 Lot에 대한 모든 셀의 Raw, Plot 데이터 가져오기##############################
            if flag_plot_delv['merge'] == False:
                for j in arr_path(i):
                    #몇줄을 뺄지 먼저 정해야함
                    #첫번째행의 값이 수명인지
                    if 'Hour' in str(pd.read_csv(i+j, header=None, skiprows=6, usecols=[0]).loc[0][0]):
                        row_skip = 7
                    else:
                        row_skip = 6

                    #Raw 데이터프레임
                    self.df_hourpass_raw.append(pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[0]))
                    self.df_V_raw.append(pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[2]))
                    self.df_LT_raw.append(pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[5]))
                    self.df_legend.append(os.path.splitext(j)[0])

                    #index에 usecols값이 포함된다
                    #Plot 위한 임시값
                    temp_first_V = self.df_V_raw[kk].iloc[0][2] if isNumber(str(self.df_V_raw[kk].iloc[0][2])) else 0
                    temp_max_LT = self.df_LT_raw[kk].max()[5] if isNumber(str(self.df_LT_raw[kk].max()[5])) else 0
                    temp_max_LT_index = self.df_LT_raw[kk].idxmax(axis=0)[5] if isNumber(str(self.df_LT_raw[kk].idxmax(axis=0)[5])) else 0
                    temp_max_time = self.df_hourpass_raw[kk].iloc[temp_max_LT_index][0] if isNumber(str(self.df_LT_raw[kk].max()[5])) else 0

                    #Raw 데이터 예외처리 필요
                    for a in range(temp_max_LT_index):
                        self.del_index.append(a)

                    #Plot data
                    self.df_hourpass_plot.append(pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[0]).drop(index = self.del_index).apply(lambda x : x - temp_max_time))
                    self.df_LT_plot.append(pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[5]).drop(index = self.del_index).apply(lambda x : x - (temp_max_LT-100)))
                    self.df_delV_raw.append(pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[2]).apply(lambda x : x - temp_first_V ))
                    self.df_V_plot.append(pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[2]).drop(index = self.del_index))
                    temp_max_delV = self.df_delV_raw[kk].iloc[temp_max_LT_index][2]
                    temp_df_V = pd.read_csv(i + j, header=None, skiprows=row_skip, usecols=[2]).apply(lambda x: x - temp_first_V)
                    self.df_delV_plot.append(temp_df_V.drop(index = self.del_index).apply(lambda x : x - temp_max_delV))

                    kk = kk + 1

                self.lot_name = self.df_legend[0][-15:][:11]

########################################################################################################################
########################################################################################################################

            for k in range(2):          #k=0일때 수명, k=1일때 전압
                #ax 그래프 생성
                if flag_plot_delv['merge'] == False:
                    if self.chk_V.isChecked() == True:
                        self.ax = self.fig.add_subplot(gs[k, LT_list.index(i)])
                    elif self.chk_V.isChecked() == False and k == 0:
                        self.ax = self.fig.add_subplot(gs[0,LT_list.index(i)])
                else:
                    if self.chk_V.isChecked() == True:
                        self.ax = self.fig.add_subplot(gs[k, 0])
                    elif self.chk_V.isChecked() == False and k == 0:
                        self.ax = self.fig.add_subplot(gs[0,0])

                self.list_ax.append(self.ax)

                # 하나의 ax에 대한 딕셔너리 연결
                self.dic_ax_dfhourpassraw[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_hourpass_raw
                self.dic_ax_dfhourpassplot[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_hourpass_plot
                self.dic_ax_dfVraw[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_V_raw
                self.dic_ax_dfVplot[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_V_plot
                self.dic_ax_dfLTraw[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_LT_raw
                self.dic_ax_dfLTplot[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_LT_plot
                self.dic_ax_dfdelVraw[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_delV_raw
                self.dic_ax_dfdelVplot[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_delV_plot
                self.dic_ax_dflegend[self.list_ax[LT_list.index(i) * (1 + self.flag_V) + k]] = self.df_legend

                self.dic_fig_ax_dfhourpassraw[self.list_fig[self.idx_fig]] = self.dic_ax_dfhourpassraw
                self.dic_fig_ax_dfhourpassplot[self.list_fig[self.idx_fig]] = self.dic_ax_dfhourpassplot
                self.dic_fig_ax_dfVraw[self.list_fig[self.idx_fig]] = self.dic_ax_dfVraw
                self.dic_fig_ax_dfVplot[self.list_fig[self.idx_fig]] = self.dic_ax_dfVplot
                self.dic_fig_ax_dfLTraw[self.list_fig[self.idx_fig]] = self.dic_ax_dfLTraw
                self.dic_fig_ax_dfLTplot[self.list_fig[self.idx_fig]] = self.dic_ax_dfLTplot
                self.dic_fig_ax_dfdelVraw[self.list_fig[self.idx_fig]] = self.dic_ax_dfdelVraw
                self.dic_fig_ax_dfdelVplot[self.list_fig[self.idx_fig]] = self.dic_ax_dfdelVplot
                self.dic_fig_ax_dflegend[self.list_fig[self.idx_fig]] = self.dic_ax_dflegend

                #df가지고 plot그림
                self.idx_ax = LT_list.index(i) * (1 + self.flag_V) + k

                if flag_plot_delv['merge'] == False:
                    self.draw_LT_V_graph(LT_list.index(i),k)
                else:
                    self.draw_LT_V_graph_m(LT_list.index(i),k)

                # merge
                if flag_plot_delv['plotMax'] == False:self.dic_fig_line_dfhourpassraw[self.list_fig[self.idx_fig]] = self.dic_line_dfhourpassraw
                if flag_plot_delv['plotMax'] == True:self.dic_fig_line_dfhourpassplot[self.list_fig[self.idx_fig]] = self.dic_line_dfhourpassplot
                if flag_plot_delv['plotMax'] == False:self.dic_fig_line_dfLTraw[self.list_fig[self.idx_fig]] = self.dic_line_dfLTraw
                if flag_plot_delv['plotMax'] == True:self.dic_fig_line_dfLTplot[self.list_fig[self.idx_fig]] = self.dic_line_dfLTplot
                if flag_plot_delv['plotMax'] == False and flag_plot_delv['delV'] == False:self.dic_fig_line_dfVraw[self.list_fig[self.idx_fig]] = self.dic_line_dfVraw
                if flag_plot_delv['plotMax'] == True and flag_plot_delv['delV'] == False:self.dic_fig_line_dfVplot[self.list_fig[self.idx_fig]] = self.dic_line_dfdelVplot
                if flag_plot_delv['plotMax'] == False and flag_plot_delv['delV'] == True:self.dic_fig_line_dfdelVraw[self.list_fig[self.idx_fig]] = self.dic_line_dfdelVraw
                if flag_plot_delv['plotMax'] == True and flag_plot_delv['delV'] == True:self.dic_fig_line_dfdelVplot[self.list_fig[self.idx_fig]] = self.dic_line_dfdelVplot
                self.dic_fig_line_dflegend[self.list_fig[self.idx_fig]] = self.dic_line_dflegend

            i_cnt += 1

        self.dic_fig_ax[self.list_fig[self.idx_fig]] = self.list_ax
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_press_event', self.mouse_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move)

        flag_plot_delv['plotMax_btn'] = False
        flag_plot_delv['delV_btn'] = False
        plt.show()

    def draw_LT_V_graph(self, LT_index, k):

        #전압 선택
        if k == 1 and self.chk_V.isChecked() == False:
            k = 2
        #수명 그릴 때 / 전압 그릴 때로 나누어서
        temp_picker_lines = []
        #수명 셀 반복
        for m in range(len(self.dic_fig_ax_dfhourpassraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]])):
            self.flag_LT_min = 0
            self.df_hourpass_R = self.dic_fig_ax_dfhourpassraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_ax_dfhourpassplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.df_V_R = self.dic_fig_ax_dfVraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_ax_dfVplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.df_LT_R = self.dic_fig_ax_dfLTraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_ax_dfLTplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.df_legend_R = self.dic_fig_ax_dflegend[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.df_delV_R = self.dic_fig_ax_dfdelVraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_ax_dfdelVplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]

            if k == 0 :

                if flag_plot_delv['plotMax'] == False:
                    if m == 0: self.hourpass_max_val = self.df_hourpass_R.max()[0]
                    if self.hourpass_max_val < self.df_hourpass_R.max()[0]: self.hourpass_max_val = self.df_hourpass_R.max()[0]
                    self.n_row += 1

                self.temp_l, = self.ax.plot(self.df_hourpass_R, self.df_LT_R, label=self.df_legend_R[-15:], picker=float(set_dic['picker_line']), linewidth=float(set_dic['thick_line']))
                if self.df_LT_R.min()[5] < float(set_dic['import_MinLT']) or not str(self.df_LT_R.min()[5]).isdigit():  # 설정값보다 더 작은 값이 있다면
                    self.LT_min_val = float(set_dic['import_MinLT'])
                    self.flag_LT_min = 1

                self.leg = self.ax.legend(ncol=2, prop={'size': 7})  # 범례
                self.ax.set_ylim(top=101)

            elif k == 1:
                if flag_plot_delv['delV'] == False:
                    self.temp_l, = self.ax.plot(self.df_hourpass_R, self.df_V_R, label='_nolegend_', picker = float(set_dic['picker_line']), linewidth=float(set_dic['thick_line']))  # 범례 생략
                    self.dic_rawline_dfV[self.temp_l] = self.df_V_R
                if flag_plot_delv['delV'] == True:
                    self.temp_l, = self.ax.plot(self.df_hourpass_R, self.df_delV_R, label='_nolegend_', picker = float(set_dic['picker_line']), linewidth=float(set_dic['thick_line']))  # 범례 생략
                    self.dic_plotline_dfdelV[self.temp_l] = self.df_delV_R

            #merge
            self.dic_line_dfhourpassraw[self.temp_l] = self.dic_fig_ax_dfhourpassraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dfhourpassplot[self.temp_l] = self.dic_fig_ax_dfhourpassplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dfLTraw[self.temp_l] = self.dic_fig_ax_dfLTraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dfLTplot[self.temp_l] = self.dic_fig_ax_dfLTplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dfVraw[self.temp_l] = self.dic_fig_ax_dfVraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dfVplot[self.temp_l] = self.dic_fig_ax_dfVplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dfdelVraw[self.temp_l] = self.dic_fig_ax_dfdelVraw[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dfdelVplot[self.temp_l] = self.dic_fig_ax_dfdelVplot[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]
            self.dic_line_dflegend[self.temp_l] = self.dic_fig_ax_dflegend[self.list_fig[self.idx_fig]][self.list_ax[self.idx_ax]][m]

            plt.gca().set_xlim(left=0, right=self.hourpass_max_val * float(set_dic['plot_time_ratio']))  # x축 최소값 0으로 지정

            if self.flag_LT_min == 1:
                #self.list_ax[self.idx_ax].set_ylim(bottom = self.LT_min_val)
                plt.gca().set_ylim(bottom = self.LT_min_val)

            temp_picker_lines.append(self.temp_l)

        self.dic_ax_line[self.list_ax[self.idx_ax]] = temp_picker_lines
        self.dic_fig_ax_line[self.list_fig[self.idx_fig]] = self.dic_ax_line

        plt.gca().grid(True, axis='y', alpha=0.5)  # y축 grid 설정
        plt.title(self.lot_name, fontsize = float(set_dic['title_font_size']))

        self.picker_lines.append(temp_picker_lines)

        #수명그래프에만 범례 표시하고 범례 선택할 수 있도록 한다.
        if k == 0 :
            self.on_press_temp = []
            self.on_press_legend_temp = []
            for legline, origline in zip(self.leg.get_lines(), self.picker_lines[LT_index * 2]):
                legline.set_picker(float(set_dic['picker_legend']))
                self.lined[legline] = origline              #범레 - 수명
                self.plotlined[origline] = legline          #수명 - 범례
                self.on_press_temp.append(origline)
                self.on_press_legend_temp.append(legline)
            self.on_press_legend[LT_index] = self.on_press_legend_temp

        elif k == 1:
            for legline, origline_V in zip(self.leg.get_lines(), self.picker_lines[LT_index * 2 + 1]):
                self.lined_V[legline] = origline_V          #범례 - 전압
                self.lined_V_torig[origline_V] = legline    #전압 - 범례
                self.on_press_temp.append(origline_V)

            for origline, origline_V in zip(self.picker_lines[LT_index *2], self.picker_lines[LT_index * 2 + 1]):
                self.plotlined_V[origline] = origline_V     #수명 - 전압
                self.plotlined_V_torig[origline_V] = origline #전압 - 수명
        self.on_press_line[LT_index] = self.on_press_temp  # on_press용 인덱스 - 라인 딕셔너리

        self.dic_fig_leg_LT[self.list_fig[self.idx_fig]] = self.lined
        self.dic_fig_leg_V[self.list_fig[self.idx_fig]] = self.lined_V
        self.dic_fig_LT_leg[self.list_fig[self.idx_fig]] = self.plotlined
        self.dic_fig_LT_V[self.list_fig[self.idx_fig]] = self.plotlined_V
        self.dic_fig_V_LT[self.list_fig[self.idx_fig]] = self.plotlined_V_torig
        self.dic_fig_V_leg[self.list_fig[self.idx_fig]] = self.lined_V_torig

        self.dic_fig_on_press_line[self.list_fig[self.idx_fig]] = self.on_press_line
        self.dic_fig_on_press_legend[self.list_fig[self.idx_fig]] = self.on_press_legend


    def draw_LT_V_graph_m(self, LT_index, k):
        #전압 선택
        if k == 1 and self.chk_V.isChecked() == False:
            k = 2

        #수명 그릴 때 / 전압 그릴 때로 나누어서
        temp_picker_lines = []
        #수명 셀 반복
        for m in range(len(self.dic_fig_visibleLT[self.list_fig[self.idx_fig]])):
            self.flag_LT_min = 0
            self.df_hourpass_R = self.dic_fig_dfhourpassraw[self.list_fig[self.idx_fig]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_dfhourpassplot[self.list_fig[self.idx_fig]][m]
            self.df_LT_R = self.dic_fig_dfLTraw[self.list_fig[self.idx_fig]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_dfLTplot[self.list_fig[self.idx_fig]][m]
            self.df_legend_R = self.dic_fig_dflegend[self.list_fig[self.idx_fig]][m]
            if flag_plot_delv['delV'] == False:
                self.df_V_R = self.dic_fig_dfVraw[self.list_fig[self.idx_fig]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_dfVplot[self.list_fig[self.idx_fig]][m]
            else:
                self.df_delV_R = self.dic_fig_dfdelVraw[self.list_fig[self.idx_fig]][m] if flag_plot_delv['plotMax'] == False else self.dic_fig_dfdelVplot[self.list_fig[self.idx_fig]][m]


            if k == 0 :

                if flag_plot_delv['plotMax'] == False:

                    if m == 0: self.hourpass_max_val = self.df_hourpass_R.max()[0]
                    if self.hourpass_max_val < self.df_hourpass_R.max()[0]: self.hourpass_max_val = self.df_hourpass_R.max()[0]

                self.temp_l, = self.ax.plot(self.df_hourpass_R, self.df_LT_R, label=self.df_legend_R[-15:], picker = float(set_dic['picker_line']), linewidth=float(set_dic['thick_line']))
                if self.df_LT_R.min()[5] < float(set_dic['import_MinLT']) or not str(self.df_LT_R.min()[5]).isdigit():  # 설정값보다 더 작은 값이 있다면
                    self.LT_min_val = float(set_dic['import_MinLT'])
                    self.flag_LT_min = 1

                self.leg = self.ax.legend(ncol=2, prop={'size': 7})  # 범례
                self.ax.set_ylim(top=101)

            elif k == 1:
                if flag_plot_delv['delV'] == False:
                    self.temp_l, = self.ax.plot(self.df_hourpass_R, self.df_V_R, label='_nolegend_', picker = float(set_dic['picker_line']), linewidth=float(set_dic['thick_line']))  # 범례 생략
                    self.dic_rawline_dfV[self.temp_l] = self.df_V_R
                if flag_plot_delv['delV'] == True:
                    self.temp_l, = self.ax.plot(self.df_hourpass_R, self.df_delV_R, label='_nolegend_', picker = float(set_dic['picker_line']), linewidth=float(set_dic['thick_line']))  # 범례 생략
                    self.dic_plotline_dfdelV[self.temp_l] = self.df_delV_R

            plt.gca().set_xlim(left=0, right=self.hourpass_max_val * float(set_dic['plot_time_ratio']))  # x축 최소값 0으로 지정

            if self.flag_LT_min == 1:
                plt.gca().set_ylim(bottom = self.LT_min_val)

            temp_picker_lines.append(self.temp_l)

        plt.gca().grid(True, axis='y', alpha=0.5)  # y축 grid 설정
        plt.title('Merge Graph / PlotMax, DelV Unable', fontsize = float(set_dic['title_font_size']))

        self.picker_lines.append(temp_picker_lines)

        #수명그래프에만 범례 표시하고 범례 선택할 수 있도록 한다.
        if k == 0 :
            self.on_press_temp = []
            self.on_press_legend_temp = []
            for legline, origline in zip(self.leg.get_lines(), self.picker_lines[LT_index * 2]):
                legline.set_picker(float(set_dic['picker_legend']))
                self.lined[legline] = origline              #범레 - 수명
                self.plotlined[origline] = legline          #수명 - 범례
                self.on_press_temp.append(origline)
                self.on_press_legend_temp.append(legline)
            self.on_press_legend[LT_index] = self.on_press_legend_temp

        elif k == 1:
            for legline, origline_V in zip(self.leg.get_lines(), self.picker_lines[LT_index * 2 + 1]):
                self.lined_V[legline] = origline_V          #범례 - 전압
                self.lined_V_torig[origline_V] = legline    #전압 - 범례
                self.on_press_temp.append(origline_V)

            for origline, origline_V in zip(self.picker_lines[LT_index *2], self.picker_lines[LT_index * 2 + 1]):
                self.plotlined_V[origline] = origline_V     #수명 - 전압
                self.plotlined_V_torig[origline_V] = origline #전압 - 수명
        self.on_press_line[LT_index] = self.on_press_temp  # on_press용 인덱스 - 라인 딕셔너리

        self.dic_fig_leg_LT[self.list_fig[self.idx_fig]] = self.lined
        self.dic_fig_leg_V[self.list_fig[self.idx_fig]] = self.lined_V
        self.dic_fig_LT_leg[self.list_fig[self.idx_fig]] = self.plotlined
        self.dic_fig_LT_V[self.list_fig[self.idx_fig]] = self.plotlined_V
        self.dic_fig_V_LT[self.list_fig[self.idx_fig]] = self.plotlined_V_torig
        self.dic_fig_V_leg[self.list_fig[self.idx_fig]] = self.lined_V_torig

        self.dic_fig_on_press_line[self.list_fig[self.idx_fig]] = self.on_press_line
        self.dic_fig_on_press_legend[self.list_fig[self.idx_fig]] = self.on_press_legend


######################################################Plot Event########################################################
########################################################################################################################
########################################################################################################################
    def mouse_click(self, event):

        if not event.inaxes:
            return
        #right click
        if event.button == 3:
            self.ax = self.dic_fig_ax[self.list_fig[plt.gcf().number - 1]][self.find_ax_list(str(event))]
            self.xs.append(event.xdata)
            self.ys.append(event.ydata)
            #add a line to plot if it has 2 points
            if len(self.xs) % 2 == 0:
                line, = self.ax.plot([self.xs[-2], self.xs[-1]], [self.ys[-2], self.ys[-1]], 'r')
                line.figure.canvas.draw()
                #line.self.list_fig[plt.gcf().number-1].canvas.draw()

        #middle click
        if event.button == 2:
            self.ax = self.dic_fig_ax[self.list_fig[plt.gcf().number - 1]][self.find_ax_list(str(event))]
            if len(self.xs) > 0:
                self.xs.pop()
                self.ys.pop()
            #delete last line drawn if the line is missing a point,
            #never delete the original stock plot
            if len(self.xs) % 2 == 1 and len(self.ax.lines) > 1:
                self.ax.lines.pop()
            #refresh plot
            self.list_fig[plt.gcf().number-1].canvas.draw()

    def mouse_move(self, event):

        if not event.inaxes:
            return
        #dtaw a temporary line from a single point to the mouse position
        #delete the temporary line when mouse move to another position
        if len(self.xs) % 2 == 1:
            line, =self.ax.plot([self.xs[-1], event.xdata], [self.ys[-1], event.ydata], 'r')

            line.figure.canvas.draw()
            #line.self.list_fig[plt.gcf().number-1].canvas.draw()
            self.ax.lines.pop()

    #라인 또는 범례 라인 클릭했을 때 visible 처리
    def on_pick(self, event):

        #전압 포함 안되는 경우는 오류로 예외처리
        if str(event.mouseevent.button) == 'MouseButton.LEFT':
            firline = event.artist

            #########################범례에서 라인
            if not '_nolegend_' in str(event.artist):
                try:
                    #범례 - 수명
                    #secline = self.lined[firline]
                    secline = self.dic_fig_leg_LT[self.list_fig[plt.gcf().number - 1]][firline]
                    visible = not secline.get_visible()
                    secline.set_visible(visible)
                    firline.set_alpha(1.0 if visible else 0.01)

                    #범례 - 전압
                    try:
                        #secline_V = self.lined_V[firline]
                        secline_V = self.dic_fig_leg_V[self.list_fig[plt.gcf().number - 1]][firline]
                        visible_V = not secline_V.get_visible()
                        secline_V.set_visible(visible_V)
                    except:
                        pass

                ####################라인에서 범례
                except:
                    #수명 - 범례
                    #secline = self.plotlined[firline]
                    secline = self.dic_fig_LT_leg[self.list_fig[plt.gcf().number - 1]][firline]
                    visible = not firline.get_visible()
                    firline.set_visible(False)

                    #수명 - 전압
                    try:
                        #firline_V = self.plotlined_V[firline]
                        firline_V = self.dic_fig_LT_V[self.list_fig[plt.gcf().number - 1]][firline]
                        #visible_V = not firline_V.get_visible()
                        firline_V.set_visible(False)
                    except:
                        pass

                    secline.set_alpha(0.01)
            ############전압에서 라인
            elif '_nolegend_' in str(event.artist):             #1. 전압 / 2. 수명 / 3. 범례
                visible = not firline.get_visible()             # 전압 라인
                firline.set_visible(False)
                #secline = self.plotlined_V_torig[firline]       #수명 라인
                secline = self.dic_fig_V_LT[self.list_fig[plt.gcf().number - 1]][firline]
                secline.set_visible(False)
                #thirdline = self.lined_V_torig[firline]         # 전압 - 범례
                thirdline = self.dic_fig_V_leg[self.list_fig[plt.gcf().number - 1]][firline]
                thirdline.set_alpha(1.0 if visible else 0.01)

            self.list_fig[plt.gcf().number - 1].canvas.draw()

    #숫자 단축키 눌렀을 때 그래프 전체 보이기
    def on_press(self, event):

        #라인 다보이게 하기
        if event.key.isdigit():

            #라인
            for origline in self.dic_fig_on_press_line[self.list_fig[plt.gcf().number-1]][int(event.key)-1]:
                origline.set_visible(True)

            for legline in self.dic_fig_on_press_legend[self.list_fig[plt.gcf().number-1]][int(event.key)-1]:
                legline.set_alpha(1)
        
        #라인 다 안보이게 하기
        if 'ctrl' in event.key and isNumber(event.key[-1]):

            for origline in self.dic_fig_on_press_line[self.list_fig[plt.gcf().number-1]][int(event.key[-1])-1]:
                origline.set_visible(False)

            for legline in self.dic_fig_on_press_legend[self.list_fig[plt.gcf().number-1]][int(event.key[-1])-1]:
                legline.set_alpha(0.01)

        #델타브이
        if event.key.upper() == set_dic['run_delV'].upper():
            if flag_plot_delv['merge'] == True:
                QMessageBox.warning(self, "Merge Interlock", "Merge 실행 후 DelV 불가")
                return
            flag_plot_delv['delV'] = not flag_plot_delv['delV']
            flag_plot_delv['delV_btn'] = True
            self.idx_fig = plt.gcf().number - 1
            #plt.close()
            self.plotLT(self.lot_final_list)

        #plotMax
        if event.key.upper() == set_dic['run_plotMax'].upper():
            if flag_plot_delv['merge'] == True:
                QMessageBox.warning(self, "QMessageBox", "Merge 실행 후 PlotMax 불가")
                return
            flag_plot_delv['plotMax'] = not flag_plot_delv['plotMax']
            flag_plot_delv['plotMax_btn'] = True
            self.idx_fig = plt.gcf().number - 1
            #plt.close()
            self.plotLT(self.lot_final_list)

        #merge
        if event.key.upper() == 'M':
            self.m_flag = 0
            flag_plot_delv['merge'] = not flag_plot_delv['merge']
            temp_idx = plt.gcf().number-1

            self.visibleLT = []
            self.visibleV = []
            self.dic_fig_visibleLT = {}
            self.dic_fig_visibleV = {}

            #self.dic_fig
            #a: list_ax

            self.fig = plt.figure(figsize=(float(set_dic['fig_width']), float(set_dic['fig_length'])))
            self.fig.set_facecolor('white')
            self.idx_fig = plt.gcf().number - 1
            self.list_fig.append(self.fig)

            aa = 0
            for a in self.dic_fig_ax_line[self.list_fig[temp_idx]]:

                for b in self.dic_ax_line[a]:
                    if b.get_visible() and self.flag_V == True:
                        if aa % 2 == 0:         #수명 그래프일때
                            self.visibleLT.append(b)
                        else:                   #전압일때
                            self.visibleV.append(b)
                aa += 1

            self.dic_fig_visibleLT[self.list_fig[self.idx_fig]] = self.visibleLT
            self.dic_fig_visibleV[self.list_fig[self.idx_fig]] = self.visibleV

            #merge 데이터프레임 추출
            #c : visible line / fig - line - dfhourpass
            if flag_plot_delv['plotMax'] == False:
                self.temp_list = []
                for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                    self.temp_list.append(self.dic_fig_line_dfhourpassraw[self.list_fig[temp_idx]][c])
                self.dic_fig_dfhourpassraw[self.list_fig[self.idx_fig]] = self.temp_list

                self.temp_list = []
                for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                    self.temp_list.append(self.dic_fig_line_dfLTraw[self.list_fig[temp_idx]][c])
                self.dic_fig_dfLTraw[self.list_fig[self.idx_fig]] = self.temp_list

                if flag_plot_delv['delV'] == False:
                    self.temp_list = []
                    for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                        self.temp_list.append(self.dic_fig_line_dfVraw[self.list_fig[temp_idx]][c])
                    self.dic_fig_dfVraw[self.list_fig[self.idx_fig]] = self.temp_list
                else:
                    self.temp_list = []
                    for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                        self.temp_list.append(self.dic_fig_line_dfdelVraw[self.list_fig[temp_idx]][c])
                    self.dic_fig_dfdelVraw[self.list_fig[self.idx_fig]] = self.temp_list

            else:
                self.temp_list = []
                for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                    self.temp_list.append(self.dic_fig_line_dfhourpassplot[self.list_fig[temp_idx]][c])
                self.dic_fig_dfhourpassplot[self.list_fig[self.idx_fig]] = self.temp_list

                self.temp_list = []
                for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                    self.temp_list.append(self.dic_fig_line_dfLTplot[self.list_fig[temp_idx]][c])
                self.dic_fig_dfLTplot[self.list_fig[self.idx_fig]] = self.temp_list

                if flag_plot_delv['delV'] == False:
                    self.temp_list = []
                    for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                        self.temp_list.append(self.dic_fig_line_dfVplot[self.list_fig[temp_idx]][c])
                    self.dic_fig_dfVplot[self.list_fig[self.idx_fig]] = self.temp_list
                else:
                    self.temp_list = []
                    for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                        self.temp_list.append(self.dic_fig_line_dfdelVplot[self.list_fig[temp_idx]][c])
                    self.dic_fig_dfdelVplot[self.list_fig[self.idx_fig]] = self.temp_list

            self.temp_list = []
            for c in self.dic_fig_visibleLT[self.list_fig[self.idx_fig]]:
                self.temp_list.append(self.dic_fig_line_dflegend[self.list_fig[temp_idx]][c])
            self.dic_fig_dflegend[self.list_fig[self.idx_fig]] = self.temp_list

            self.plotLT(self.lot_final_list)

        self.list_fig[plt.gcf().number-1].canvas.draw()

###############################################Plot Event 여기까지########################################################
########################################################################################################################
########################################################################################################################

    def find_ax_list(self,e_str):

        if '(0.125,0.11;0.775x0.77)' in e_str : return 0      #1
        if '(0.125,0.11;0.352273x0.77)' in e_str: return 0    #2
        if '(0.125,0.11;0.227941x0.77)' in e_str: return 0    #3
        if '(0.125,0.11;0.168478x0.77)' in e_str: return 0    #4
        if '(0.125,0.11;0.133621x0.77)' in e_str: return 0    #5
        if '(0.125,0.11;0.110714x0.77)' in e_str: return 0    #6
        if '(0.125,0.355;0.775x0.525)' in e_str: return 0     #7
        if '(0.125,0.11;0.775x0.175)' in e_str: return 1     #8
        if '(0.125,0.355;0.352273x0.525)' in e_str: return 0  #9
        if '(0.125,0.11;0.352273x0.175)' in e_str: return 1   #10
        if '(0.125,0.355;0.227941x0.525)' in e_str: return 0  #11
        if '(0.125,0.11;0.227941x0.175)' in e_str: return 1   #12
        if '(0.125,0.355;0.168478x0.525)' in e_str: return 0  #13
        if '(0.125,0.11;0.168478x0.175)' in e_str: return 1   #14
        if '(0.125,0.355;0.133621x0.525)' in e_str: return 0  #15
        if '(0.125,0.11;0.133621x0.175)' in e_str: return 1   #16
        if '(0.125,0.355;0.110714x0.525)' in e_str: return 0  #17
        if '(0.125,0.11;0.110714x0.175)' in e_str: return 1   #18

        if '(0.547727,0.11;0.352273x0.77)' in e_str: return 1    #1
        if '(0.398529,0.11;0.227941x0.77)' in e_str: return 1     #2
        if '(0.327174,0.11;0.168478x0.77)' in e_str: return 1     #3
        if '(0.285345,0.11;0.133621x0.77)' in e_str: return 1     #4
        if '(0.257857,0.11;0.110714x0.77)' in e_str: return 1     #5
        if '(0.547727,0.355;0.352273x0.525)' in e_str: return 2   #6
        if '(0.547727,0.11;0.352273x0.175)' in e_str: return 3    #7
        if '(0.398529,0.355;0.227941x0.525)' in e_str: return 2   #8
        if '(0.398529,0.11;0.227941x0.175)' in e_str: return 3    #9
        if '(0.327174,0.355;0.168478x0.525)' in e_str: return 2   #10
        if '(0.327174,0.11;0.168478x0.175)' in e_str: return 3    #11
        if '(0.285345,0.355;0.133621x0.525)' in e_str: return 2   #12
        if '(0.285345,0.11;0.133621x0.175)' in e_str: return 3    #13
        if '(0.257857,0.355;0.110714x0.525)' in e_str: return 2   #14
        if '(0.257857,0.11;0.110714x0.175)' in e_str: return 3    #15

        if '(0.672059,0.11;0.227941x0.77)' in e_str: return 2     #1
        if '(0.529348,0.11;0.168478x0.77)' in e_str: return 2     #2
        if '(0.44569,0.11;0.133621x0.77)' in e_str: return 2      #3
        if '(0.390714,0.11;0.110714x0.77)' in e_str: return 2     #4
        if '(0.672059,0.355;0.227941x0.525)' in e_str: return 4   #5
        if '(0.672059,0.11;0.227941x0.175)' in e_str: return 5    #6
        if '(0.529348,0.355;0.168478x0.525)' in e_str: return 4   #7
        if '(0.529348,0.11;0.168478x0.175)' in e_str: return 5    #8
        if '(0.44569,0.355;0.133621x0.525)' in e_str: return 4    #9
        if '(0.44569,0.11;0.133621x0.175)' in e_str: return 5     #10
        if '(0.390714,0.355;0.110714x0.525)' in e_str: return 4   #11
        if '(0.390714,0.11;0.110714x0.175)' in e_str: return 5    #12

        if '(0.731522,0.11;0.168478x0.77)' in e_str: return 3     #1
        if '(0.606034,0.11;0.133621x0.77)' in e_str: return 3     #2
        if '(0.523571,0.11;0.110714x0.77)' in e_str: return 3     #3
        if '(0.731522,0.355;0.168478x0.525)' in e_str: return 6   #4
        if '(0.731522,0.11;0.168478x0.175)' in e_str: return 7    #5
        if '(0.606034,0.355;0.133621x0.525)' in e_str: return 6   #6
        if '(0.606034,0.11;0.133621x0.175)' in e_str: return 7    #7
        if '(0.523571,0.355;0.110714x0.525)' in e_str: return 6   #8
        if '(0.523571,0.11;0.110714x0.175)' in e_str: return 7    #9

        if '(0.766379,0.11;0.133621x0.77)' in e_str: return 4     #1
        if '(0.656429,0.11;0.110714x0.77)' in e_str: return 4     #2
        if '(0.766379,0.355;0.133621x0.525)' in e_str: return 8   #3
        if '(0.766379,0.11;0.133621x0.175)' in e_str: return 9    #4
        if '(0.656429,0.355;0.110714x0.525)' in e_str: return 8   #5
        if '(0.656429,0.11;0.110714x0.175)' in e_str: return 9    #6

        if '(0.789286,0.11;0.110714x0.77)' in e_str: return 5
        if '(0.789286,0.355;0.110714x0.525)' in e_str: return 10
        if '(0.789286,0.11;0.110714x0.175)' in e_str: return 11

    #LT_Table Load
    def load_LT_table(self):
        global lot_f_list
        global dic_Lot_row

        lot_f_list = []
        dic_Lot_row = {}

        flag_plot_delv['LT_table_btn'] = True
        flag_plot_delv['path_find'] = 0
        self.not_find_path = []

        ################################################경로 찾기
        for i in range(self.Lot_list.count()):
            self.Lot_name_t = self.Lot_list.item(i).text()[:7]
            self.Lot_year_t = '20' + self.Lot_name_t[:2]
            self.Lot_month_t = self.Lot_name_t[2:4]
            p_flag = 0

            # 수명 호기 접근
            for life_eqp_path in df_life_path['Path']:
                # Lot 년도
                y_flag = 0
                for life_year in arr_path(life_eqp_path):
                    if self.Lot_year_t in life_year:
                        self.life_path = life_eqp_path + '\\' + life_year + '\\'
                        y_flag = 1
                        break
                # Lot 월
                m_flag = 0
                if self.Lot_month_t[0] == '1' and y_flag == 1:
                    for life_month in arr_path(self.life_path):
                        if self.Lot_month_t in life_month:
                            self.life_path = self.life_path + life_month + '\\'
                            m_flag = 1
                            break
                elif self.Lot_month_t[0] == '0' and y_flag == 1:
                    for life_month in arr_path(self.life_path):
                        if self.Lot_month_t[-1] in life_month and self.Lot_month_t[0] == '0':
                            self.life_path = self.life_path + life_month + '\\'
                            m_flag = 1
                            break
                # 증착호기
                d_flag = 0
                if '1호기' in self.basic_list_arr[0].currentItem().text() and m_flag == 1:
                    self.life_path = self.life_path + '증착1호기' + '\\'
                    d_flag = 1
                elif '2호기' in self.basic_list_arr[0].currentItem().text() and m_flag == 1:
                    self.life_path = self.life_path + '증착2호기' + '\\'
                    d_flag = 1
                # Lot
                for life_lot in arr_path(self.life_path):
                    if self.Lot_name_t in life_lot and d_flag == 1:
                        self.life_path = self.life_path + life_lot + '\\'
                        lot_f_list.append(self.life_path)
                        flag_plot_delv['path_find'] += 1
                        p_flag = 1
                        break

            if p_flag == 0:
                self.not_find_path.append(self.Lot_name_t)

            dic_Lot_row[i] = len(os.listdir(lot_f_list[i]))

        total_not_find_str = ""
        if flag_plot_delv['path_find'] != self.Lot_list.count():
            for i in range(len(self.not_find_path)):
                if i == len(self.not_find_path) - 1:
                    total_not_find_str = total_not_find_str + self.not_find_path[i]
                else:
                    total_not_find_str = total_not_find_str + self.not_find_path[i] + ', '
            QMessageBox.warning(self, "Path Interlock", "수명 경로를 찾을 수 없습니다.\n" + total_not_find_str)
            return

        self.dlg_LT_table = LT_table_dialog()
        self.dlg_LT_table.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dlg_LT_table.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.dlg_LT_table.exec_()

    #설정 버튼
    def set_up(self):
        self.dlg = Setdialog()
        self.dlg.exec_()

class LT_table_dialog(QDialog):
    def __init__(self):

        super().__init__()
        global set_dic
        global lot_f_list
        global dic_Lot_row

        self.setupUi(self)              #1. Lot_list[], 2. dic_Lot_row,

    #ui파일에서 가져옴
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1056, 400 * len(lot_f_list))        #dialog 전체 size
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1032, 350 * len(lot_f_list)))          #수명테이블 사이즈 결정
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame.setMinimumSize(QtCore.QSize(0, 350 * len(lot_f_list)))                                   #스크롤 최소 사이즈
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setContentsMargins(10, 10, 10, 30)
        self.gridLayout_2.setSpacing(20)
        self.gridLayout_2.setObjectName("gridLayout_2")

        #addWidget (self, QWidget, row, column, rowSpan, columnSpan, Qt.Alignment alignment = 0)
        ##########################################################객체
        #Lot1
        for i in range(len(lot_f_list)):

            self.line_Lot1 = QtWidgets.QLineEdit(self.frame)
            self.line_Lot1.setObjectName("line_Lot1")
            self.gridLayout_2.addWidget(self.line_Lot1, i*2, 0, 1, 1)

            ############################################################table1 front 코드
            self.table1_Lot1 = QtWidgets.QTableWidget(self.frame)
            self.table1_Lot1.setObjectName("table1_Lot1")
            self.table1_Lot1.setColumnCount(10)
            self.table1_Lot1.setRowCount(25)
            self.table1_Lot1.horizontalHeader().setVisible(True)
            self.table1_Lot1.verticalHeader().setVisible(False)
            self.table1_Lot1.setHorizontalHeaderLabels(('TL', '파일명', 'Max(%)', 'Max(h)', '99%', '98%', '95%', '90%', '파일위치', 'mA'))
            self.table1_Lot1.horizontalHeader().setFrameStyle(QFrame.Box)
            self.table1_Lot1.horizontalHeader().setLineWidth(1)
            self.table1_Lot1.horizontalHeader().setFont(QtGui.QFont('맑은 고딕', 7))
            self.table1_Lot1.horizontalHeader().setMinimumSectionSize(3)

            #self.table1_Lot1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)           #열너비 자동조절
            self.table1_Lot1.setColumnWidth(0, 28)
            self.table1_Lot1.setColumnWidth(1, 220)
            self.table1_Lot1.setColumnWidth(2, 50)
            self.table1_Lot1.setColumnWidth(3, 50)
            self.table1_Lot1.setColumnWidth(4, 40)
            self.table1_Lot1.setColumnWidth(5, 40)
            self.table1_Lot1.setColumnWidth(6, 40)
            self.table1_Lot1.setColumnWidth(7, 40)
            self.table1_Lot1.setColumnWidth(8, 155)
            self.table1_Lot1.setColumnWidth(9, 50)
            self.table1_Lot1.horizontalHeader().setStretchLastSection(True)

            self.table1_Lot1.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table1_Lot1.verticalHeader().setMinimumSectionSize(5)
            self.table1_Lot1.setFont(QtGui.QFont('맑은 고딕', 7))
            item = QTableWidgetItem()
            item.setText('test')
            item.setTextAlignment(Qt.AlignCenter)
            self.table1_Lot1.setItem(1,1,item)
            self.gridLayout_2.addWidget(self.table1_Lot1, i * 2 + 1, 0, 1, 1)
            ###############################################################

            self.table2_Lot1 = QtWidgets.QTableWidget(self.frame)
            self.table2_Lot1.setObjectName("table2_Lot1")
            self.table2_Lot1.setColumnCount(0)
            self.table2_Lot1.setRowCount(0)
            self.gridLayout_2.addWidget(self.table2_Lot1, i * 2 + 1, 1, 1, 1)

            self.verticalLayout.addWidget(self.frame)
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
            self.gridLayout_2.setColumnStretch(0, 3)
            self.gridLayout_2.setColumnStretch(1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))


class Setdialog(QDialog, form_class_set):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        global set_dic

        self.text_picker_line.setText(set_dic['picker_line'])
        self.text_picker_legend.setText(set_dic['picker_legend'])
        self.text_thick_line.setText(set_dic['thick_line'])
        self.text_import_MinLT.setText(set_dic['import_MinLT'])
        self.text_title_font_size.setText(set_dic['title_font_size'])
        self.text_run_plotMax.setText(set_dic['run_plotMax'])
        self.text_run_delV.setText(set_dic['run_delV'])
        self.text_plot_time_ratio.setText(set_dic['plot_time_ratio'])
        self.text_fig_width.setText(set_dic['fig_width'])
        self.text_fig_length.setText(set_dic['fig_length'])

        #버튼 정의
        self.push_apply.clicked.connect(self.qd_push_apply)
        self.push_save_default.clicked.connect(self.qd_push_save_default)
        self.push_cancel.clicked.connect(self.qd_push_cancel)

    def qd_push_apply(self):
        set_dic['picker_line'] = self.text_picker_line.text()
        set_dic['picker_legend'] = self.text_picker_legend.text()
        set_dic['thick_line'] = self.text_thick_line.text()
        set_dic['import_MinLT'] = self.text_import_MinLT.text()
        set_dic['title_font_size'] = self.text_title_font_size.text()
        set_dic['run_plotMax'] = self.text_run_plotMax.text()
        set_dic['run_delV'] = self.text_run_delV.text()
        set_dic['plot_time_ratio'] = self.text_plot_time_ratio.text()
        set_dic['fig_width'] = self.text_fig_width.text()
        set_dic['fig_length'] = self.text_fig_length.text()
        self.close()

    def qd_push_save_default(self):
        set_dic['picker_line'] = self.text_picker_line.text()
        set_dic['picker_legend'] = self.text_picker_legend.text()
        set_dic['thick_line'] = self.text_thick_line.text()
        set_dic['import_MinLT'] = self.text_import_MinLT.text()
        set_dic['title_font_size'] = self.text_title_font_size.text()
        set_dic['run_plotMax'] = self.text_run_plotMax.text()
        set_dic['run_delV'] = self.text_run_delV.text()
        set_dic['plot_time_ratio'] = self.text_plot_time_ratio.text()
        set_dic['fig_width'] = self.text_fig_width.text()
        set_dic['fig_length'] = self.text_fig_length.text()
        with open('Setting.txt','w',newline='') as f:
            writer = csv.writer(f)
            for k, v in set_dic.items():
                writer.writerow([k,v])
        self.close()

    def qd_push_cancel(self):
        self.close()

if __name__ == "__main__" :                     #현재 창에서 실행되는지, 모듈에서 실행되는지
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()
    #프로그램 화면을 보여주는 코드
    myWindow.show()
    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()