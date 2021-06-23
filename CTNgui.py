from PyQt5 import QtWidgets
from PyQt5 import QtGui
from CTNProjectWidget import *
from CTNOpenWidget import *
from CTNInitWidget import *
from CTNImportDumpWidget import *
from CTNImportDatWidget import *
from CTNAnalysisResidWidget import *
from CTNImportExistingWidget import *
from CTNAnalysisNewPointsWidget import *
from CTNAnalysisChangePointsWidget import *
from CTNExportExistingWidget import *

""" Graphical User Interface - main window of the CTN app"""


class CTNgui(QtWidgets.QMainWindow):
    """ Constructor """

    def __init__(self):
        super().__init__()
        self.init_menu()

    """ Main window view """

    def init_menu(self):
        try:
            text_ = ''
            welcome_file = open('./welcome_view.txt', 'r')
            lines_ = welcome_file.readlines()
            for line_ in lines_:
                text_ = text_ + line_
            welcome_file.close()
        except:
            text_ = ''
        self.setCentralWidget(CTNInitWidget(message=text_))

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        import_menu = menu_bar.addMenu('&Import')
        analysis_menu = menu_bar.addMenu('&Analysis')
        export_menu = menu_bar.addMenu('&Export')

        projects_ = QtWidgets.QAction('Projects', self)
        projects_.triggered.connect(self.projects_)
        file_menu.addAction(projects_)

        open_projects = QtWidgets.QAction('Open', self)
        open_projects.triggered.connect(self.open_projects)
        file_menu.addAction(open_projects)

        dump_import = QtWidgets.QAction('Dump', self)
        dump_import.triggered.connect(self.import_dump)
        import_menu.addAction(dump_import)

        dat_import = QtWidgets.QAction('Dat', self)
        dat_import.triggered.connect(self.import_dat)
        import_menu.addAction(dat_import)

        ex_import = QtWidgets.QAction('Existing rev', self)
        ex_import.triggered.connect(self.import_ex)
        import_menu.addAction(ex_import)

        resid_analysis = QtWidgets.QAction('Residuals', self)
        resid_analysis.triggered.connect(self.resid_analysis)
        analysis_menu.addAction(resid_analysis)

        new_p_analysis = QtWidgets.QAction('New points', self)
        new_p_analysis.triggered.connect(self.new_p_analysis)
        analysis_menu.addAction(new_p_analysis)

        change_p_analysis = QtWidgets.QAction('Changed points', self)
        change_p_analysis.triggered.connect(self.change_p_analysis)
        analysis_menu.addAction(change_p_analysis)

        csv_export = QtWidgets.QAction('Export csv', self)
        csv_export.triggered.connect(self.csv_existing_export)
        export_menu.addAction(csv_export)

        self.setGeometry(50, 50, 800, 800)
        self.setWindowTitle('Control Networks')
        self.show()

    """ Connection with --File -> Projects-- widget """

    def projects_(self):
        self.setCentralWidget(CTNProjectWidget())

    """ Connection with --File -> Open-- widget """

    def open_projects(self):
        self.setCentralWidget(CTNOpenWidget())

    """ Connection with --Import -> Dump-- widget """

    def import_dump(self):
        self.setCentralWidget(CTNImportDumpWidget())

    """ Connection with --Import -> Dat-- widget """

    def import_dat(self):
        self.setCentralWidget(CTNImportDatWidget())

    """ Connection with --Import -> Existing-- widget """

    def import_ex(self):
        self.setCentralWidget(CTNImportExistingWidget())

    """ Connection with --Analysis -> Residuals-- widget """

    def resid_analysis(self):
        self.setCentralWidget(CTNAnalysisResidWidget())

    """ Connection with --Analysis -> New Points-- widget """

    def new_p_analysis(self):
        self.setCentralWidget(CTNAnalysisNewPointsWidget())

    """ Connection with --Analysis -> Changed Points-- widget """

    def change_p_analysis(self):
        self.setCentralWidget(CTNAnalysisChangePointsWidget())

    """ Connection with --Export -> Export csv-- widget """

    def csv_existing_export(self):
        self.setCentralWidget(CTNExportExistingWidget())

