#######################################################################
# Writen by: Derek Santos
#######################################################################

# 3rd Party Modules
import pyqtgraph as pg
from pyqtgraph import GraphicsWindow, GraphicsLayoutWidget, MultiPlotWidget
from pyqtgraph.Qt import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QFont, QFileDialog

import numpy as np

import pysftp

# Python Modules
import sys
from random import randint
from config import *
from threading import Thread
from time import sleep, time
from queue import Queue

def SELECT_LATEST_FILE(directory = DIRECTORY_OF_SENSOR_DATA):
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

class Server_Handler(QThread):
    def __init__(self):
        QThread.__init__(self)

        self.current_data = []
        self.is_running = True

        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None

    def __del__(self):
        self.stop_thread()
        self.quit()
        self.wait()

    def get_sensor_data_from_server(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(host = RASPBERRY_PI_HOST, username = RASPBERRY_PI_USERNAME, password = RASPBERRY_PI_PASSWORD, cnopts = cnopts, port = RASPBERRY_PI_PORT) as stfp:
            sftp.timeout(3)
            stfp.get_d(RASPBERRY_PI_SENSOR_DATA_FOLDER, DIRECTORY_OF_SENSOR_DATA, preserve_mtime=True)

    def run(self):
        while (self.is_running):
            try:
                self.get_sensor_data_from_server()
                sleep(0.5)
            except Exception as e:
                pass
    def stop_thread(self):
        self.is_running = False


class Data_Processing_Stream_Thread(QThread):
    def __init__(self, passed_widget):
        QThread.__init__(self)

        self.parent_widget = passed_widget

        self.server_handler = Server_Handler()
        self.is_running = True


        self.directory_of_frequency_channels = dict(DICTIONARY_OF_CHANNEL_KEYS)

        self.frequency_queue = Queue(2)
        self.resistance_queue = Queue(2)
        self.sorted_keys = sorted(self.directory_of_frequency_channels.keys())

        self.file_path = self.parent_widget.file_path

        self.process_timer_frequency_resistance = QtCore.QTimer()
        self.process_timer_frequency_resistance.timeout.connect(self.process)
        self.process_timer_frequency_resistance.start(100)


    def stop_thread(self):
        self.is_running = False

    def __del__(self):
        self.stop_thread()
        self.quit()
        self.wait()

    def run(self):
        pass

        #while(self.is_running):
        #    pass


        #    try:
        #        pass
        #        #self.server_handler.get_sensor_data_from_server()
        #    except Exception as e:
        #        print ('ERROR: Server Handler :', e)

        #    try:
        #        if not time() - last_update <= 1.0:

        #            if self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
        #                self.process_frequency_data()
        #                #self.parent_widget.plot_frequency_data(self.frequency_queue.get())

        #            elif self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
        #                self.process_resistance_data()
        #                #self.parent_widget.plot_resistance_data()

        #            last_update = time()

        #    except Exception as e:
        #        print ('ERROR: :', e)

        #self.stop_thread()

    def process(self):
        time_now = time()
        try:
            if self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
                self.process_frequency_data()

            elif self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
                self.process_resistance_data()

        except Exception as e:
            print ('ERROR: Processing Data Thread:', e)

        #finally:
        #    print ('Process Function took: %0.2f ms' % float(time() - time_now))



    def process_frequency_data(self):
        # Reads data from latest file and splits into a list of lines

        if self.frequency_queue.full():
            return
        try:
            with open(self.file_path, 'r') as current_file:
                data = current_file.read().split('\n')

            for key in self.sorted_keys:
                self.directory_of_frequency_channels[key]['x'].clear()
                self.directory_of_frequency_channels[key]['y'].clear()

            for line in data:

                line = line.split(',')

                if '' in line:
                    line.remove('')
                if len(line) == 0:
                    continue

                #for key in self.sorted_keys:
                #    for count in range(0, len(line), 3):
                key_position = 0
                for count in range(0, len(line), 3):
                        key = self.sorted_keys[key_position]
                        self.directory_of_frequency_channels[key]['x'].append(float(line[count+1]))
                        self.directory_of_frequency_channels[key]['y'].append(float(line[count+2]))
                        key_position += 1

            if not self.frequency_queue.full():
                self.frequency_queue.put(dict(self.directory_of_frequency_channels))
            else:
                self.frequency_queue.get()
                self.frequency_queue.put(dict(self.directory_of_frequency_channels))
        except Exception as e:
            print ('ERROR: process_frequency_data:', e)

    def process_resistance_data(self):
        try:
            if self.resistance_queue.full():
                return

            with open(self.file_path, 'r') as current_file:
                file_lines = current_file.read().split('\n')

            time_duration_list = []
            resistance_list = []

            for line in file_lines:
                if line.find(',') == -1 :
                    continue
                line = line.split(',')
                if len(line) < 4:
                    continue

                if '\n' in line:
                    line.remove('\n')
                if '' in line:
                    line.remove('')
                if ' ' in line:
                    line.remove(' ')

                time_duration_list.append (float(line[0]))
                resistance_list.append (float(line[3]))

            self.resistance_queue.put ( (time_duration_list, resistance_list) )
        except Exception as e:
            print ('Error: process_resistance_data:', e)

    def get_frequency_data(self):
        return self.frequency_queue.get()

    def get_resistance_data(self):
        return self.resistance_queue.get()


class Graph_Window(GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()

        a = QPushButton('Open CSV', self)
        a.resize(50, 50)
        a.clicked.connect(self.select_file)


        #self.resize (1280, 720)
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
        self.overview_graph         = self.addPlot(title = 'Overview Graph')

        self.frequency_resistance_plot_graph.showGrid  (x = True, y = True)
        self.temperature_plot_graph.showGrid(x = True, y = True)
        self.pressure_plot_graph.showGrid   (x = True, y = True)
        self.humidity_plot_graph.showGrid   (x = True, y = True)
        self.overview_graph.showGrid        (x = True, y = True)
        #self.overview_graph_viewbox = self.overview_graph.getViewBox()
        #self.overview_graph_viewbox.scaleBy(x = 0.5)


        self.frequency_resistance_plot_graph.sigXRangeChanged.connect  (self.update_frequency_region)
        self.temperature_plot_graph.sigXRangeChanged.connect(self.update_temperature_region)
        self.pressure_plot_graph.sigXRangeChanged.connect   (self.update_pressure_region)
        self.humidity_plot_graph.sigXRangeChanged.connect   (self.update_humidity_region)

        self.frequency_lines = []

        for position in range(0, len(DICTIONARY_OF_CHANNEL_KEYS.keys())):
            self.frequency_lines.append( pg.PlotCurveItem(x=[],
                                     y=[],
                                     pen = pg.mkPen(cosmetic = True, width = LINE_THICKNESS, color = LINE_COLORS[position]),
                                     name = 'Channel %d' % position) )
        for curve in self.frequency_lines:
            self.frequency_resistance_plot_graph.addItem(curve)


        self.resistance_line = pg.PlotCurveItem(x = [],
                                                y = [],
                                                pen = LINE_COLORS[0],
                                                width = LINE_THICKNESS,
                                                name = 'Resistance')
        self.frequency_resistance_plot_graph.addItem(self.resistance_line)

        self.overview_graph_line = self.overview_graph.plot  (x = [],
                                                    y = [],
                                                    pen = LINE_COLORS[0],
                                                    symbol = 'o',
                                                    name = 'Resistance')

        self.overview_graph.addItem(self.linear_region)

        self.linear_region.sigRegionChanged.connect(self.update_plots_using_region)

        self.file_path = SELECT_LATEST_FILE()

        ########################################################################
        # Data Processing Thread
        ########################################################################

        self.process_data_thread = Data_Processing_Stream_Thread(self)
        #self.process_data_thread.start()

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
        print ( QFileDialog.getOpenFileName() )


    def plot_all_data(self):
        self.plot_frequency_or_resistance_data()
        self.plot_temperature_data()
        self.plot_pressure_data()
        self.plot_humidity_data()


    def plot_frequency_or_resistance_data(self):
        try:

            if self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
                if not self.process_data_thread.frequency_queue.empty():
                    self.frequency_resistance_plot_graph.setTitle ('Frequency')
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

    def plot_pressure_data(self):
        self.pressure_plot_graph.setLabel ('left', 'Pa')
        self.pressure_plot_graph.setLabel ('bottom', 'Time (S)')

    def plot_humidity_data(self):
        self.humidity_plot_graph.setLabel ('left', '% Rh')
        self.humidity_plot_graph.setLabel ('bottom', 'Time (S)')

    # When the region changes then this function will change the plots accordingly
    def update_plots_using_region(self):
        self.frequency_resistance_plot_graph.setXRange  (*self.linear_region.getRegion(), padding = 0)
        self.temperature_plot_graph.setXRange(*self.linear_region.getRegion(), padding = 0)
        self.pressure_plot_graph.setXRange   (*self.linear_region.getRegion(), padding = 0)
        self.humidity_plot_graph.setXRange   (*self.linear_region.getRegion(), padding = 0)
        #self.overview_graph.setXRange(*self.linear_region.getRegion(), padding = 0)

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


if __name__ == '__main__':

    app = QApplication(sys.argv)

    #pg.setConfigOption('background', 'w')
    #pg.setConfigOption('foreground', 'k')
    pg.setConfigOptions(antialias = True)

    graph_window = Graph_Window()
    graph_window.show_graphs()



    sys.exit(app.exec_())
