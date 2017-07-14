#######################################################################
# Writen by: Derek Santos
#######################################################################

# 3rd Party Modules
import pyqtgraph as pg
from pyqtgraph import GraphicsLayoutWidget
from pyqtgraph.Qt import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QFont, QFileDialog

# Python Modules
import sys
from config import *
from time import time

# Developer Modules
from graph_widget_threads import *

def SELECT_LATEST_FILE(directory = LOCAL_DIRECTORY_OF_SENSOR_DATA):
    latest_time = None
    latest_path = None
    first_loop = True
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            current_time = os.stat(file_path)
            if not first_loop and int(current_time.st_mtime) > int(latest_time.st_mtime):
                latest_time = os.stat(file_path)
                latest_path = file_path
            elif first_loop:
                latest_time = os.stat(file_path)
                latest_path = file_path
                first_loop = False
    return latest_path

class Graph_Window(GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()

        a = QPushButton('Open CSV', self)
        a.resize(100, 50)
        a.clicked.connect(self.select_file)

        b = QPushButton('Attempt Connection', self)
        b.resize(150, 50)
        b.clicked.connect(self.attempt_to_connect)
        b.move(115, 0)

        self.resize (1920, 1080)

        ########################################################################
        # Init of linear region that can control all graphs at once
        ########################################################################
        self.linear_region = pg.LinearRegionItem([0,3000])
        self.linear_region.setZValue(-10)

        ########################################################################
        # Init of all plot widgets
        ########################################################################

        self.frequency_resistance_plot_graph   = self.addPlot(title = 'Frequency')
        self.frequency_resistance_legend = self.frequency_resistance_plot_graph.addLegend()

        self.nextRow()
        self.temperature_plot_graph = self.addPlot(title = 'Temperature')
        self.nextRow()
        self.pressure_plot_graph    = self.addPlot(title = 'Pressure')
        self.nextRow()
        self.humidity_plot_graph    = self.addPlot(title = 'Humidity')
        self.nextRow()
        self.overview_graph    = self.addPlot(title = 'Overview Graph')
        self.overview_graph.addItem(self.linear_region)

        self.frequency_resistance_plot_graph.showGrid  (x = True, y = True)
        self.temperature_plot_graph.showGrid(x = True, y = True)
        self.pressure_plot_graph.showGrid   (x = True, y = True)
        self.humidity_plot_graph.showGrid   (x = True, y = True)
        self.overview_graph.showGrid   (x = True, y = True)

        self.frequency_resistance_plot_graph.sigXRangeChanged.connect  (self.update_frequency_region)
        self.temperature_plot_graph.sigXRangeChanged.connect(self.update_temperature_region)
        self.pressure_plot_graph.sigXRangeChanged.connect   (self.update_pressure_region)
        self.humidity_plot_graph.sigXRangeChanged.connect   (self.update_humidity_region)

        self.frequency_lines = []

        for position in range(0, len(DICTIONARY_OF_CHANNEL_KEYS.keys())):

            self.frequency_lines.append( self.frequency_resistance_plot_graph.plot(x=[],
                                             y=[],
                                             pen = pg.mkPen(cosmetic = True, width = LINE_THICKNESS, color = LINE_COLORS[position]),
                                             symbol = 'o',
                                             name = 'Channel %d' % position))

        #for curve in self.frequency_lines:
        #    self.frequency_resistance_plot_graph.addItem(curve)


        self.resistance_line = self.frequency_resistance_plot_graph.plot(x=[],
                                 y=[],
                                 pen = pg.mkPen(cosmetic = True, width = LINE_THICKNESS, color = LINE_COLORS[position]),
                                 symbol = 'o',
                                 name = 'Resistance')
        #self.frequency_resistance_plot_graph.addItem(self.resistance_line)

        self.temperature_line = self.temperature_plot_graph.plot(x=[],
                                         y=[],
                                         pen = pg.mkPen(cosmetic = True, width = LINE_THICKNESS, color = LINE_COLORS[1]),
                                         symbol = 'o',
                                         name = 'Temperature')
        self.pressure_line = self.pressure_plot_graph.plot(x=[],
                                         y=[],
                                         pen = pg.mkPen(cosmetic = True, width = LINE_THICKNESS, color = LINE_COLORS[2]),
                                         symbol = 'o',
                                         name = 'Pressure')
        self.humidity_line = self.humidity_plot_graph.plot(x=[],
                                         y=[],
                                         pen = pg.mkPen(cosmetic = True, width = LINE_THICKNESS, color = LINE_COLORS[3]),
                                         symbol = 'o',
                                         name = 'Humidity')

        self.linear_region.sigRegionChanged.connect(self.update_plots_using_region)


        self.file_path = SELECT_LATEST_FILE()

        ########################################################################
        # Data Processing Thread
        ########################################################################
        self.server_handler = Server_Handler(self)
        self.server_handler.start()

        self.process_data_thread = Data_Processing_Stream_Thread(self)
        self.process_data_thread.start()



        ########################################################################
        # Timers
        ########################################################################
        self.plot_timer_frequency_resistance = QtCore.QTimer()
        self.plot_timer_frequency_resistance.timeout.connect(self.plot_frequency_or_resistance_data)
        self.plot_timer_frequency_resistance.start(1000)

        self.plot_timer_temperature = QtCore.QTimer()
        self.plot_timer_temperature.timeout.connect(self.plot_temperature_data)
        self.plot_timer_temperature.start(1000)

        self.plot_timer_pressure = QtCore.QTimer()
        self.plot_timer_pressure.timeout.connect(self.plot_pressure_data)
        self.plot_timer_pressure.start(1000)

        self.plot_timer_humidity = QtCore.QTimer()
        self.plot_timer_humidity.timeout.connect(self.plot_humidity_data)
        self.plot_timer_humidity.start(1000)

    def select_file(self):
        new_file_path = QFileDialog.getOpenFileName()[0]
        if not new_file_path == '' and new_file_path[-len('.csv'):] == '.csv':
            self.clear_all_plots()
            self.file_path = new_file_path

    def clear_all_plots(self):
        for curve in self.frequency_lines:
            curve.clear()

        self.resistance_line.clear()

    def attempt_to_connect(self):
        if self.server_handler.attempt_connection:
            self.server_handler.attempt_connection = False
        else:
            self.server_handler.attempt_connection = True

    def plot_frequency_or_resistance_data(self):
        try:

            if self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
                if not self.process_data_thread.frequency_queue.empty():
                    self.frequency_resistance_plot_graph.setTitle ('Resonant Frequency')
                    self.frequency_resistance_plot_graph.setLabel ('left', 'Frequency (MHz)')
                    self.frequency_resistance_plot_graph.setLabel ('bottom', 'Time (s)')
                    self.plot_frequency_data()

            elif self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
                if not self.process_data_thread.resistance_queue.empty():
                    self.frequency_resistance_plot_graph.setTitle ('Resistance')
                    self.frequency_resistance_plot_graph.setLabel ('left', 'Resistance (Ohms)')
                    self.frequency_resistance_plot_graph.setLabel ('bottom', 'Time (s)')
                    self.plot_resistance_data()

        except Exception as e:
            print ('ERROR: Plot frequency / resistance data:', e)

    def plot_frequency_data(self):

        directory_of_frequency_channels = self.process_data_thread.get_frequency_data()
        sorted_keys = sorted_keys = sorted(directory_of_frequency_channels.keys())

        for position, key in enumerate(sorted_keys):
            self.frequency_lines[position].setData(x = directory_of_frequency_channels[key]['x'], y = directory_of_frequency_channels[key]['y'])

    def plot_resistance_data(self):
        time_duration_list, resistance_list = self.process_data_thread.get_resistance_data()

        self.resistance_line.setData(x = time_duration_list, y = resistance_list)

    def plot_temperature_data(self):
        self.temperature_plot_graph.setLabel ('left', 'Temperature (C)')
        self.temperature_plot_graph.setLabel ('bottom', 'Time (S)')

        self.temperature_line.setData(*self.process_data_thread.get_temperature_data())


    def plot_pressure_data(self):
        self.pressure_plot_graph.setLabel ('left', 'Pa')
        self.pressure_plot_graph.setLabel ('bottom', 'Time (S)')

        self.pressure_line.setData(*self.process_data_thread.get_pressure_data())

    def plot_humidity_data(self):
        self.humidity_plot_graph.setLabel ('left', '% Rh')
        self.humidity_plot_graph.setLabel ('bottom', 'Time (S)')

        self.humidity_line.setData(*self.process_data_thread.get_humidity_data())

    # When the region changes then this function will change the plots accordingly
    def update_plots_using_region(self):
        self.frequency_resistance_plot_graph.setXRange  (*self.linear_region.getRegion(), padding = 0)
        self.temperature_plot_graph.setXRange(*self.linear_region.getRegion(), padding = 0)
        self.pressure_plot_graph.setXRange   (*self.linear_region.getRegion(), padding = 0)
        self.humidity_plot_graph.setXRange   (*self.linear_region.getRegion(), padding = 0)

    def update_frequency_region(self):
        self.linear_region.setRegion(self.frequency_resistance_plot_graph.getViewBox().viewRange()[0])

    def update_temperature_region(self):
        self.linear_region.setRegion(self.temperature_plot_graph.getViewBox().viewRange()[0])

    def update_pressure_region(self):
        self.linear_region.setRegion(self.pressure_plot_graph.getViewBox().viewRange()[0])

    def update_humidity_region(self):
        self.linear_region.setRegion(self.humidity_plot_graph.getViewBox().viewRange()[0])

    def show_graphs(self):
        self.frequency_resistance_plot_graph.show()
        self.temperature_plot_graph.show()
        self.pressure_plot_graph.show()
        self.humidity_plot_graph.show()
        self.overview_graph.show()

        self.show()
