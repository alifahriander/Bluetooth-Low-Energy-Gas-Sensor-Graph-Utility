#######################################################################
# Writen by: Derek Santos
#######################################################################

# 3rd Party Modules
import pyqtgraph as pg
from pyqtgraph import GraphicsLayoutWidget, PlotWidget
from pyqtgraph.Qt import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QFont, QFileDialog

# Python Modules
import sys
from config import *
from time import time

# Developer Modules
from graph_widget_threads import *


def SELECT_LATEST_FILE_JSON(directory=LOCAL_DIRECTORY_OF_SENSOR_DATA):
    """ Gets the latest JSON file with a directory """
    latest_time = None
    latest_path = None
    first_loop = True
    for file_name in os.listdir(directory):
        file_path_json = os.path.join(directory, file_name)
        if os.path.isfile(file_path_json):
            current_time = os.stat(file_path_json)
            if not first_loop and int(current_time.st_mtime) > int(latest_time.st_mtime) and \
                    file_path_json[-len('.json'):] == '.json':
                latest_time = os.stat(file_path_json)
                latest_path = file_path_json
            elif first_loop:
                latest_time = os.stat(file_path_json)
                latest_path = file_path_json
                first_loop = False
    return latest_path


class Graph_Window(GraphicsLayoutWidget):
    def __init__(self, parent_widget):
        GraphicsLayoutWidget.__init__(self, parent_widget)
        self.parent_widget = parent_widget

        self.resize(1920, 1080)

        button_width = 19

        #######################################################################
        # Plot Channel Plotting Booleans
        #######################################################################

        self.plot_channel_one = True
        self.plot_channel_two = True
        self.plot_channel_three = True
        self.plot_channel_four = True
        self.plot_channel_five = True
        self.plot_channel_six = True
        self.plot_channel_seven = True
        self.plot_channel_eight = True

        # The position of this list corispond to the position of the sorted directory_of_frequency_channels keys
        self.plot_channel_key_booleans = [
            True for count in range(len(DICTIONARY_OF_CHANNEL_KEYS.keys()))]

        #######################################################################
        # Init of linear region that can control all graphs at once
        #######################################################################
        self.linear_region = pg.LinearRegionItem([0, 3000])
        self.linear_region.setZValue(-10)

        #######################################################################
        # Init of all plot widgets
        #######################################################################

        self.frequency_plot_graph = self.addPlot(title='Frequency')
        if ADD_FREQUENCY_LEGEND:
            self.frequency_resistance_legend = self.frequency_plot_graph.addLegend()
        self.nextRow()

        self.resistance_graph = self.addPlot(title='Resistance')
        self.nextRow()

        self.temperature_plot_graph = self.addPlot(title='Temperature')
        self.nextRow()

        self.pressure_plot_graph = self.addPlot(title='Pressure')
        self.nextRow()

        self.humidity_plot_graph = self.addPlot(title='Humidity')
        self.nextRow()

        self.overview_graph = self.addPlot(title='Overview')
        self.overview_graph.addItem(self.linear_region)

        self.frequency_plot_graph.showGrid(x=True, y=True)
        self.resistance_graph.showGrid(x=True, y=True)
        self.temperature_plot_graph.showGrid(x=True, y=True)
        self.pressure_plot_graph.showGrid(x=True, y=True)
        self.humidity_plot_graph.showGrid(x=True, y=True)
        self.overview_graph.showGrid(x=True, y=True)

        self.frequency_plot_graph.sigXRangeChanged.connect(
            self.update_frequency_region)
        self.resistance_graph.sigXRangeChanged.connect(
            self.update_resistance_region)
        self.temperature_plot_graph.sigXRangeChanged.connect(
            self.update_temperature_region)
        self.pressure_plot_graph.sigXRangeChanged.connect(
            self.update_pressure_region)
        self.humidity_plot_graph.sigXRangeChanged.connect(
            self.update_humidity_region)

        self.frequency_lines = []

        for position in range(0, len(DICTIONARY_OF_CHANNEL_KEYS.keys())):
            self.frequency_lines.append(self.frequency_plot_graph.plot(x=[],
                                                                       y=[],
                                                                       pen=pg.mkPen(cosmetic=True, width=LINE_THICKNESS,
                                                                                    color=LINE_COLORS[position]),
                                                                       symbol='o',
                                                                       symbolBrush=pg.mkBrush(
                                                                           LINE_COLORS[position]),
                                                                       name='Channel %d' % position))

        self.resistance_line = self.resistance_graph.plot(x=[],
                                                          y=[],
                                                          pen=pg.mkPen(cosmetic=True, width=LINE_THICKNESS,
                                                                       color=LINE_COLORS[0]),
                                                          symbol='o',
                                                          symbolBrush=pg.mkBrush(
                                                              LINE_COLORS[0]),
                                                          name='Resistance')

        self.temperature_line = self.temperature_plot_graph.plot(x=[],
                                                                 y=[],
                                                                 pen=pg.mkPen(cosmetic=True, width=LINE_THICKNESS,
                                                                              color=LINE_COLORS[1]),
                                                                 symbol='o',
                                                                 symbolBrush=pg.mkBrush(
                                                                     LINE_COLORS[1]),
                                                                 name='Temperature')
        self.pressure_line = self.pressure_plot_graph.plot(x=[],
                                                           y=[],
                                                           pen=pg.mkPen(cosmetic=True, width=LINE_THICKNESS,
                                                                        color=LINE_COLORS[2]),
                                                           symbol='o',
                                                           symbolBrush=pg.mkBrush(
                                                               LINE_COLORS[2]),
                                                           name='Pressure')
        self.humidity_line = self.humidity_plot_graph.plot(x=[],
                                                           y=[],
                                                           pen=pg.mkPen(cosmetic=True, width=LINE_THICKNESS,
                                                                        color=LINE_COLORS[3]),
                                                           symbol='o',
                                                           symbolBrush=pg.mkBrush(
                                                               LINE_COLORS[3]),
                                                           name='Humidity')

        self.linear_region.sigRegionChanged.connect(
            self.update_plots_using_region)

        self.resistance_json_path = None
        self.file_path_json = SELECT_LATEST_FILE_JSON()

        #######################################################################
        # Data Processing Thread
        #######################################################################
        self.server_handler = Server_Handler(
            self, self.parent_widget.attempt_connection_button)
        self.server_handler.start()

        self.process_data_thread = Data_Processing_Stream_Thread(self)
        self.process_data_thread.start()

        #######################################################################
        # Timers
        #######################################################################
        self.plot_timer_frequency = QtCore.QTimer()
        self.plot_timer_frequency.timeout.connect(self.plot_frequency_data)
        self.plot_timer_frequency.start(1000)

        self.plot_timer_resistance = QtCore.QTimer()
        self.plot_timer_resistance.timeout.connect(self.plot_resistance_data)
        self.plot_timer_resistance.start(1000)

        self.plot_timer_temperature = QtCore.QTimer()
        self.plot_timer_temperature.timeout.connect(self.plot_temperature_data)
        self.plot_timer_temperature.start(1000)

        self.plot_timer_pressure = QtCore.QTimer()
        self.plot_timer_pressure.timeout.connect(self.plot_pressure_data)
        self.plot_timer_pressure.start(1000)

        self.plot_timer_humidity = QtCore.QTimer()
        self.plot_timer_humidity.timeout.connect(self.plot_humidity_data)
        self.plot_timer_humidity.start(1000)

    def download_all_files(self):
        """ Get sensor data from server when button is pressed """
        self.server_handler.get_sensor_data_from_server()

    def select_json_file(self):
        """ Selects a json file to parse overall data from """
        new_file_path_json = QFileDialog.getOpenFileName()[0]
        if not new_file_path_json == '' and new_file_path_json[-len('.json'):] == '.json':
            self.clear_all_plots()
            self.file_path_json = new_file_path_json
            self.resistance_json_path = None

    def select_resistance_json_file(self):
        """ Selects a json file to parse the resitance from """
        new_file_path_json = QFileDialog.getOpenFileName()[0]
        if not new_file_path_json == '' and new_file_path_json[-len('.json'):] == '.json':
            self.resistance_line.clear()
            self.resistance_json_path = new_file_path_json

    def switch_frequency_plot_channel_one(self):
        """ Plot Channel One Toogle """
        if self.plot_channel_key_booleans[0]:
            self.plot_channel_key_booleans[0] = False
            self.parent_widget.graph_channel_one_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))

        else:
            self.plot_channel_key_booleans[0] = True
            self.parent_widget.graph_channel_one_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[0]))

    def switch_frequency_plot_channel_two(self):
        """ Plot Channel Two Toogle """
        if self.plot_channel_key_booleans[1]:
            self.plot_channel_key_booleans[1] = False
            self.parent_widget.graph_channel_two_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))
        else:
            self.plot_channel_key_booleans[1] = True
            self.parent_widget.graph_channel_two_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[1]))

    def switch_frequency_plot_channel_three(self):
        """ Plot channel three toogle """
        if self.plot_channel_key_booleans[2]:
            self.plot_channel_key_booleans[2] = False
            self.parent_widget.graph_channel_three_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))

        else:
            self.plot_channel_key_booleans[2] = True
            self.parent_widget.graph_channel_three_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[2]))

    def switch_frequency_plot_channel_four(self):
        """ Plot channel four toogle """
        if self.plot_channel_key_booleans[3]:
            self.plot_channel_key_booleans[3] = False
            self.parent_widget.graph_channel_four_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))
        else:
            self.plot_channel_key_booleans[3] = True
            self.parent_widget.graph_channel_four_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[3]))

    def switch_frequency_plot_channel_five(self):
        """ Plot channel five toogle """
        if self.plot_channel_key_booleans[4]:
            self.plot_channel_key_booleans[4] = False
            self.parent_widget.graph_channel_five_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))
        else:
            self.plot_channel_key_booleans[4] = True
            self.parent_widget.graph_channel_five_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[4]))

    def switch_frequency_plot_channel_six(self):
        """ Plot channel six toogle """
        if self.plot_channel_key_booleans[5]:
            self.plot_channel_key_booleans[5] = False
            self.parent_widget.graph_channel_six_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))
        else:
            self.plot_channel_key_booleans[5] = True
            self.parent_widget.graph_channel_six_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[5]))

    def switch_frequency_plot_channel_seven(self):
        """ Plot channel seven toogle """
        if self.plot_channel_key_booleans[6]:
            self.plot_channel_key_booleans[6] = False
            self.parent_widget.graph_channel_seven_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))
        else:
            self.plot_channel_key_booleans[6] = True
            self.parent_widget.graph_channel_seven_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[6]))

    def switch_frequency_plot_channel_eight(self):
        """ Plot channel eight toogle """
        if self.plot_channel_key_booleans[7]:
            self.plot_channel_key_booleans[7] = False
            self.parent_widget.graph_channel_eight_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (255, 255, 255))
        else:
            self.plot_channel_key_booleans[7] = True
            self.parent_widget.graph_channel_eight_button.setStyleSheet(
                "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[7]))

    def clear_all_plots(self):
        """ Clears all graphs """
        for curve in self.frequency_lines:
            curve.clear()

        self.resistance_line.clear()
        self.temperature_line.clear()
        self.pressure_line.clear()
        self.humidity_line.clear()

    def attempt_to_connect(self):
        """ Atempt connection to specified server """
        if self.server_handler.attempt_connection:
            self.server_handler.attempt_connection = False
        else:
            self.server_handler.attempt_connection = True

    def plot_frequency_data(self):
        """ Plot frequency data """
        try:
            if self.file_path_json is None:
                return

            if self.process_data_thread.frequency_queue.empty():
                return

            directory_of_frequency_channels = self.process_data_thread.get_frequency_data()
            sorted_keys = sorted(directory_of_frequency_channels.keys())

            for position, key in enumerate(sorted_keys):
                if self.plot_channel_key_booleans[position]:
                    self.frequency_lines[position].setData(x=directory_of_frequency_channels[key]['x'],
                                                           y=directory_of_frequency_channels[key]['y'])
                else:
                    self.frequency_lines[position].setData([], [])
        except Exception as e:
            print(e)

    def plot_resistance_data(self):
        """ Plot resistance data """
        try:
            if self.file_path_json is None:
                return

            if self.process_data_thread.resistance_queue.empty():
                return

            self.resistance_line.setData(
                *self.process_data_thread.get_resistance_data())
        except Exception as e:
            print(e)

    def plot_temperature_data(self):
        """ Plot temperature data """
        try:
            if self.file_path_json is None:
                return

            self.temperature_plot_graph.setLabel('left', 'Temperature (C)')
            self.temperature_plot_graph.setLabel('bottom', 'Time (S)')
            if not self.process_data_thread.temperature_queue.empty():
                self.temperature_line.setData(
                    *self.process_data_thread.get_temperature_data())
        except Exception as e:
            print(e)

    def plot_pressure_data(self):
        """ Plot pressure data """
        try:
            if self.file_path_json is None:
                return

            self.pressure_plot_graph.setLabel('left', 'Pa')
            self.pressure_plot_graph.setLabel('bottom', 'Time (S)')

            if not self.process_data_thread.pressure_queue.empty():
                self.pressure_line.setData(
                    *self.process_data_thread.get_pressure_data())

        except Exception as e:
            print(e)

    def plot_humidity_data(self):
        """ Plot humidity data """
        try:
            if self.file_path_json is None:
                return

            self.humidity_plot_graph.setLabel('left', '% Rh')
            self.humidity_plot_graph.setLabel('bottom', 'Time (S)')

            if not self.process_data_thread.humidity_queue.empty():
                self.humidity_line.setData(
                    *self.process_data_thread.get_humidity_data())
        except Exception as e:
            print(e)

    # When the region changes then this function will change the plots accordingly
    def update_plots_using_region(self):
        """ If linear_region x_axis changes, then change all graphs """
        self.frequency_plot_graph.setXRange(
            *self.linear_region.getRegion(), padding=0)
        self.resistance_graph.setXRange(
            *self.linear_region.getRegion(), padding=0)
        self.temperature_plot_graph.setXRange(
            *self.linear_region.getRegion(), padding=0)
        self.pressure_plot_graph.setXRange(
            *self.linear_region.getRegion(), padding=0)
        self.humidity_plot_graph.setXRange(
            *self.linear_region.getRegion(), padding=0)

    def update_frequency_region(self):
        """ Update the X axis of the frequency graph """
        self.linear_region.setRegion(
            self.frequency_plot_graph.getViewBox().viewRange()[0])

    def update_resistance_region(self):
        """ Update the X axis of the resistance graph """
        self.linear_region.setRegion(
            self.resistance_graph.getViewBox().viewRange()[0])

    def update_temperature_region(self):
        """ Update the X axis of the temperature graph """
        self.linear_region.setRegion(
            self.temperature_plot_graph.getViewBox().viewRange()[0])

    def update_pressure_region(self):
        """ Update the X axis of the pressure graph """
        self.linear_region.setRegion(
            self.pressure_plot_graph.getViewBox().viewRange()[0])

    def update_humidity_region(self):
        """ Update the X axis of the humidity graph """
        self.linear_region.setRegion(
            self.humidity_plot_graph.getViewBox().viewRange()[0])

    def show_graphs(self):
        """ Display the graph within the gui """
        self.frequency_plot_graph.show()
        self.resistance_graph.show()
        self.temperature_plot_graph.show()
        self.pressure_plot_graph.show()
        self.humidity_plot_graph.show()
        self.overview_graph.show()
        self.overview_graph.setXRange(-1000, 5000)


class Main_Widget(QWidget):
    def __init__(self):
        """ Give basic structure to the main widget """
        super().__init__()

        #######################################################################
        # Attempt Connection Buttons
        #######################################################################

        self.attempt_connection_button = QPushButton(
            'Attempt Connection', self)

        #######################################################################
        # Graph Widget
        #######################################################################

        self.graph_widget = Graph_Window(self)
        self.graph_widget.show_graphs()

        # Need to keep this function bellow the declaration of self.graph_widget
        self.attempt_connection_button.clicked.connect(
            self.graph_widget.attempt_to_connect)

        #######################################################################
        # File Manipulation Buttons
        #######################################################################

        self.open_frequency_resistance_file_button = QPushButton(
            'Open Json', self)
        self.open_frequency_resistance_file_button.clicked.connect(
            self.graph_widget.select_json_file)

        self.open_second_resistance_button = QPushButton(
            'Open Resistance Json', self)
        self.open_second_resistance_button.clicked.connect(
            self.graph_widget.select_resistance_json_file)

        #######################################################################
        # Graph Channel Buttons
        #######################################################################

        self.graph_channel_one_button = QPushButton('Graph Channel 0', self)
        self.graph_channel_one_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_one)
        self.graph_channel_one_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[0]))

        self.graph_channel_two_button = QPushButton('Graph Channel 1', self)
        self.graph_channel_two_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_two)
        self.graph_channel_two_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[1]))

        self.graph_channel_three_button = QPushButton('Graph Channel 2', self)
        self.graph_channel_three_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_three)
        self.graph_channel_three_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[2]))

        self.graph_channel_four_button = QPushButton('Graph Channel 3', self)
        self.graph_channel_four_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_four)
        self.graph_channel_four_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[3]))

        self.graph_channel_five_button = QPushButton('Graph Channel 4', self)
        self.graph_channel_five_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_five)
        self.graph_channel_five_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[4]))

        self.graph_channel_six_button = QPushButton('Graph Channel 5', self)
        self.graph_channel_six_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_six)
        self.graph_channel_six_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[5]))

        self.graph_channel_seven_button = QPushButton('Graph Channel 6', self)
        self.graph_channel_seven_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_seven)
        self.graph_channel_seven_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[6]))

        self.graph_channel_eight_button = QPushButton('Graph Channel 7', self)
        self.graph_channel_eight_button.clicked.connect(
            self.graph_widget.switch_frequency_plot_channel_eight)
        self.graph_channel_eight_button.setStyleSheet(
            "background-color:rgb(%d,%d,%d)" % (LINE_COLORS[7]))

        self.download_all_files_button = QPushButton(
            'Download All Files', self)
        self.download_all_files_button.clicked.connect(
            self.graph_widget.download_all_files)
        self.download_all_files_button.setStyleSheet(
            "background-color:rgb(255,255,255)")

        #######################################################################
        # Layouts
        #######################################################################

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_frequency_resistance_file_button)
        button_layout.addWidget(self.open_second_resistance_button)
        button_layout.addWidget(self.attempt_connection_button)
        button_layout.addWidget(self.graph_channel_one_button)
        button_layout.addWidget(self.graph_channel_two_button)
        button_layout.addWidget(self.graph_channel_three_button)
        button_layout.addWidget(self.graph_channel_four_button)
        button_layout.addWidget(self.graph_channel_five_button)
        button_layout.addWidget(self.graph_channel_six_button)
        button_layout.addWidget(self.graph_channel_seven_button)
        button_layout.addWidget(self.graph_channel_eight_button)
        button_layout.addWidget(self.download_all_files_button)

        overall_layout = QVBoxLayout()
        overall_layout.addLayout(button_layout)
        overall_layout.addWidget(self.graph_widget)

        self.setLayout(overall_layout)

        self.setGeometry(100, 100, 1280 + 100, 720 + 100)
