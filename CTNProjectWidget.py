from PyQt5 import QtWidgets
from CTNdb import *

ctn_db = CTNdb()

""" Widget for projects and revisions management """


class CTNProjectWidget(QtWidgets.QWidget):
    """ Constructor """

    def __init__(self):
        super().__init__()
        self.grid = QtWidgets.QGridLayout()
        self.table = QtWidgets.QTableWidget()
        self.update_line = QtWidgets.QLineEdit()
        self.update_line.setText('')
        self.new_name_line = QtWidgets.QLineEdit()
        self.new_rev_line = QtWidgets.QLineEdit()
        self.project_name = 'Prj_34746_BlueJay_'
        self.revision_name = '_Rev_001'
        self.projects_view()
        self.name_check_test = False
        self.current_file_proj = ctn_db.current_file_proj

    """ Widget view """

    def projects_view(self):
        projects = []
        try:
            projects = ctn_db.read_projects_db()
        except:
            self.update_line.setText('Something get wrong! Check the project DB...')
        self.table.setRowCount(len(projects))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Id', 'Project', 'Revision'])
        for i in range(len(projects)):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(projects[i][0])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(projects[i][1]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(projects[i][2]))
        self.grid.setSpacing(10)

        self.new_name_line.setText('Project name')
        btn_new_name = QtWidgets.QPushButton('New project')
        btn_new_name.clicked.connect(self.name_dialog_project)
        self.new_rev_line.setText('Revision name')
        btn_new_rev = QtWidgets.QPushButton('New revision')
        btn_new_rev.clicked.connect(self.name_dialog_revision)
        btn_create = QtWidgets.QPushButton('Create')
        btn_create.clicked.connect(self.create_new_project)
        btn_delete = QtWidgets.QPushButton('Delete')
        btn_delete.clicked.connect(self.delete_project)
        btn_import = QtWidgets.QPushButton('Import')
        btn_import.clicked.connect(self.import_project_file)
        btn_create_db = QtWidgets.QPushButton('Create DB')
        btn_create_db.clicked.connect(self.create_new_db)
        self.grid.addWidget(self.update_line, 1, 1, 1, 4)
        self.grid.addWidget(btn_new_name, 2, 1)
        self.grid.addWidget(self.new_name_line, 2, 2)
        self.grid.addWidget(btn_new_rev, 2, 3)
        self.grid.addWidget(self.new_rev_line, 2, 4)
        self.grid.addWidget(btn_create, 2, 5)
        self.grid.addWidget(btn_delete, 2, 6)
        self.grid.addWidget(btn_import, 1, 5)
        self.grid.addWidget(btn_create_db, 1, 6)
        self.grid.addWidget(self.table, 3, 1, 6, 6)
        self.setLayout(self.grid)
        self.show()

    """ Fill the project name """

    def name_dialog_project(self):
        text, ok_pressed = QtWidgets.QInputDialog.getText(self, 'Project name', 'Project name')
        if ok_pressed:
            self.new_name_line.setText(text)
            self.project_name = 'Prj_' + text

    """ Fill the revision name """

    def name_dialog_revision(self):
        text, ok_pressed = QtWidgets.QInputDialog.getText(self, 'Revision name', 'Revision name')
        if ok_pressed:
            self.new_rev_line.setText(text)
            self.revision_name = '_Rev_' + text

    """ Delete one project """

    def delete_project(self):
        projects = []
        try:
            projects = ctn_db.read_projects_db()
        except:
            self.update_line.setText('Something get wrong! Check the project DB...')
        id_list, i_list = [], []
        for i in range(len(projects)):
            id_list.append(projects[i][0])
            i_list.append(i)
        to_choose = id_list
        if len(to_choose) > 0:
            if len(to_choose) > 1:
                for i in range(len(to_choose)):
                    to_choose[i] = str(to_choose[i])
            else:
                to_choose[0] = str(to_choose[0])
            id_del, ok_pressed = QtWidgets.QInputDialog.getItem(self, 'Select', 'Project to delete', to_choose, 0,
                                                                False)
            if ok_pressed:
                i_ = 0
                for i in range(len(id_list)):
                    if int(id_del) == int(id_list[i]):
                        i_ = i_list[i]
                proj_name, rev_name = projects[i_][1], projects[i_][2]
                try:
                    ctn_db.delete_project(id_del=id_del)
                    text_ = 'Deleted project: ' + proj_name + rev_name
                    self.update_line.setText(text_)
                except:
                    self.update_line.setText('Something get wrong!')
                self.projects_view()

    """ Create new project """

    def create_new_project(self):
        projects = []
        try:
            projects = ctn_db.read_projects_db()
        except:
            self.update_line.setText('Something get wrong! Check the project DB...')
        for i in range(len(projects)):
            if projects[i][1] == self.project_name and projects[i][2] == self.revision_name:
                self.name_check_test = True
        if self.name_check_test:
            self.update_line.setText('Project and revision name are repeated')
            self.projects_view()
            pass
        else:
            try:
                ctn_db.add_project_rev(proj_name=self.project_name, proj_revision=self.revision_name)
                text_ = 'Created project: ' + self.project_name + self.revision_name
                self.update_line.setText(text_)

                json_obj = {'project': [], 'files': []}
                json_obj['project'].append({
                    'project_name': self.project_name,
                    'project_revision': self.revision_name
                })
                json_obj['files'].append({
                    'dump_file': '',
                    'dat_file': '',
                    'existing_file': '',
                    'new_points_file': '',
                    'changed_points_file': ''
                })
                with open(self.current_file_proj, 'w') as jsonFile:
                    json.dump(json_obj, jsonFile)
            except:
                self.update_line.setText('Something get wrong!...')
            self.projects_view()
        self.name_check_test = False

    """ Import other project """

    def import_project_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, ok_select = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',
                                                                     'All Files (*);;Python Files (*.py)',
                                                                     options=options)
        if ok_select:
            try:
                ctn_db.import_project(dir_zip_file=file_name)
                self.update_line.setText('File ' + str(file_name) + ' is saved in database')
            except:
                self.update_line.setText('Something get wrong! Try .zip archive...')
            self.projects_view()

    def create_new_db(self):
        try:
            ctn_db.projects_db_create()
            self.update_line.setText('Database for projects is created')
        except:
            self.update_line.setText('Something get wrong! Check the project DB...')
