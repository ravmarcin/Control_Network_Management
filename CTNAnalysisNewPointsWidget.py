from PyQt5 import QtWidgets
from CTNdb import *
from CTNInitWidget import *
from collections import Counter
import json
import time
import sys
ctn_db = CTNdb()

""" Widget to show the new points from analysis of residuals """


class CTNAnalysisNewPointsWidget(QtWidgets.QWidget):
    """ Constructor """

    def __init__(self):
        super().__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.table = QtWidgets.QTableWidget()
        self.current_line = QtWidgets.QLineEdit()
        self.grid.addWidget(self.current_line, 1, 1, 1, 6)
        self.file_line = QtWidgets.QLineEdit()
        current_file_proj = ctn_db.current_file_proj
        self.new_tp = ctn_db.new_tp
        self.file_name = ''
        self.point_list = []
        self.id_list = []
        self.project_open = False
        with open(current_file_proj) as f:
            data_ = json.load(f)
        self.project_name = data_['project'][0]['project_name']
        self.revision_name = data_['project'][0]['project_revision']
        if len(self.project_name) > 0:
            self.project_open = True
        if self.project_open:
            text_ = 'You are in project: ' + self.project_name + '; revision: ' + self.revision_name
            self.current_line.setText(text_)
            self.analysis_new_p_view()
        else:
            text_ = 'No any project is open'
            self.current_line.setText(text_)
        self.setLayout(self.grid)
        self.show()

    """ Widget view """

    def analysis_new_p_view(self):
        table_info = ctn_db.read_col_db(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names = [col_[1] for col_ in table_info]
        rows_ = ctn_db.read_table_db(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.table.setRowCount(len(rows_))
        self.table.setColumnCount(len(col_names))
        self.table.setHorizontalHeaderLabels(col_names)
        for i in range(len(rows_)):
            for j in range(len(col_names)):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(rows_[i][j])))
                if col_names[j] == 'name':
                    self.point_list.append(str(rows_[i][j]))
                    self.id_list.append(str(rows_[i][j-1]))
        btn_save = QtWidgets.QPushButton('Save')
        btn_save.clicked.connect(self.save_file)
        btn_check = QtWidgets.QPushButton('Check repeat')
        btn_check.clicked.connect(self.check_repeat)
        btn_delete = QtWidgets.QPushButton('Delete')
        btn_delete.clicked.connect(self.delete_one_point)
        btn_delete_rep = QtWidgets.QPushButton('Delete repeat')
        btn_delete_rep.clicked.connect(self.delete_repeated_points)
        btn_delete_all = QtWidgets.QPushButton('Delete all')
        btn_delete_all.clicked.connect(self.delete_all)
        self.grid.addWidget(btn_save, 1, 9, 1, 1)
        self.grid.addWidget(self.file_line, 2, 1, 1, 6)
        self.grid.addWidget(btn_check, 1, 8, 1, 1)
        self.grid.addWidget(btn_delete, 2, 7, 1, 1)
        self.grid.addWidget(btn_delete_rep, 2, 8, 1, 1)
        self.grid.addWidget(btn_delete_all, 2, 9, 1, 1)
        self.grid.addWidget(self.table, 3, 1, 6, 9)
        self.setLayout(self.grid)
        self.show()

    """ Save the file to the database """

    def save_file(self):
        if len(self.file_name) > 0:
            ctn_db.save_to_project(proj_name=self.project_name, proj_revision=self.revision_name, type_=self.new_tp)
            text_ = 'The changes are saved to the project: ' + self.project_name + '; rev: ' + self.revision_name
            self.current_line.setText(text_)
        else:
            text_ = "No any project is open!\n"
            self.current_line.setText(text_)
        self.analysis_new_p_view()

    """ Find repeated points """

    def check_repeat(self):
        repeat_ = dict(Counter(self.point_list))
        repeat_list = []
        for i in repeat_:
            if repeat_[i] > 1:
                repeat_list.append(i)
        repeat_str = ''
        for i in repeat_list:
            repeat_str = repeat_str + '; ' + i
        count_ = len(repeat_list)
        window_ = QtWidgets.QMessageBox()
        window_.setWindowTitle('Repeated points')
        window_.setText('Number of repeated points: %s' % str(count_))
        window_.setDetailedText(repeat_str)
        window_.setGeometry(400, 400, 600, 400)
        window_.exec_()

    """ Delete repeated points """

    def delete_repeated_points(self):
        text_types = ('Yes', 'No')
        text_sel, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Yes or No', text_types, 0, False)
        if ok_pressed and text_sel == 'Yes':
            repeat_ = dict(Counter(self.point_list))
            repeat_list = []
            for i in repeat_:
                if repeat_[i] > 1:
                    repeat_list.append(i)
            id_del = []
            for i in range(len(repeat_list)):
                for j in range(len(self.point_list)):
                    if repeat_list[i] == self.point_list[j]:
                        id_del.append(self.id_list[j])
                        break
            ctn_db.delete_one_row(id_del=id_del, type_=self.new_tp, proj_name=self.project_name,
                                  proj_revision=self.revision_name, if_list=True)
            text_ = 'All repeated records are removed'
            self.current_line.setText(text_)
            self.analysis_new_p_view()

    """ Delete one point """

    def delete_one_point(self):
        to_choose = self.point_list
        if len(to_choose) > 0:
            if len(to_choose) > 1:
                for i in range(len(to_choose)):
                    to_choose[i] = str(to_choose[i])
            else:
                to_choose[0] = str(to_choose[0])
            name_del, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Point to delete', to_choose, 0, False)
            for j in range(len(self.point_list)):
                if name_del == self.point_list[j]:
                    id_del = self.id_list[j]
                    ctn_db.delete_one_row(id_del=id_del, type_=self.new_tp, proj_name=self.project_name,
                                          proj_revision=self.revision_name)
                    text_ = 'Record ' + name_del + ' is removed'
                    self.current_line.setText(text_)
                    self.analysis_new_p_view()

    """ Delete all points """

    def delete_all(self):
        text_types = ('Yes', 'No')
        text_sel, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Yes or No', text_types, 0, False)
        if ok_pressed and text_sel == 'Yes':
            ctn_db.delete_all(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name)
            text_ = 'All records are removed'
            self.current_line.setText(text_)
            self.analysis_new_p_view()
