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

def SELECT_LATEST_FILE_FREQUENCY_RESISTANCE(directory = LOCAL_DIRECTORY_OF_SENSOR_DATA):
    latest_time = None
    latest_path = None
    first_loop = True
    for file_name in os.listdir(directory):
        file_path_frequency_resistance = os.path.join(directory, file_name)
        if os.path.isfile(file_path_frequency_resistance):
            current_time = os.stat(file_path_frequency_resistance)
            if not first_loop and int(current_time.st_mtime) > int(latest_time.st_mtime) and \
                (file_path_frequency_resistance[-len('Frequency.csv'):] == 'Frequency.csv' or \
                file_path_frequency_resistance[-len('Resistance.csv'):] == 'Resistance.csv'):
                latest_time = os.stat(file_path_frequency_resistance)
                latest_path = file_path_frequency_resistance
            elif first_loop:
                latest_time = os.stat(file_path_frequency_resistance)
                latest_path = file_path_frequency_resistance
                first_loop = False
    return latest_path

def SELECT_LATEST_FILE_ENVIRONMENT(directory = LOCAL_DIRECTORY_OF_SENSOR_DATA):
    latest_time = None
    latest_path = None
    first_loop = True
    for file_name in os.listdir(directory):
        file_path_environment = os.path.join(directory, file_name)
        if os.path.isfile(file_path_environment):
            current_time = os.stat(file_path_environment)
            if not first_loop and int(current_time.st_mtime) > int(latest_time.st_mtime) and \
                file_path_environment[-len('Environment.csv'):] == 'Environment.csv':
                latest_time = os.stat(file_path_environment)
                latest_path = file_path_environment
            elif first_loop:
                latest_time = os.stat(file_path_environment)
                latest_path = file_path_environment
                first_loop = False
    return latest_path

