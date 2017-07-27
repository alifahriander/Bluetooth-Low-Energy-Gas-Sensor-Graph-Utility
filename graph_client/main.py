# Python Modules
import sys

# Developer Modules
from graph_widget import *
from config import ANTIALIAS


def main():
    app = QApplication(sys.argv)

    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOptions(antialias=ANTIALIAS)

    graph_window = Main_Widget()
    graph_window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
