from PyQt5 import QtWidgets, QtCore
from CTNdb import *
from CTNInitWidget import *
from collections import Counter
import json
import time
import sys
import csv
import numpy as np
import pandas as pd
import datetime
ctn_db = CTNdb()

""" Widget for export the results """


class CTNExportExistingWidget(QtWidgets.QWidget):
    """ Constructor """

    def __init__(self):
        super().__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.table = QtWidgets.QTableWidget()
        self.current_line = QtWidgets.QLineEdit()
        self.grid.addWidget(self.current_line, 1, 1, 1, 6)
        self.file_line = QtWidgets.QLineEdit()

        self.final_to_export = []
        self.register_to_export = []
        self.new_to_export = []
        self.change_to_export = []
        self.col_names = []

        self.new_rev_line = QtWidgets.QLineEdit()
        current_file_proj = ctn_db.current_file_proj
        self.ex_tp = ctn_db.ex_tp
        self.ch_tp = ctn_db.ch_tp
        self.new_tp = ctn_db.new_tp

        self.file_name = ''
        self.section_name = ''
        self.remarks_name = ''
        self.register_columns = ['Date', 'Version', 'Stations Added', 'Section', 'Stations changed', 'Remarks']

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
            self.export_existing_view()
        else:
            text_ = 'No any project is open'
            self.current_line.setText(text_)
        self.setLayout(self.grid)
        self.show()

    """ Widget view """

    def export_existing_view(self):
        table_info = ctn_db.read_col_db(type_=self.ex_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.col_names = [col_[1] for col_ in table_info]
        self.final_to_export = ctn_db.read_table_db(type_=self.ex_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.table.setRowCount(len(self.final_to_export))
        self.table.setColumnCount(len(self.col_names))
        self.table.setHorizontalHeaderLabels(self.col_names)
        for i in range(len(self.final_to_export)):
            for j in range(len(self.col_names)):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(self.final_to_export[i][j])))
                if self.col_names[j] == 'name':
                    self.point_list.append(str(self.final_to_export[i][j]))
                    self.id_list.append(str(self.final_to_export[i][j-1]))
        btn_export_fin = QtWidgets.QPushButton('Export final')
        btn_export_fin.clicked.connect(self.export_final)
        btn_export_reg = QtWidgets.QPushButton('Export register')
        btn_export_reg.clicked.connect(self.export_register)
        btn_export_new = QtWidgets.QPushButton('Export new points')
        btn_export_new.clicked.connect(self.export_new)
        btn_export_change = QtWidgets.QPushButton('Export changed points')
        btn_export_change.clicked.connect(self.export_change)
        self.grid.addWidget(self.table, 3, 1, 6, 9)
        self.grid.addWidget(btn_export_fin, 1, 7, 1, 1)
        self.grid.addWidget(self.file_line, 2, 1, 1, 6)
        self.grid.addWidget(btn_export_reg, 1, 8, 1, 1)
        self.grid.addWidget(btn_export_new, 2, 7, 1, 1)
        self.grid.addWidget(btn_export_change, 2, 8, 1, 1)
        self.grid.addWidget(self.table, 3, 1, 6, 9)
        self.setLayout(self.grid)
        self.show()

    """ Export final values to the .csv format """

    def export_final(self):
        filename, ok_select = QtWidgets.QFileDialog.getSaveFileName(self, "Save File",
                                                                    (QtCore.QDir.homePath() + "/" + self.project_name +
                                                                     self.revision_name + "_FinalValues.csv"),
                                                                    "CSV Files (*.csv)")
        if ok_select:
            self.file_name = filename
            df_ = pd.DataFrame(np.array(self.final_to_export))
            df_.columns = self.col_names
            df_[self.col_names[1:]].to_csv(self.file_name, index=False)
            self.file_line.setText('The final values are saved in th file: ' + self.file_name)
        self.export_existing_view()

    """ Export new points to the .csv format """

    def export_new(self):
        filename, ok_select = QtWidgets.QFileDialog.getSaveFileName(self, "Save File",
                                                                    (QtCore.QDir.homePath() + "/" + self.project_name +
                                                                     self.revision_name + "_NewPoints.csv"),
                                                                    "CSV Files (*.csv)")
        if ok_select:
            self.file_name = filename
            self.create_new()
            self.new_to_export.to_csv(self.file_name, index=False)
            self.file_line.setText('The new points are saved in th file: ' + self.file_name)
        self.export_existing_view()

    """ Export changed points to the .csv format """

    def export_change(self):
        filename, ok_select = QtWidgets.QFileDialog.getSaveFileName(self, "Save File",
                                                                    (QtCore.QDir.homePath() + "/" + self.project_name +
                                                                     self.revision_name + "_ChangedPoints.csv"),
                                                                    "CSV Files (*.csv)")
        if ok_select:
            self.file_name = filename
            self.create_change()
            self.change_to_export.to_csv(self.file_name, index=False)
            self.file_line.setText('The changed points are saved in th file: ' + self.file_name)
        self.export_existing_view()

    """ Export register file with the information about revision """

    def export_register(self):
        text_, ok_pressed = QtWidgets.QInputDialog.getText(self, 'Section', 'Section name')
        if ok_pressed:
            self.section_name = text_

        text_, ok_pressed = QtWidgets.QInputDialog.getText(self, 'Remarks', 'Remarks')
        if ok_pressed:
            self.remarks_name = text_

        filename, ok_select = QtWidgets.QFileDialog.getSaveFileName(self, "Save File",
                                                                    (QtCore.QDir.homePath() + "/" + self.project_name +
                                                                     self.revision_name + "_Register.csv"),
                                                                    "CSV Files (*.csv)")
        if ok_select:
            self.file_name = filename
            self.create_register()
            self.register_to_export.to_csv(self.file_name, index=False)
            self.file_line.setText('The register sheet is saved in th file: ' + self.file_name)
        self.export_existing_view()

    """ Create register file with the information about revision """

    def create_register(self):
        date_ = str(datetime.date.today())
        year_ = date_[:4]
        month_ = date_[5:7]
        day_ = date_[8:10]
        date_con = year_ + '/' + month_ + '/' + day_

        project_name = self.project_name + self.revision_name

        list_change = []
        list_change_str = ''
        table_info = ctn_db.read_col_db(type_=self.ch_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names_c = [col_[1] for col_ in table_info]
        rows_c = ctn_db.read_table_db(type_=self.ch_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        for i in range(len(rows_c)):
            for j in range(len(col_names_c)):
                if col_names_c[j] == 'name':
                    list_change.append(str(rows_c[i][j]))
                    if i == 0:
                        list_change_str = str(rows_c[i][j])
                    else:
                        list_change_str = list_change_str + ', ' + str(rows_c[i][j])
                    break

        list_new = []
        list_new_str = ''
        table_info = ctn_db.read_col_db(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names_n = [col_[1] for col_ in table_info]
        rows_n = ctn_db.read_table_db(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        for i in range(len(rows_n)):
            for j in range(len(col_names_n)):
                if col_names_n[j] == 'name':
                    list_new.append(str(rows_n[i][j]))
                    if i == 0:
                        list_new_str = str(rows_n[i][j])
                    else:
                        list_new_str = list_new_str + ', ' + str(rows_n[i][j])
                    break

        data_ = {self.register_columns[0]: [date_con],
                self.register_columns[1]: [project_name],
                self.register_columns[2]: [list_new_str],
                self.register_columns[3]: [self.section_name],
                self.register_columns[4]: [list_change_str],
                self.register_columns[5]: [self.remarks_name],
                }
        self.register_to_export = pd.DataFrame(data_, columns=self.register_columns)

    """ Create new points to the .csv format """

    def create_new(self):
        table_info = ctn_db.read_col_db(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names_n = [col_[1] for col_ in table_info]
        new_to_export = ctn_db.read_table_db(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.new_to_export = pd.DataFrame(new_to_export, columns=col_names_n)

    """ Create changed points to the .csv format """

    def create_change(self):
        table_info = ctn_db.read_col_db(type_=self.ch_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names_n = [col_[1] for col_ in table_info]
        change_to_export = ctn_db.read_table_db(type_=self.ch_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.change_to_export = pd.DataFrame(change_to_export, columns=col_names_n)