import sys
import pyqtgraph as pg
from pyqtgraph import GraphicsWindow
from pyqtgraph.Qt import QtCore
from PyQt5.QtWidgets import QApplication, QWidget

from random import randint

STARTING_X = 0

def update_data():
    with open('cool.txt', 'r') as current_file:
        data = current_file.read().split('\n')

    return data



class Graph_Window(GraphicsWindow):
    def __init__(self):
        super().__init__('Title')

        self.resize (1280, 720)

        ########################################################################
        # Init of linear region that can control all graphs at once
        ########################################################################
        self.linear_region = pg.LinearRegionItem([0,200])
        self.linear_region.setZValue(-10)

        ########################################################################
        # Init of all plot widgets
        ########################################################################

        self.frequency_plot_graph   = self.addPlot(title = 'Frequency')
        self.nextRow()
        self.temperature_plot_graph = self.addPlot(title = 'Temperature')
        self.nextRow()
        self.pressure_plot_graph    = self.addPlot(title = 'Pressure')
        self.nextRow()
        self.humidity_plot_graph    = self.addPlot(title = 'Humidity')
        self.nextRow()
        self.overview_graph         = self.addPlot(title = 'Overview Graph')

        self.frequency_plot_graph.showGrid  (x = True, y = True)
        self.temperature_plot_graph.showGrid(x = True, y = True)
        self.pressure_plot_graph.showGrid   (x = True, y = True)
        self.humidity_plot_graph.showGrid   (x = True, y = True)
        self.overview_graph.showGrid        (x = True, y = True)


        self.frequency_plot_graph.sigXRangeChanged.connect  (self.update_frequency_region)
        self.temperature_plot_graph.sigXRangeChanged.connect(self.update_temperature_region)
        self.pressure_plot_graph.sigXRangeChanged.connect   (self.update_pressure_region)
        self.humidity_plot_graph.sigXRangeChanged.connect   (self.update_humidity_region)

        self.overview_graph.addItem(self.linear_region)

        pg.setConfigOptions(antialias = True)

        self.xs = []
        self.ys = []

        self.starting_x = 0

        self.linear_region.sigRegionChanged.connect(self.update_plots_using_region)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.plot_random)
        self.timer.start(1)





    def plot_random(self):
        self.starting_x += 1
        self.xs.append(self.starting_x)
        self.ys.append(randint(0, 100))

        self.frequency_plot_graph.clear()
        self.temperature_plot_graph.clear()
        self.pressure_plot_graph.clear()
        self.humidity_plot_graph.clear()
        self.overview_graph.clear()

        self.frequency_plot_graph.plot(x = self.xs, y = self.ys, pen = (255, 0, 0), symbolPen = 'w')
        self.temperature_plot_graph.plot(x = self.xs, y = self.ys, pen = (255, 0, 0), symbolPen = 'w')
        self.pressure_plot_graph.plot(x = self.xs, y = self.ys, pen = (255, 0, 0), symbolPen = 'w')
        self.humidity_plot_graph.plot(x = self.xs, y = self.ys, pen = (255, 0, 0), symbolPen = 'w')
        self.overview_graph.plot(x = self.xs, y = self.ys, pen = (255, 0, 0), symbolPen = 'w')
        self.overview_graph.addItem(self.linear_region)


        if self.starting_x <= 10:
            self.overview_graph.enableAutoRange('xy', False)

    # When the region changes then this function will change the plots accordingly
    def update_plots_using_region(self):
        self.frequency_plot_graph.setXRange(*self.linear_region.getRegion(), padding = 0)
        self.temperature_plot_graph.setXRange(*self.linear_region.getRegion(), padding = 0)
        self.pressure_plot_graph.setXRange(*self.linear_region.getRegion(), padding = 0)
        self.humidity_plot_graph.setXRange(*self.linear_region.getRegion(), padding = 0)
        #self.overview_graph.setXRange(*self.linear_region.getRegion(), padding = 0)

    def update_frequency_region(self):
        self.linear_region.setRegion(self.frequency_plot_graph.getViewBox().viewRange()[0])

    def update_temperature_region(self):
        self.linear_region.setRegion(self.temperature_plot_graph.getViewBox().viewRange()[0])

    def update_pressure_region(self):
        self.linear_region.setRegion(self.pressure_plot_graph.getViewBox().viewRange()[0])

    def update_humidity_region(self):
        self.linear_region.setRegion(self.humidity_plot_graph.getViewBox().viewRange()[0])



    def show_graphs(self):
        self.frequency_plot_graph.show()
        self.temperature_plot_graph.show()
        self.pressure_plot_graph.show()
        self.humidity_plot_graph.show()
        self.overview_graph.show()

        self.show()



if __name__ == '__main__':

    app = QApplication(sys.argv)

    graph_window = Graph_Window()
    graph_window.show_graphs()

    sys.exit(app.exec_())
