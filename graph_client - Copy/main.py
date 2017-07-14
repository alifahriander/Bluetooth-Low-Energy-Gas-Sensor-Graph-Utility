# Python Modules
import sys

# Developer Modules 
from graph_widget import *

if __name__ == '__main__':

    app = QApplication(sys.argv)

    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOptions(antialias = True)

    graph_window = Graph_Window()
    graph_window.show_graphs()



    sys.exit(app.exec_())