class Graph_Window(GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()

        self.resize (1920, 1080)

        button_width = 19

        ########################################################################
        # File Manipulation Buttons
        ########################################################################

        open_frequency_resistance_file_button = QPushButton('Open Frequency CSV', self)
        open_frequency_resistance_file_button.resize(160, button_width)
        open_frequency_resistance_file_button.clicked.connect(self.select_file_frequency_resistance)

        open_environment_file_button = QPushButton('Open Environment CSV', self)
        open_environment_file_button.resize(180, button_width)
        open_environment_file_button.clicked.connect(self.select_file_environment)
        open_environment_file_button.move(160, 0)

        ########################################################################
        # Attempt Connection Buttons
        ########################################################################

        attempt_connection_button = QPushButton('Attempt Connection', self)
        attempt_connection_button.resize(150, button_width)
        attempt_connection_button.clicked.connect(self.attempt_to_connect)
        attempt_connection_button.move(340, 0)

        ########################################################################
        # Plot Channel Plotting Booleans
        ########################################################################
        self.plot_channel_one   = True
        self.plot_channel_two   = True
        self.plot_channel_three = True
        self.plot_channel_four  = True
        self.plot_channel_five  = True
        self.plot_channel_six   = True
        self.plot_channel_seven = True
        self.plot_channel_eight = True

        # The position of this list corispond to the position of the sorted directory_of_frequency_channels keys
        self.plot_channel_key_booleans = []
        for count in range( len(DICTIONARY_OF_CHANNEL_KEYS.keys()) ):
            self.plot_channel_key_booleans.append(True)


        ########################################################################
        # Graph Channel Buttons
        ########################################################################

        channel_button_x_location_start = 490
        length_of_button = 100
        graph_channel_one_button = QPushButton('Graph Channel 0', self)
        graph_channel_one_button.resize(length_of_button, button_width)
        graph_channel_one_button.clicked.connect(self.switch_frequency_plot_channel_one)
        graph_channel_one_button.move(channel_button_x_location_start, 0)
        graph_channel_one_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[0]))


        channel_button_x_location_start += length_of_button
        graph_channel_two_button = QPushButton('Graph Channel 1', self)
        graph_channel_two_button.resize(length_of_button, button_width)
        graph_channel_two_button.clicked.connect(self.switch_frequency_plot_channel_two)
        graph_channel_two_button.move(channel_button_x_location_start, 0)
        graph_channel_two_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[1]))


        channel_button_x_location_start += length_of_button
        graph_channel_three_button = QPushButton('Graph Channel 2', self)
        graph_channel_three_button.resize(length_of_button, button_width)
        graph_channel_three_button.clicked.connect(self.switch_frequency_plot_channel_three)
        graph_channel_three_button.move(channel_button_x_location_start, 0)
        graph_channel_three_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[2]))


        channel_button_x_location_start += length_of_button
        graph_channel_four_button = QPushButton('Graph Channel 3', self)
        graph_channel_four_button.resize(length_of_button, button_width)
        graph_channel_four_button.clicked.connect(self.switch_frequency_plot_channel_four)
        graph_channel_four_button.move(channel_button_x_location_start, 0)
        graph_channel_four_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[3]))


        channel_button_x_location_start += length_of_button
        graph_channel_five_button = QPushButton('Graph Channel 4', self)
        graph_channel_five_button.resize(length_of_button, button_width)
        graph_channel_five_button.clicked.connect(self.switch_frequency_plot_channel_five)
        graph_channel_five_button.move(channel_button_x_location_start, 0)
        graph_channel_five_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[4]))


        channel_button_x_location_start += length_of_button
        graph_channel_six_button = QPushButton('Graph Channel 5', self)
        graph_channel_six_button.resize(length_of_button, button_width)
        graph_channel_six_button.clicked.connect(self.switch_frequency_plot_channel_six)
        graph_channel_six_button.move(channel_button_x_location_start, 0)
        graph_channel_six_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[5]))


        channel_button_x_location_start += length_of_button
        graph_channel_seven_button = QPushButton('Graph Channel 6', self)
        graph_channel_seven_button.resize(length_of_button, button_width)
        graph_channel_seven_button.clicked.connect(self.switch_frequency_plot_channel_seven)
        graph_channel_seven_button.move(channel_button_x_location_start, 0)
        graph_channel_seven_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[6]))


        channel_button_x_location_start += length_of_button
        graph_channel_eight_button = QPushButton('Graph Channel 7', self)
        graph_channel_eight_button.resize(length_of_button, button_width)
        graph_channel_eight_button.clicked.connect(self.switch_frequency_plot_channel_eight)
        graph_channel_eight_button.move(channel_button_x_location_start, 0)
        graph_channel_eight_button.setStyleSheet("background-color:rgb(%d,%d,%d)" % (LINE_COLORS[7]))




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

        self.frequency_resistance_plot_graph.showGrid  (x = True, y = True)
        self.temperature_plot_graph.showGrid(x = True, y = True)
        self.pressure_plot_graph.showGrid   (x = True, y = True)
        self.humidity_plot_graph.showGrid   (x = True, y = True)

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
                                             symbolBrush = pg.mkBrush(LINE_COLORS[position]),
                                             name = 'Channel %d' % position))

        self.resistance_line = self.frequency_resistance_plot_graph.plot(x=[],
                                         y=[],
                                         pen = pg.mkPen(cosmetic = True, width = LINE_THICKNESS, color = LINE_COLORS[position]),
                                         symbol = 'o',
                                         name = 'Resistance')

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

        self.file_path_frequency_resistance = SELECT_LATEST_FILE_FREQUENCY_RESISTANCE()
        #self.file_path_environment = LOCAL_DIRECTORY_OF_SENSOR_DATA + 'E7_3A_23_33_CD_A5 - Fri Jul 14 16_58_43 2017 - Environment.csv'
        self.file_path_environment = SELECT_LATEST_FILE_ENVIRONMENT()

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

    def select_file_frequency_resistance(self):
        new_file_path_frequency_resistance = QFileDialog.getOpenFileName()[0]
        if not new_file_path_frequency_resistance == '' and new_file_path_frequency_resistance[-len('.csv'):] == '.csv':
            self.clear_all_plots()
            self.file_path_frequency_resistance = new_file_path_frequency_resistance

    def select_file_environment(self):
        new_file_path_environment = QFileDialog.getOpenFileName()[0]
        if not new_file_path_environment == '' and new_file_path_environment[-len('.csv'):] == '.csv':
            self.clear_all_plots()
            self.file_path_frequency_resistance = new_file_path_environment

    def switch_frequency_plot_channel_one(self):
        if self.plot_channel_key_booleans[0]:
            self.plot_channel_key_booleans[0] = False
        else:
            self.plot_channel_key_booleans[0]  = True

    def switch_frequency_plot_channel_two(self):
        if self.plot_channel_key_booleans[1]:
            self.plot_channel_key_booleans[1] = False
        else:
            self.plot_channel_key_booleans[1]  = True

    def switch_frequency_plot_channel_three(self):
        if self.plot_channel_key_booleans[2]:
            self.plot_channel_key_booleans[2] = False
        else:
            self.plot_channel_key_booleans[2]  = True

    def switch_frequency_plot_channel_four(self):
        if self.plot_channel_key_booleans[3]:
            self.plot_channel_key_booleans[3] = False
        else:
            self.plot_channel_key_booleans[3]  = True

    def switch_frequency_plot_channel_five(self):
        if self.plot_channel_key_booleans[4]:
            self.plot_channel_key_booleans[4] = False
        else:
            self.plot_channel_key_booleans[4]  = True

    def switch_frequency_plot_channel_six(self):
        if self.plot_channel_key_booleans[5]:
            self.plot_channel_key_booleans[5] = False
        else:
            self.plot_channel_key_booleans[5]  = True

    def switch_frequency_plot_channel_seven(self):
        if self.plot_channel_key_booleans[6]:
            self.plot_channel_key_booleans[6] = False
        else:
            self.plot_channel_key_booleans[6]  = True

    def switch_frequency_plot_channel_eight(self):
        if self.plot_channel_key_booleans[7]:
            self.plot_channel_key_booleans[7] = False
        else:
            self.plot_channel_key_booleans[7]  = True

    def clear_all_plots(self):
        for curve in self.frequency_lines:
            curve.clear()

        self.resistance_line.clear()
        self.temperature_line.clear()
        self.pressure_line.clear()
        self.humidity_line.clear()

    def attempt_to_connect(self):
        if self.server_handler.attempt_connection:
            self.server_handler.attempt_connection = False
        else:
            self.server_handler.attempt_connection = True

    def plot_frequency_or_resistance_data(self):
        try:
            if self.file_path_frequency_resistance is None:
                return

            if self.file_path_frequency_resistance[-len('Frequency.csv'):] == 'Frequency.csv':
                if not self.process_data_thread.frequency_queue.empty():
                    self.frequency_resistance_plot_graph.setTitle ('Resonant Frequency')
                    self.frequency_resistance_plot_graph.setLabel ('left', 'Frequency (MHz)')
                    self.frequency_resistance_plot_graph.setLabel ('bottom', 'Time (s)')
                    self.plot_frequency_data()

            elif self.file_path_frequency_resistance[-len('Resistance.csv'):] == 'Resistance.csv':
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
            if self.plot_channel_key_booleans[position]:
                self.frequency_lines[position].setData(x = directory_of_frequency_channels[key]['x'], y = directory_of_frequency_channels[key]['y'])
            else:
                self.frequency_lines[position].setData([],[])

    def plot_resistance_data(self):
        time_duration_list, resistance_list = self.process_data_thread.get_resistance_data()

        self.resistance_line.setData(x = time_duration_list, y = resistance_list)

    def plot_temperature_data(self):
        self.temperature_plot_graph.setLabel ('left', 'Temperature (C)')
        self.temperature_plot_graph.setLabel ('bottom', 'Time (S)')
        if not self.process_data_thread.temperature_queue.empty():
            self.temperature_line.setData(*self.process_data_thread.get_temperature_data())


    def plot_pressure_data(self):
        self.pressure_plot_graph.setLabel ('left', 'Pa')
        self.pressure_plot_graph.setLabel ('bottom', 'Time (S)')

        if not self.process_data_thread.pressure_queue.empty():
            self.pressure_line.setData(*self.process_data_thread.get_pressure_data())

    def plot_humidity_data(self):
        self.humidity_plot_graph.setLabel ('left', '% Rh')
        self.humidity_plot_graph.setLabel ('bottom', 'Time (S)')


        if not self.process_data_thread.humidity_queue.empty():
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
        #self.overview_graph.show()

        self.show()
