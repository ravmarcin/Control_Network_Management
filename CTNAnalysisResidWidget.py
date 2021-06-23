from PyQt5 import QtWidgets
from PyQt5 import QtGui
from CTNdb import *
from CTNInitWidget import *
from collections import Counter
import json
import time
import sys
import numpy as np
from functools import partial

ctn_db = CTNdb()

""" 
Widget for analysis of residuals.

Comparison of two projects, which includes:
    - compare the coordinates from dump files
    - compare the new with the old residuals
    - compare the new coordinates with the old ones
"""


class CTNAnalysisResidWidget(QtWidgets.QWidget):
    """ Constructor """

    def __init__(self):
        super().__init__()
        self.temp_ex_save = True


        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.table = QtWidgets.QTableWidget()
        self.table.setSortingEnabled(True)
        self.current_line = QtWidgets.QLineEdit()
        self.grid.addWidget(self.current_line, 1, 1, 1, 7)
        self.file_line = QtWidgets.QLineEdit()

        self.current_file_proj = ctn_db.current_file_proj
        self.old_file_proj = ctn_db.old_file_proj

        self.temp_compare = ctn_db.temp_compare
        self.temp_residuals = ctn_db.temp_residuals
        self.temp_ex_file = ctn_db.temp_ex_file
        self.temp_steps_file = ctn_db.temp_steps_file
        self.temp_new_p_file = ctn_db.temp_new_p_file
        self.temp_change_p_file = ctn_db.temp_change_p_file

        self.proj_tp = ctn_db.proj_tp
        self.dat_tp = ctn_db.dat_tp
        self.dp_tp = ctn_db.dp_tp
        self.ex_tp = ctn_db.ex_tp
        self.new_tp = ctn_db.new_tp
        self.ch_tp = ctn_db.ch_tp
        self.residua_tp = ctn_db.residua_tp

        self.cur_dp_tab_info = []
        self.cur_dp_row = []
        self.cur_dat_tab_info = []
        self.cur_dat_row = []
        self.cur_ex_tab_info = []
        self.cur_ex_row = []
        self.cur_new_tab_info = []
        self.cur_new_row = []

        self.old_dp_tab_info = []
        self.old_dp_row = []
        self.old_dat_tab_info = []
        self.old_dat_row = []
        self.old_ex_tab_info = []
        self.old_ex_row = []
        self.old_new_tab_info = []
        self.old_new_row = []

        self.old_res_tab_info = []
        self.old_res_row = []

        self.pt_to_del = []

        self.current_project = ''
        self.current_revision = ''
        self.old_project = ''
        self.old_revision = ''

        list_ = [[''], [''], [0], [0], [0], [0], [0], [0]]
        list_2 = [[''], [''], [0], [0], [0], [0], [0], [0], [0], [0], [0]]
        list_3 = [[''], [0], [0], [0], ['']]
        list_ = [np.array(i) for i in list_]
        self.starting_list_2 = np.array([np.array(i) for i in list_2])
        self.starting_list_3 = np.array([np.array(i) for i in list_3])
        self.starting_list_ = np.array(list_)
        self.new_proj = self.starting_list_
        self.new_pt_dump = self.starting_list_
        self.change_pt_dump = self.starting_list_
        self.old_proj = self.starting_list_
        self.residua = self.starting_list_2
        self.new_proj_ex = self.starting_list_3
        self.old_residua = []

        self.dp_n_rows = []
        self.ex_n_rows = []
        self.dp_o_rows = []
        self.ex_o_rows = []

        self.changed_points = np.array(list_3)

        self.point_list = []
        self.id_list = []
        self.project_open = False
        self.project_name = ''
        self.revision_name = ''
        try:
            with open(self.current_file_proj) as f:
                data_ = json.load(f)
            self.project_name = data_['project'][0]['project_name']
            self.revision_name = data_['project'][0]['project_revision']
            new_folder = ctn_db.ctn_data_id + '/' + self.project_name + self.revision_name
            self.temp_folder_ = new_folder + ctn_db.temp_folder
        except:
            self.current_line.setText('Something get wrong! Check the file ./temp/current_proj.json...')
        if len(self.project_name) > 0:
            self.project_open = True
        if self.project_open:
            text_ = 'You are in project: ' + self.project_name + '; revision: ' + self.revision_name
            self.current_line.setText(text_)
            try:
                self.load_project()
            except:
                self.current_line.setText('Something get wrong! Cannot computed the residuals')

            self.residual_analysis_view()

        else:
            text_ = 'No any project is open'
            self.current_line.setText(text_)
        self.setLayout(self.grid)
        self.show()

    """ Widget view """

    def residual_analysis_view(self):
        try:
            pt_to_del = []

            col_names_all = [col_[1] for col_ in self.cur_dp_tab_info]
            old_col_names = col_names_all[3:6] + col_names_all[12:15]
            old_col_names = [(i + '_old') for i in old_col_names]
            if len(self.old_residua) > 0:
                col_names = col_names_all[1:6] + col_names_all[12:15] + ['existing E', 'existing N', 'existing H', 'change', 'delete'] + old_col_names
                col_names = ['name', 'description', 'new DP to old DP - N', 'new DP to old DP - E',
                             'new DP to old DP - H', 'new DP to old DP - stdN', 'new DP to old DP - stdE',
                             'new DP to old DP - stdH', 'existing to new N', 'existing to new E', 'existing to new H',
                             'change', 'delete'] + old_col_names

            else:
                col_names = col_names_all[1:6] + col_names_all[12:15] + ['existing E', 'existing N', 'existing H', 'change', 'delete']
                col_names = ['name', 'description', 'new DP to old DP - N', 'new DP to old DP - E',
                             'new DP to old DP - H', 'new DP to old DP - stdN', 'new DP to old DP - stdE',
                             'new DP to old DP - stdH', 'existing to new N', 'existing to new E', 'existing to new H',
                             'change', 'delete']
            rows_n = len(self.new_proj[0, :])
            self.table.setRowCount(rows_n)
            self.table.setColumnCount(len(col_names))
            self.table.setHorizontalHeaderLabels(col_names)
            for i in range(rows_n):
                answer_ = True
                if len(str(self.residua[1, i])) > 7:
                    if str(self.residua[1, i])[0:7] == 'DELETE_':
                        answer_ = False
                if len(self.old_residua) > 0:
                    row_ = np.append(self.residua[:, i], self.old_residua[i, 0])
                    row_ = np.append(row_, self.old_residua[i, :])
                else:
                    row_ = self.residua[:, i]
                if not answer_:
                    pt_to_del.append(row_[0])
                for j in range(len(col_names)):
                    if col_names[j] != 'change' and col_names[j] != 'delete':
                        #if col_names[j] == 'existing E' or col_names[j] == 'existing N' or col_names[j] == 'existing H':
                        if col_names[j] == 'existing to new N' or col_names[j] == 'existing to new E' or col_names[j] == 'existing to new H':
                            if answer_:
                                self.table.setItem(i, j, QtWidgets.QTableWidgetItem("{:.4f}".format(float(row_[j]))))
                                if abs(float(row_[j])) >= 0.002:
                                    self.table.item(i, j).setBackground(QtGui.QColor(255, 100, 100))
                                elif abs(float(row_[j])) == 0.001:
                                    self.table.item(i, j).setBackground(QtGui.QColor(100, 255, 200))
                                elif abs(float(row_[j])) <= 0.001:
                                    self.table.item(i, j).setBackground(QtGui.QColor(100, 255, 100))
                            else:
                                self.table.setItem(i, j, QtWidgets.QTableWidgetItem('nan'))
                        elif col_names[j] != 'name' and col_names[j] != 'description':
                            self.table.setItem(i, j, QtWidgets.QTableWidgetItem("{:.4f}".format(float(row_[j]))))
                            if abs(float(row_[j])) >= 0.002:
                                self.table.item(i, j).setBackground(QtGui.QColor(255, 100, 100))
                            elif abs(float(row_[j])) == 0.001:
                                self.table.item(i, j).setBackground(QtGui.QColor(100, 255, 200))
                            elif abs(float(row_[j])) <= 0.001:
                                self.table.item(i, j).setBackground(QtGui.QColor(100, 255, 100))
                        else:
                            self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(row_[j])))
                    if col_names[j] == 'change':
                        if row_[j - 1] != 'nan':
                            btn_change = QtWidgets.QPushButton('Change no ' + str((i + 1)))
                            self.table.setCellWidget(i, j, btn_change)
                            btn_change.clicked.connect(partial(self.change_one_, i))
                        else:
                            self.table.setItem(i, j, QtWidgets.QTableWidgetItem(''))
                    if col_names[j] == 'delete':
                        if row_[j - 2] != 'nan':
                            btn_delete = QtWidgets.QPushButton('Delete no ' + str((i + 1)))
                            self.table.setCellWidget(i, j, btn_delete)
                            btn_delete.clicked.connect(partial(self.delete_one_, i))
                        else:
                            self.table.setItem(i, j, QtWidgets.QTableWidgetItem(''))
            self.pt_to_del = pt_to_del
        except:
            self.current_line.setText('Something get wrong! Cannot computed the residuals')

        btn_back = QtWidgets.QPushButton('Back')
        btn_back.clicked.connect(self.back_change)
        btn_change_above = QtWidgets.QPushButton('Change all above...')
        btn_change_above.clicked.connect(self.change_all_above)
        btn_save_ = QtWidgets.QPushButton('Save changes')
        btn_save_.clicked.connect(self.save_changes)
        btn_laod_ = QtWidgets.QPushButton('Load residua')
        btn_laod_.clicked.connect(self.residual_load)
        btn_calc_ = QtWidgets.QPushButton('Calculate residua')
        btn_calc_.clicked.connect(self.residual_calc_view)
        self.grid.addWidget(self.file_line, 2, 1, 1, 7)
        self.grid.addWidget(btn_back, 2, 8)
        self.grid.addWidget(btn_change_above, 1, 8)
        self.grid.addWidget(btn_save_, 2, 9)
        self.grid.addWidget(btn_laod_, 1, 9)
        self.grid.addWidget(btn_calc_, 1, 10)
        self.grid.addWidget(self.table, 3, 1, 6, 10)

        self.setLayout(self.grid)
        self.show()

    def residual_calc_view(self):
        self.residual_calc()
        self.export_to_temp()
        self.residual_analysis_view()

    def residual_load(self):
        self.load_temp_residuals()
        self.load_temp_comparison()
        self.load_temp_new_ex()
        self.load_temp_new_pt_dump()
        self.residual_analysis_view()

    """ Calculation of residuals """

    def residual_calc(self):

        self.new_proj = self.starting_list_
        self.new_pt_dump = self.starting_list_
        self.old_proj = self.starting_list_
        self.residua = np.array(self.starting_list_2)
        self.new_proj_ex = np.array(self.starting_list_3)

        """ For loop on new dump data """
        for i in range(len(self.dp_n_rows)):

            """ Find index in old dump data related to i-th point from new dump """
            index_old = np.argwhere(self.dp_o_rows[:, 1] == self.dp_n_rows[i, 1])

            """ If statement to check if there is any index in old dump """
            if np.size(index_old) > 0:
                index_old = index_old[0][0]

                """ 
                Row from new dump for i-th point 
                [name, description, northing, easting, elevation] + [std Northing, std Easting, std Elevation]
                """
                n_row = np.array(self.dp_n_rows[i, 1:6])
                std_n = self.dp_n_rows[i, 12:15]
                for j in std_n:
                    n_row = np.append(n_row, j)
                self.new_proj = np.append(self.new_proj, np.atleast_2d(n_row).T, axis=1)

                """ 
                Row from old dump for i-th point from new dump
                [name, description, northing, easting, elevation] + [std Northing, std Easting, std Elevation]
                """
                o_row = np.array(self.dp_o_rows[index_old, 1:6])
                std_o = self.dp_o_rows[index_old, 12:15]
                for j in std_o:
                    o_row = np.append(o_row, j)
                self.old_proj = np.append(self.old_proj, np.atleast_2d(o_row).T, axis=1)

                """ Find index in existing new points related to i-th point from new dump """
                index_ex_n = np.argwhere(self.ex_n_rows[:, 1] == self.dp_n_rows[i, 1])

                """ If statement to check if there is any index in existing new points """
                if np.size(index_ex_n) > 0:
                    index_ex_n = index_ex_n[0][0]

                    """ 
                    Row from existing new points for i-th point from new dump
                    [name, easting, northing, elevation]
                    """
                    ex_n_row = np.array(self.ex_n_rows[index_ex_n, 1:-1])
                    """ 
                    Row from existing new points for i-th point from new dump
                    [name, easting, northing, elevation, description]
                    """
                    ex_n_row_ar = np.array(self.ex_n_rows[index_ex_n, 1:])
                    self.new_proj_ex = np.append(self.new_proj_ex, np.atleast_2d(ex_n_row_ar).T, axis=1)

                """ Find index in existing old points related to i-th point from new dump """
                index_ex_o = np.argwhere(self.ex_o_rows[:, 1] == self.dp_n_rows[i, 1])

                """ If statement to check if there is any index in existing old points """
                if np.size(index_ex_o) > 0:
                    index_ex_o = index_ex_o[0][0]

                    """ 
                    Row from existing old points for i-th point from new dump
                    [name, easting, northing, elevation]
                    """
                    ex_o_row = np.array(self.ex_o_rows[index_ex_o, 1:-1])

                """ 
                Row to create residua for i-th point from new dump 
                [name, description]
                """
                res_row = np.array(self.dp_n_rows[i, 1:3])

                """ 
                Calculate residua from new dump and old dump rows for i-th point from new dump
                Append results to row for residua
                [name, description, res N dump, res E dump, res H dump]
                """
                for j in range(len(n_row[2:])):
                    res_ = float(n_row[j + 2]) - float(o_row[j + 2])
                    res_row = np.append(res_row, res_)

                """ 
                Calculate residua from new existing and old existing rows for i-th point from new dump,
                only if there are any,
                Append results to row for residua
                [name, description, res N dump, res E dump, res H dump, res N ex, res E ex, res H ex]
                """
                for j in range(3):
                    if np.size(index_ex_n) > 0 and np.size(index_ex_o) > 0:
                        res_ = float(ex_n_row[j + 1]) - float(ex_o_row[j + 1])
                        res_row = np.append(res_row, res_)
                    else:
                        res_row = np.append(res_row, 'nan')
                self.residua = np.append(self.residua, np.atleast_2d(res_row).T, axis=1)

            else:
                n_row = np.array(self.dp_n_rows[i, 1:6])
                std_n = self.dp_n_rows[i, 12:15]
                for j in std_n:
                    n_row = np.append(n_row, j)
                self.new_pt_dump = np.append(self.new_pt_dump, np.atleast_2d(n_row).T, axis=1)
        if self.new_proj[0, 0] == '':
            self.new_proj = self.new_proj[:, 1:]
        if self.old_proj[0, 0] == '':
            self.old_proj = self.old_proj[:, 1:]
        if self.residua[0, 0] == '':
            self.residua = self.residua[:, 1:]
        if self.new_proj_ex[0, 0] == '':
            self.new_proj_ex = self.new_proj_ex[:, 1:]
        if self.new_pt_dump[0, 0] == '':
            self.new_pt_dump = self.new_pt_dump[:, 1:]
        try:
            self.old_residua = self.convert_old_residua(old_residua=self.old_residua)
        except:
            pass

    """ Export data to temporary files """

    def export_to_temp(self):

        data_out = [self.new_proj, self.old_proj]
        if self.temp_ex_save:
            ctn_db.dump_temp_file(file=self.temp_compare, proj_name=self.current_project,
                                  proj_revision=self.current_revision, data_out=data_out)
            ctn_db.dump_temp_file(file=self.temp_residuals, proj_name=self.current_project,
                                  proj_revision=self.current_revision, data_out=self.residua)
            ctn_db.dump_temp_file(file=self.temp_ex_file, proj_name=self.current_project,
                                  proj_revision=self.current_revision, data_out=self.new_proj_ex)
            ctn_db.dump_temp_file(file=self.temp_new_p_file, proj_name=self.current_project,
                                  proj_revision=self.current_revision, data_out=self.new_pt_dump)

    """ Load the old and new projects """

    def load_project(self):
        current_project_dir = self.current_file_proj
        old_project_dir = self.old_file_proj
        if os.path.exists(current_project_dir):
            self.cur_dp_tab_info, self.cur_dp_row, self.cur_dat_tab_info, self.cur_dat_row, self.cur_ex_tab_info, self.cur_ex_row, self.cur_new_tab_info, self.cur_new_row = self.load_data(
                dir_=current_project_dir, proj_='n')
            self.dp_n_rows = np.array([np.array(i) for i in self.cur_dp_row])
            self.ex_n_rows = np.array([np.array(i) for i in self.cur_ex_row])
        if os.path.exists(old_project_dir):
            self.old_dp_tab_info, self.old_dp_row, self.old_dat_tab_info, self.old_dat_row, self.old_ex_tab_info, self.old_ex_row, self.old_new_tab_info, self.old_new_row = self.load_data(
                dir_=old_project_dir, proj_='o')
            self.dp_o_rows = np.array([np.array(i) for i in self.old_dp_row])
            self.ex_o_rows = np.array([np.array(i) for i in self.old_ex_row])

    """ Load the data from the project """

    def load_data(self, dir_, proj_):
        with open(dir_) as f:
            data_ = json.load(f)
            proj_name = data_['project'][0]['project_name']
            rev_name = data_['project'][0]['project_revision']
            dump_dir = data_['files'][0]['dump_file']
            dat_dir = data_['files'][0]['dat_file']
            ex_dir = data_['files'][0]['existing_file']
            new_dir = data_['files'][0]['new_points_file']
            residua_dir = data_['files'][0]['residua_file']

            dump_table_info, dump_rows = self.load_db(type_=self.dp_tp, dir_=dump_dir, proj_name=proj_name,
                                                      rev_name=rev_name)
            n_dat_table_info, dat_rows = self.load_db(type_=self.dat_tp, dir_=dat_dir, proj_name=proj_name,
                                                      rev_name=rev_name)
            ex_table_info, ex_rows = self.load_db(type_=self.ex_tp, dir_=ex_dir, proj_name=proj_name,
                                                  rev_name=rev_name)
            new_table_info, new_rows = self.load_db(type_=self.new_tp, dir_=new_dir, proj_name=proj_name,
                                                    rev_name=rev_name)

            if proj_ == 'n':
                self.current_project = proj_name
                self.current_revision = rev_name
            elif proj_ == 'o':
                self.old_project = proj_name
                self.old_revision = rev_name
                if len(residua_dir) > 0:
                    res_table_info, res_rows = self.load_db(type_=self.residua_tp, dir_=residua_dir, proj_name=proj_name,
                                                            rev_name=rev_name)
                    self.old_residua = np.array([np.array((i[0:2] + i[3:9])[1:]) for i in res_rows])

            return dump_table_info, dump_rows, n_dat_table_info, dat_rows, ex_table_info, ex_rows, new_table_info, new_rows

    """ Load the data from databases """

    def load_db(self, type_, dir_, proj_name, rev_name):
        table_info, rows_ = [], []
        if len(dir_) > 0:
            table_info = ctn_db.read_col_db(type_=type_, proj_name=proj_name, proj_revision=rev_name)
            rows_ = ctn_db.read_table_db(type_=type_, proj_name=proj_name, proj_revision=rev_name)
        return table_info, rows_

    """ Change the coordinates based on the limit in residuals """

    def change_all_above(self):
        to_choose = list(range(1, 11))
        to_choose = [str(i / 1000) for i in to_choose]
        limit_, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Limit for change', to_choose, 0, False)
        if ok_pressed:
            col_names_all = [col_[1] for col_ in self.cur_dp_tab_info]
            col_names = col_names_all[3:6] + col_names_all[12:15]
            column_, ok_pressed_2 = QtWidgets.QInputDialog.getItem(self, 'Select', 'Limit for change', col_names, 0,
                                                                   False)
            if ok_pressed_2:
                col_no = 2
                for i in range(len(col_names)):
                    if column_ == col_names[i]:
                        col_no = col_no + i
                        break
                residua_float = [float(i) for i in self.residua[col_no, :]]
                index_res_all = np.argwhere(np.abs(residua_float) > float(limit_))
                if np.size(index_res_all) > 0:
                    for i in range(len(index_res_all)):
                        index_ex = np.argwhere(self.residua[0, index_res_all[i]] == self.new_proj_ex[0, :])
                        if np.size(index_ex) > 0:
                            new_row = np.append(self.new_proj[0, index_res_all[i]], self.new_proj[2:5, index_res_all[i]])
                            new_row = np.append(new_row, self.new_proj[1, index_res_all[i]])
                            new_row_dump = self.new_proj[:, index_res_all[i]]
                            self.update_temp_residua(index_=index_res_all[i], new_row=new_row)
                            new_row_ex_index = np.argwhere(self.ex_n_rows[:, 1] == self.new_proj[0, index_res_all[i]])[0][0]
                            self.update_temp_existing(index_=new_row_ex_index, new_row=new_row)

                            for j in range(len(new_row)):
                                self.new_proj_ex[j, index_ex] = np.array(str(new_row[j]))
                            self.changed_points = np.append(self.changed_points, np.atleast_2d(new_row).T, axis=1)
                            self.change_pt_dump = np.append(self.change_pt_dump, np.atleast_2d(new_row_dump), axis=1)
                    if self.changed_points[0, 0] == '':
                        self.changed_points = self.changed_points[:, 1:]
                        self.change_pt_dump = self.change_pt_dump[:, 1:]
                    data_out = [[self.temp_ex_file], [self.ex_tp], ['change'], self.changed_points[0, :].tolist()]
                    ctn_db.dump_temp_file(file=self.temp_steps_file, proj_name=self.current_project,
                                          proj_revision=self.current_revision, data_out=data_out)
                self.export_to_temp()
                self.residual_analysis_view()

    """ Change only one points """

    def change_one_(self, i_):
        new_row = np.append(self.new_proj[0, i_], self.new_proj[2:5, i_])
        new_row = np.append(new_row, self.new_proj[1, i_])
        new_row_dump = self.new_proj[:, i_]

        self.update_temp_residua(index_=i_, new_row=new_row)
        self.changed_points = np.append(self.changed_points, np.atleast_2d(new_row).T, axis=1)
        self.change_pt_dump = np.append(self.change_pt_dump, np.atleast_2d(new_row_dump).T, axis=1)
        if self.changed_points[0, 0] == '':
            self.changed_points = self.changed_points[:, 1:]
            self.change_pt_dump = self.change_pt_dump[:, 1:]
        data_out = [[self.temp_ex_file], [self.ex_tp], ['change'], self.changed_points[0, -1]]
        ctn_db.dump_temp_file(file=self.temp_steps_file, proj_name=self.current_project,
                              proj_revision=self.current_revision, data_out=data_out)

        new_row_ex_index = np.argwhere(self.ex_n_rows[:, 1] == self.new_proj[0, i_])[0][0]
        self.update_temp_existing(index_=new_row_ex_index, new_row=new_row)
        self.export_to_temp()
        self.residual_analysis_view()

    """ Delete only one points """

    def delete_one_(self, i_):
        text_types = ('Yes', 'No')
        text_ = 'Are you sure to remove point ' + str(self.residua[0, i_])
        text_sel, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', text_, text_types, 0, False)
        if ok_pressed and text_sel == 'Yes':
            self.pt_to_del.append(str(self.residua[0, i_]))
            self.residua[1, i_] = 'DELETE_' + str(self.residua[0, i_])

            #new_row_ex_index = np.argwhere(self.ex_n_rows[:, 1] == self.new_proj[0, i_])[0][0]
            data_out = [[self.temp_new_p_file], [self.dp_tp], ['delete'], self.residua[0, i_]]
            ctn_db.dump_temp_file(file=self.temp_steps_file, proj_name=self.current_project,
                                  proj_revision=self.current_revision, data_out=data_out)
            
            self.export_to_temp()
            self.residual_analysis_view()

    """ Update the temporary residuals variable """

    def update_temp_residua(self, index_, new_row):

        """ Find index in existing old points related to index-th from residua  """
        index_ex_o = np.argwhere(self.ex_o_rows[:, 1] == self.residua[0, index_])

        """ If statement to check if there is any index in existing old points """
        if np.size(index_ex_o) > 0:
            index_ex_o = index_ex_o[0][0]

            """ 
            Row from existing old points
            [easting, northing, elevation]
            Conversion from string to float
            """
            ex_o_row = np.array(self.ex_o_rows[index_ex_o, 2:-1])
            new_row_res = [float(i) for i in new_row[1:-1]]
            ex_o_row_res = [float(i) for i in ex_o_row]

            """ 
            Update the data in existing residua
            Switch northing and easting in existing data
            """
            self.residua[1, index_] = new_row[-1]
            self.residua[8, index_] = new_row_res[0] - ex_o_row_res[1]
            self.residua[9, index_] = new_row_res[1] - ex_o_row_res[0]
            self.residua[10, index_] = new_row_res[2] - ex_o_row_res[2]

    """ Update the temporary coordinates variable """

    def update_temp_existing(self, index_, new_row):
        new_row_ex = [str(i) for i in new_row[1:-1]]
        self.ex_n_rows[index_, 1] = new_row[-1]
        self.ex_n_rows[index_, 2] = new_row_ex[0]
        self.ex_n_rows[index_, 3] = new_row_ex[1]
        self.ex_n_rows[index_, 4] = new_row_ex[2]

    """ Procedure to back one step """

    def back_change(self):
        data_in, procedure_ = ctn_db.back_result(proj_name=self.current_project, proj_revision=self.current_revision,
                                                 last_remove=True)
        if procedure_ == 'change':
            if len(data_in) > 1:
                for i in data_in:
                    position = np.argwhere(self.residua[0, :] == i[1])
                    new_row = [i[1], i[3], i[2], i[4], i[5]]
                    self.update_temp_residua(index_=position[0], new_row=new_row)
                    new_row_ex_index = np.argwhere(self.ex_n_rows[:, 1] == i[1])[0][0]
                    self.update_temp_existing(index_=new_row_ex_index, new_row=new_row)

            elif len(data_in) == 1:
                position = np.argwhere(self.residua[0, :] == data_in[0][1])
                new_row = [data_in[0][1], data_in[0][3], data_in[0][2], data_in[0][4], data_in[0][5]]
                self.update_temp_residua(index_=position[0], new_row=new_row)
                new_row_ex_index = np.argwhere(self.ex_n_rows[:, 1] == data_in[0][1])[0][0]
                self.update_temp_existing(index_=new_row_ex_index, new_row=new_row)
        elif procedure_ == 'delete':
            if len(data_in) > 1:
                for i in data_in:
                    position = np.argwhere(self.residua[0, :] == i[1])
                    self.residua[1, position[0]] = i[2]
                    pt_to_del = []
                    for j in self.pt_to_del:
                        if j != str(i[2]):
                            pt_to_del.append(j)
                    self.pt_to_del = pt_to_del
            elif len(data_in) == 1:
                position = np.argwhere(self.residua[0, :] == data_in[0][1])
                self.residua[1, position[0]] = data_in[0][2]
                pt_to_del = []
                for j in self.pt_to_del:
                    if j != str(data_in[0][2]):
                        pt_to_del.append(j)
                self.pt_to_del = pt_to_del
        self.export_to_temp()
        self.residual_analysis_view()

    """ Save the residuals to the database """

    def save_residual(self):
        data_out = self.residua
        if np.size(data_out) == 0:
            text_ = 'No residuals to save'
        elif data_out[0, 0] == '':
            text_ = 'No residuals to save'
        else:
            ctn_db.dump_database(type_=self.residua_tp, proj_name=self.project_name, proj_revision=self.revision_name,
                                 data_out=data_out)
            ctn_db.dump_temp_file(file=self.temp_residuals, proj_name=self.current_project,
                                  proj_revision=self.current_revision, data_out=self.residua)
            ctn_db.save_to_project(proj_name=self.project_name, proj_revision=self.revision_name, type_=self.residua_tp)
            text_ = 'Residuals have been saved'
        return text_

    """ Save the new points to the database """

    def save_new_points(self):
        data_out = self.new_pt_dump
        if np.size(data_out) == 0:
            text_ = 'No new points to save'
        elif data_out[0, 0] == '':
            text_ = 'No new points to save'
        else:
            ctn_db.dump_database(type_=self.new_tp, proj_name=self.project_name, proj_revision=self.revision_name,
                                 data_out=data_out)
            ctn_db.save_to_project(proj_name=self.project_name, proj_revision=self.revision_name, type_=self.new_tp)
            text_ = 'New points have been saved'
        return text_

    """ Save the changed points to the database """

    def save_change_points(self):
        data_out = self.change_pt_dump
        if np.size(data_out) == 0:
            text_ = 'No changed points to save'
        elif data_out[0, 0] == '':
            text_ = 'No changed points to save'
        else:
            ctn_db.dump_database(type_=self.ch_tp, proj_name=self.project_name, proj_revision=self.revision_name,
                                 data_out=data_out)
            ctn_db.save_to_project(proj_name=self.project_name, proj_revision=self.revision_name, type_=self.ch_tp)
            text_ = 'Changed points have been saved'
        return text_

    """ Save the changes in final values to the database """

    def save_changes_to_existing(self):
        data_out = np.transpose(self.ex_n_rows[:, 1:])
        if np.size(data_out) > 0:
            ctn_db.dump_database(type_=self.ex_tp, proj_name=self.project_name, proj_revision=self.revision_name,
                                 data_out=data_out)
            ctn_db.dump_temp_file(file=self.temp_ex_file, proj_name=self.current_project,
                                  proj_revision=self.current_revision, data_out=self.new_proj_ex)
            ctn_db.save_to_project(proj_name=self.project_name, proj_revision=self.revision_name, type_=self.ex_tp)
            text_ = 'Existing database is updated'
        else:
            text_ = 'No existing points to save'
        return text_

    def save_deleted_points(self):
        for i in self.pt_to_del:
            res_pos = np.argwhere(self.residua[0, :] == i)
            new_pos = np.argwhere(self.new_pt_dump[0, :] == i)
            ch_pos = np.argwhere(self.change_pt_dump[0, :] == i)
            ex_pos = np.argwhere(self.ex_n_rows[:, 1] == i)
            if len(res_pos) > 0:
                res_pos = res_pos[0][0]
                self.residua = np.delete(self.residua, res_pos, axis=1)
            if len(new_pos) > 0:
                new_pos = new_pos[0][0]
                self.new_pt_dump = np.delete(self.new_pt_dump, new_pos, axis=1)
            if len(ch_pos) > 0:
                ch_pos = ch_pos[0][0]
                self.change_pt_dump = np.delete(self.change_pt_dump, ch_pos, axis=1)
            if len(ex_pos) > 0:
                ex_pos = ex_pos[0][0]
                self.ex_n_rows = np.delete(self.ex_n_rows, ex_pos, axis=0)
        pass

    """ Save all to the database """

    def save_changes(self):
        self.save_deleted_points()
        text_res = self.save_residual()
        text_np = self.save_new_points()
        text_cp = self.save_change_points()
        text_ex = self.save_changes_to_existing()
        text_ = text_res + ' // ' + text_np + ' // ' + text_cp + ' // ' + text_ex
        self.file_line.setText(text_)
        ctn_db.create_temp_file(file_=self.temp_steps_file, temp_folder=self.temp_folder_)
        self.residual_analysis_view()

    """ Conversion of old residuals """

    def convert_old_residua(self, old_residua):
        old_residua_conv = []
        nan_ = np.array(['nan' for i in range(6)])
        for i in range(len(self.residua[0, :])):
            position = np.argwhere(old_residua[:, 0] == self.residua[0, i])
            if np.size(position) > 0:
                new_row = old_residua[position[0][0], :]
                old_residua_conv.append(new_row)
            else:
                old_residua_conv.append(np.append(self.residua[0, i], nan_))
        return np.vstack(old_residua_conv)

    """ Load calculated residuals """

    def load_temp_residuals(self):
        temp_residua = ctn_db.read_temp_file(file=self.temp_residuals, proj_name=self.project_name,
                                             proj_revision=self.revision_name)
        self.residua = np.array([np.array(i) for i in temp_residua])

    def load_temp_comparison(self):
        temp_comp = ctn_db.read_temp_file(file=self.temp_compare, proj_name=self.project_name,
                                          proj_revision=self.revision_name)
        new_proj = temp_comp[0]
        old_proj = temp_comp[1]
        self.new_proj = np.array([np.array(i) for i in new_proj])
        self.old_proj = np.array([np.array(i) for i in old_proj])

    def load_temp_new_ex(self):
        temp_new_ex = ctn_db.read_temp_file(file=self.temp_ex_file, proj_name=self.project_name,
                                            proj_revision=self.revision_name)
        self.new_proj_ex = np.array([np.array(i) for i in temp_new_ex])

    def load_temp_new_pt_dump(self):
        temp_new_pt_dump = ctn_db.read_temp_file(file=self.temp_new_p_file, proj_name=self.project_name,
                                                 proj_revision=self.revision_name)
        self.new_pt_dump = np.array([np.array(i) for i in temp_new_pt_dump])