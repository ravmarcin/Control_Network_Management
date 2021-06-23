from PyQt5 import QtWidgets
import sys
from CTNgui import *

''' Application initialization '''
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = CTNgui()
    sys.exit(app.exec_())
