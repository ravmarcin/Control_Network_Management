from PyQt5 import QtWidgets

""" Starting Widget'"""


class CTNInitWidget(QtWidgets.QWidget):

    def __init__(self, message=None):
        """ Constructor """

        super().__init__()
        self.message = message
        self.init_ui(self.message)

    """ Widget view """

    def init_ui(self, message):
        status_toolbar = QtWidgets.QTextEdit()
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(status_toolbar, 1, 1, 5, 1)
        self.setLayout(grid)
        status_toolbar.setText(str(message))
        self.show()