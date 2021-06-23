from PyQt5 import QtWidgets
from CTNdb import *
from CTNInitWidget import *
from collections import Counter
import json
import time
import sys
ctn_db = CTNdb()

""" Widget for import of dat files """


class CTNImportDatWidget(QtWidgets.QWidget):
    """ Constructor """

    def __init__(self):
        super().__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        self.table = QtWidgets.QTableWidget()
        self.table_res = QtWidgets.QTableWidget()
        self.table_del = QtWidgets.QTableWidget()

        self.current_line = QtWidgets.QLineEdit()
        self.grid.addWidget(self.current_line, 1, 1, 1, 1)
        self.file_line = QtWidgets.QLineEdit()
        self.file_name = ''

        current_file_proj = ctn_db.current_file_proj
        self.dat_tp = ctn_db.dat_tp
        self.res_tp = ctn_db.res_tp
        self.del_tp = ctn_db.del_tp

        self.point_list = []
        self.id_list = []
        self.point_list_res = []
        self.id_list_res = []
        self.point_list_del = []
        self.id_list_del = []
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
            self.import_dat_view()
        else:
            text_ = 'No any project is open'
            self.current_line.setText(text_)
        self.setLayout(self.grid)
        self.show()

    """ Widget view """

    def import_dat_view(self):
        table_info = ctn_db.read_col_db(type_=self.dat_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names = [col_[1] for col_ in table_info]
        rows_ = ctn_db.read_table_db(type_=self.dat_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.table.setRowCount(len(rows_))
        self.table.setColumnCount(len(col_names))
        self.table.setHorizontalHeaderLabels(col_names)
        for i in range(len(rows_)):
            for j in range(len(col_names)):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(rows_[i][j])))
                if col_names[j] == 'file_dir':
                    self.point_list.append(str(rows_[i][j]))
                    self.id_list.append(str(rows_[i][j-1]))

        table_info_res = ctn_db.read_col_db(type_=self.res_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names_res = [col_[1] for col_ in table_info_res]
        rows_res = ctn_db.read_table_db(type_=self.res_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.table_res.setRowCount(len(rows_res))
        self.table_res.setColumnCount(len(col_names_res))
        self.table_res.setHorizontalHeaderLabels(col_names_res)
        for i in range(len(rows_res)):
            for j in range(len(col_names_res)):
                self.table_res.setItem(i, j, QtWidgets.QTableWidgetItem(str(rows_res[i][j])))
                if col_names_res[j] == 'resection_name':
                    self.point_list_res.append(str(rows_res[i][j]))
                    self.id_list_res.append(str(rows_res[i][j-1]))

        table_info_del = ctn_db.read_col_db(type_=self.del_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        col_names_del = [col_[1] for col_ in table_info_del]
        rows_del = ctn_db.read_table_db(type_=self.del_tp, proj_name=self.project_name, proj_revision=self.revision_name)
        self.table_del.setRowCount(len(rows_del))
        self.table_del.setColumnCount(len(col_names_del))
        self.table_del.setHorizontalHeaderLabels(col_names_del)
        for i in range(len(rows_del)):
            for j in range(len(col_names_del)):
                self.table_del.setItem(i, j, QtWidgets.QTableWidgetItem(str(rows_del[i][j])))
                if col_names_del[j] == 'delete_name':
                    self.point_list_del.append(str(rows_del[i][j]))
                    self.id_list_del.append(str(rows_del[i][j-1]))

        btn_save = QtWidgets.QPushButton('Save')
        btn_save.clicked.connect(self.save_file)
        btn_import = QtWidgets.QPushButton('Import')
        btn_import.clicked.connect(self.import_file)
        btn_read = QtWidgets.QPushButton('Read dat file')
        btn_read.clicked.connect(self.read_dat_file_but)

        btn_delete_dat = QtWidgets.QPushButton('Delete dat')
        btn_delete_dat.clicked.connect(self.delete_one_point_dat)
        btn_delete_all_dat = QtWidgets.QPushButton('Delete all dats')
        btn_delete_all_dat.clicked.connect(self.delete_all_dat)
        btn_delete_res = QtWidgets.QPushButton('Delete resec')
        btn_delete_res.clicked.connect(self.delete_one_point_res)
        btn_delete_all_res = QtWidgets.QPushButton('Delete all resecs')
        btn_delete_all_res.clicked.connect(self.delete_all_res)
        btn_delete_del = QtWidgets.QPushButton('Delete point')
        btn_delete_del.clicked.connect(self.delete_one_point_del)
        btn_delete_all_del = QtWidgets.QPushButton('Delete all points')
        btn_delete_all_del.clicked.connect(self.delete_all_del)

        self.grid.addWidget(btn_save, 1, 2, 1, 1)
        self.grid.addWidget(btn_import, 1, 3, 1, 1)
        self.grid.addWidget(self.file_line, 1, 4, 1, 2)
        self.grid.addWidget(btn_read, 1, 6, 1, 1)
        self.grid.addWidget(btn_delete_dat, 2, 1)
        self.grid.addWidget(btn_delete_all_dat, 2, 2)
        self.grid.addWidget(btn_delete_res, 2, 3)
        self.grid.addWidget(btn_delete_all_res, 2, 4)
        self.grid.addWidget(btn_delete_del, 2, 5)
        self.grid.addWidget(btn_delete_all_del, 2, 6)

        self.grid.addWidget(self.table, 3, 1, 10, 2)
        self.grid.addWidget(self.table_res, 3, 3, 10, 2)
        self.grid.addWidget(self.table_del, 3, 5, 10, 2)
        self.setLayout(self.grid)
        self.show()

    """ Save the file to the database """

    def save_file(self):
        if len(self.file_name) > 0:
            ctn_db.save_to_project(proj_name=self.project_name, proj_revision=self.revision_name, type_=self.dat_tp)
            text_ = 'Dat file is saved to the project: ' + self.project_name + '; rev: ' + self.revision_name
            self.current_line.setText(text_)
        else:
            text_ = "No any project is open!\n"
            self.current_line.setText(text_)
        self.import_dat_view()

    """ Import the dat file """

    def import_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, ok_select = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',
                                                                     'All Files (*);;Python Files (*.py)',
                                                                     options=options)
        if ok_select:
            if file_name[-3:] == 'dat':
                if self.project_open:
                    ctn_db.import_file(file_dir=file_name, type_=self.dat_tp, proj_name=self.project_name,
                                       proj_revision=self.revision_name)
                    self.file_name = file_name
                    self.file_line.setText(str(file_name))
                else:
                    text_ = "No any project is open!\n"
                    self.current_line.setText(text_)
        self.import_dat_view()

    """ Delete one point from dat file """

    def delete_one_point_dat(self):
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
                    ctn_db.delete_one_row(id_del=id_del, type_=self.dat_tp, proj_name=self.project_name,
                                          proj_revision=self.revision_name)
                    text_ = 'Record ' + name_del + ' is removed'
                    self.current_line.setText(text_)
                    self.import_dat_view()

    """ Delete one resection point """

    def delete_one_point_res(self):
        to_choose = self.point_list_res
        if len(to_choose) > 0:
            if len(to_choose) > 1:
                for i in range(len(to_choose)):
                    to_choose[i] = str(to_choose[i])
            else:
                to_choose[0] = str(to_choose[0])
            name_del, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Point to delete', to_choose, 0, False)
            for j in range(len(self.point_list_res)):
                if name_del == self.point_list_res[j]:
                    id_del = self.id_list_res[j]
                    ctn_db.delete_one_row(id_del=id_del, type_=self.res_tp, proj_name=self.project_name,
                                          proj_revision=self.revision_name)
                    text_ = 'Resection record ' + name_del + ' is removed'
                    self.current_line.setText(text_)
                    self.import_dat_view()

    """ Delete one point from the points to remove """

    def delete_one_point_del(self):
        to_choose = self.point_list_del
        if len(to_choose) > 0:
            if len(to_choose) > 1:
                for i in range(len(to_choose)):
                    to_choose[i] = str(to_choose[i])
            else:
                to_choose[0] = str(to_choose[0])
            name_del, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Point to delete', to_choose, 0, False)
            for j in range(len(self.point_list_del)):
                if name_del == self.point_list_del[j]:
                    id_del = self.id_list_del[j]
                    ctn_db.delete_one_row(id_del=id_del, type_=self.del_tp, proj_name=self.project_name,
                                          proj_revision=self.revision_name)
                    text_ = 'Record to delete ' + name_del + ' is removed'
                    self.current_line.setText(text_)
                    self.import_dat_view()

    """ Delete all points from dat file """

    def delete_all_dat(self):
        text_types = ('Yes', 'No')
        text_sel, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Yes or No', text_types, 0, False)
        if ok_pressed and text_sel == 'Yes':
            ctn_db.delete_all(type_=self.dat_tp, proj_name=self.project_name, proj_revision=self.revision_name)
            text_ = 'All records to delete are removed'
            self.current_line.setText(text_)
            self.import_dat_view()

    """ Delete all resections """

    def delete_all_res(self):
        text_types = ('Yes', 'No')
        text_sel, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Yes or No', text_types, 0, False)
        if ok_pressed and text_sel == 'Yes':
            ctn_db.delete_all(type_=self.res_tp, proj_name=self.project_name, proj_revision=self.revision_name)
            text_ = 'All resections records are removed'
            self.current_line.setText(text_)
            self.import_dat_view()

    """ Delete all points from the points to remove """

    def delete_all_del(self):
        text_types = ('Yes', 'No')
        text_sel, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Yes or No', text_types, 0, False)
        if ok_pressed and text_sel == 'Yes':
            ctn_db.delete_all(type_=self.del_tp, proj_name=self.project_name, proj_revision=self.revision_name)
            text_ = 'All records are removed'
            self.current_line.setText(text_)
            self.import_dat_view()

    """ Read the data from dat file """

    def read_dat_file_but(self):
        to_choose = self.point_list

        if len(to_choose) > 0:
            if len(to_choose) > 1:
                for i in range(len(to_choose)):
                    to_choose[i] = str(to_choose[i])
            else:
                to_choose[0] = str(to_choose[0])
            name_read, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'File to read', to_choose, 0, False)
            for j in range(len(self.point_list)):
                if name_read == self.point_list[j]:
                    id_read = self.id_list[j]
                    ctn_db.read_dat_file(id_file=id_read, proj_name=self.project_name, proj_revision=self.revision_name)
                    text_ = 'Dat file is read and applied to dump filed'
                    self.current_line.setText(text_)
                    self.import_dat_view()
