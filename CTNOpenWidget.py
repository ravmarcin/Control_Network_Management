from PyQt5 import QtWidgets
from CTNdb import *
from CTNInitWidget import *
from collections import Counter
import json
import time
import sys
ctn_db = CTNdb()

""" Widget to open the old and current revision for analysis """


class CTNOpenWidget(QtWidgets.QWidget):
    """ Constructor """

    def __init__(self):
        super().__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.current_line = QtWidgets.QLineEdit()
        self.grid.addWidget(self.current_line, 1, 1, 1, 5)

        self.current_file_line = QtWidgets.QLineEdit()
        self.current_project_win = QtWidgets.QTextEdit()
        self.current_project_win.setText('')
        self.old_file_line = QtWidgets.QLineEdit()
        self.old_project_win = QtWidgets.QTextEdit()
        self.old_project_win.setText('')
        self.temp_folder = ctn_db.temp_folder
        self.current_file_proj = ctn_db.current_file_proj
        self.old_file_proj = ctn_db.old_file_proj
        self.project_open = False

        self.project_ = ''
        self.revision_ = ''
        self.dump_file = ''
        self.dat_file = ''
        self.existing_file = ''
        self.new_points_file = ''
        self.changed_points_file = ''
        self.residua_file = ''

        self.project_old = ''
        self.revision_old = ''
        self.dump_file_old = ''
        self.dat_file_old = ''
        self.existing_file_old = ''
        self.new_points_file_old = ''
        self.changed_points_file_old = ''
        self.residua_file_old = ''


        try:
            with open(self.current_file_proj) as f:
                data_ = json.load(f)
            self.project_name = data_['project'][0]['project_name']
            self.revision_name = data_['project'][0]['project_revision']
            if len(self.project_name) > 0:
                self.project_open = True
            if self.project_open:
                text_ = 'You are in project: ' + self.project_name + '; revision: ' + self.revision_name
                self.current_line.setText(text_)
            else:
                text_ = 'No any project is open'
                self.current_line.setText(text_)
        except:
            self.current_line.setText('Something get wrong! Check the file ./temp/current_proj.json...')

        self.project_view()
        self.setLayout(self.grid)
        self.show()

    """ Widget view """

    def project_view(self):
        btn_open_working_proj = QtWidgets.QPushButton('Open new revision')
        btn_open_working_proj.clicked.connect(self.open_working_project)
        btn_open_old_proj = QtWidgets.QPushButton('Open old revision')
        btn_open_old_proj.clicked.connect(self.open_old_project)
        self.grid.addWidget(btn_open_working_proj, 2, 1)
        self.grid.addWidget(self.current_project_win, 3, 1, 9, 2)
        self.grid.addWidget(self.current_file_line, 2, 2)
        self.grid.addWidget(btn_open_old_proj, 2, 3)
        self.grid.addWidget(self.old_file_line, 2, 4)
        self.grid.addWidget(self.old_project_win, 3, 3, 9, 2)
        self.setLayout(self.grid)
        self.show()

    """ 
    Open current project with working revision
    
    File with suffix: -- _project_proj.json -- 
    """

    def open_working_project(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, ok_select = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',
                                                                     'All Files (*);;Python Files (*.py)',
                                                                     options=options)
        if ok_select:
            try:
                if file_name[-10:] == '_proj.json':
                    with open(file_name) as f:
                        data_ = json.load(f)

                    self.project_ = data_['project'][0]['project_name']
                    self.revision_ = data_['project'][0]['project_revision']
                    self.dump_file = data_['files'][0]['dump_file']
                    self.dat_file = data_['files'][0]['dat_file']
                    self.existing_file = data_['files'][0]['existing_file']
                    self.new_points_file = data_['files'][0]['new_points_file']
                    self.changed_points_file = data_['files'][0]['changed_points_file']
                    self.residua_file = data_['files'][0]['residua_file']
                    self.project_open = True

                    json_obj = {'project': [], 'files': []}
                    json_obj['project'].append({
                        'project_name': self.project_,
                        'project_revision': self.revision_
                    })
                    json_obj['files'].append({
                        'dump_file': self.dump_file,
                        'dat_file': self.dat_file,
                        'existing_file': self.existing_file,
                        'new_points_file': self.new_points_file,
                        'changed_points_file': self.changed_points_file,
                        'residua_file': self.residua_file
                    })
                    with open(self.current_file_proj, 'w') as jsonFile:
                        json.dump(json_obj, jsonFile)
                    text_ = 'You are in project: ' + self.project_ + '; revision: ' + self.revision_
                    self.current_line.setText(text_)
                    self.current_file_line.setText(file_name)
                    sent_ = ''
                    for key, value in data_.items():
                        sent_ = sent_ + '\n' + str(key) + ' : ' + '\n' + '\t' + str(value) + '\n'
                        self.current_project_win.setText(sent_)
                else:
                    self.current_line.setText('Wrong file! Try to open project file (..._project_proj.json)')
            except:
                self.current_line.setText('Something get wrong! Check the file ./temp/current_proj.json...')
        self.project_view()

    """ 
    Open current project with old revision

    File with suffix: -- _project_proj.json -- 
    """

    def open_old_project(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, ok_select = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',
                                                                     'All Files (*);;Python Files (*.py)',
                                                                     options=options)
        if ok_select:
            try:
                if file_name[-10:] == '_proj.json':
                    with open(file_name) as f:
                        data_ = json.load(f)
                    self.project_old = data_['project'][0]['project_name']
                    self.revision_old = data_['project'][0]['project_revision']
                    self.dump_file_old = data_['files'][0]['dump_file']
                    self.dat_file_old = data_['files'][0]['dat_file']
                    self.existing_file_old = data_['files'][0]['existing_file']
                    self.new_points_file_old = data_['files'][0]['new_points_file']
                    self.changed_points_file_old = data_['files'][0]['changed_points_file']
                    self.residua_file_old = data_['files'][0]['residua_file']
                    self.project_open = True

                    json_obj = {'project': [], 'files': []}
                    json_obj['project'].append({
                        'project_name': self.project_old,
                        'project_revision': self.revision_old
                    })
                    json_obj['files'].append({
                        'dump_file': self.dump_file_old,
                        'dat_file': self.dat_file_old,
                        'existing_file': self.existing_file_old,
                        'new_points_file': self.new_points_file_old,
                        'changed_points_file': self.changed_points_file_old,
                        'residua_file': self.residua_file_old
                    })
                    with open(self.old_file_proj, 'w') as jsonFile:
                        json.dump(json_obj, jsonFile)
                    text_ = 'Your project to compare is: ' + self.project_ + '; revision: ' + self.revision_
                    self.current_line.setText(text_)
                    self.old_file_line.setText(file_name)
                    sent_ = ''
                    for key, value in data_.items():
                        sent_ = sent_ + '\n' + str(key) + ' : ' + '\n' + '\t' + str(value) + '\n'
                        self.old_project_win.setText(sent_)
                else:
                    self.current_line.setText('Wrong file! Try to open project file (..._project_proj.json)')
            except:
                self.current_line.setText('Something get wrong! Check the file ./temp/current_proj.json...')
        self.project_view()
