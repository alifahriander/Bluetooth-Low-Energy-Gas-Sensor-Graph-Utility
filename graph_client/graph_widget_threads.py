# 3rd Party Modules
import paramiko
import pysftp

# Python Modules
import socket
from time import sleep, time
from queue import Queue

# Developer Modules
from graph_widget import *
from config import *

import json


class Server_Handler(QThread):
    def __init__(self, passed_parent_widget, attempt_connection_button):
        QThread.__init__(self)

        self.parent_widget = passed_parent_widget
        self.attempt_connection_button = attempt_connection_button

        self.current_data = []
        self.is_running = True

        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None

        self.attempt_connection = False

        if self.ping_test():
            self.get_sensor_data_from_server()

    def __del__(self):
        self.stop_thread()
        self.quit()
        self.wait()

    def ping_test(self):
        """ Test to see if server being connected to is reachable """
        try:
            ping_test_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            ping_test_socket.settimeout(0.08)
            ping_test_socket.connect((RASPBERRY_PI_HOST, RASPBERRY_PI_PORT))
            return True
        except socket.error as e:
            print('ERROR: Ping Test', e)
            return False

        finally:
            ping_test_socket.close()

    def get_file_from_server(self, passed_file_path_json):
        """ Retrieve the current file from the server being connected to """
        # Check if server is reachable
        if not self.ping_test():
            return

        passed_file_path_json = passed_file_path_json.replace('\\', '/')
        position_to_cut = len(LOCAL_DIRECTORY_OF_SENSOR_DATA)

        with pysftp.Connection(host=RASPBERRY_PI_HOST,
                               username=RASPBERRY_PI_USERNAME,
                               password=RASPBERRY_PI_PASSWORD,
                               cnopts=self.cnopts,
                               port=RASPBERRY_PI_PORT) as sftp:

            remote_path = RASPBERRY_PI_SENSOR_DATA_FOLDER + \
                passed_file_path_json[position_to_cut:]

            global DOWNLOADING_FILES
            if sftp.exists(remote_path) and not DOWNLOADING_FILES:
                DOWNLOADING_FILES = True
                sftp.get(remote_path, LOCAL_DIRECTORY_OF_SENSOR_DATA + passed_file_path_json[position_to_cut:],
                         preserve_mtime=True)
                DOWNLOADING_FILES = False

    def get_sensor_data_from_server(self):
        """ Retieve whole directory of JSON files using config.py path """
        if not self.ping_test():
            return

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(host=RASPBERRY_PI_HOST,
                               username=RASPBERRY_PI_USERNAME,
                               password=RASPBERRY_PI_PASSWORD,
                               cnopts=self.cnopts,
                               port=RASPBERRY_PI_PORT) as stfp:
            global DOWNLOADING_FILES
            DOWNLOADING_FILES = True
            stfp.get_d(RASPBERRY_PI_SENSOR_DATA_FOLDER,
                       LOCAL_DIRECTORY_OF_SENSOR_DATA, preserve_mtime=True)
            DOWNLOADING_FILES = False

    def run(self):
        """ Loop until program ends, get files when booleans are true """
        while (self.is_running):
            try:
                if self.attempt_connection:
                    self.attempt_connection_button.setStyleSheet(
                        "background-color:rgb(0,255,0)")
                    self.get_file_from_server(
                        str(self.parent_widget.file_path_json))
                else:
                    self.attempt_connection_button.setStyleSheet(
                        "background-color:rgb(255,0,0)")

            except Exception as e:
                print(e)
            finally:
                sleep(0.5)

    def stop_thread(self):
        self.is_running = False


class Data_Processing_Stream_Thread(QThread):
    def __init__(self, passed_widget):
        QThread.__init__(self)

        self.parent_widget = passed_widget

        self.is_running = True

        self.directory_of_frequency_channels = dict(DICTIONARY_OF_CHANNEL_KEYS)

        self.frequency_queue = Queue(2)
        self.resistance_queue = Queue(2)
        self.temperature_queue = Queue(2)
        self.pressure_queue = Queue(2)
        self.humidity_queue = Queue(2)
        self.sorted_keys = sorted(self.directory_of_frequency_channels.keys())

        self.time_until_next_server_update = time()

    def stop_thread(self):
        """ When function is involked, boolean will switch to false """
        self.is_running = False

    def __del__(self):
        self.stop_thread()
        self.quit()
        self.wait()

    def run(self):
        """ Run process function until thread ends """
        while self.is_running:
            self.process()

    def process(self):
        """ Interprets JSON files, and places contents
         within queues for later functions to use """
        time_to_process = time()

        try:
            if self.parent_widget.file_path_json is None:
                return

            if self.parent_widget.file_path_json[-len('csv'):]:
                if DOWNLOADING_FILES:
                    return
                json_data = self.open_json_file(
                    self.parent_widget.file_path_json)

                if json_data is None:
                    return

                self.process_frequency_data(json_data)

                if self.parent_widget.resistance_json_path is None:
                    self.process_resistance_data(json_data)
                else:
                    second_json_data = self.open_json_file(
                        self.parent_widget.resistance_json_path)
                    self.process_resistance_data(second_json_data)

                self.process_temperature_data(json_data)
                self.process_pressure_data(json_data)
                self.process_humidity_data(json_data)

        except Exception as e:
            print('ERROR: Processing Data Thread:', e)

        finally:
            # print('Process Function took: %0.4f ms' %
            #      float(time() - time_to_process))
            sleep(0.1)

    def open_json_file(self, path):
        """ Open JSON file that graphs will use to plot """
        try:
            with open(path, 'r') as current_file:
                json_data = json.load(current_file)

        except Exception as e:
            print('ERROR: Opening JSON File:', e)
            json_data = None
        finally:
            return json_data

    def process_temperature_data(self, json_data):
        """ Process Temperature Data from a json file """
        try:
            time_duration_list = []
            temperature_list = []
            for dictionary in json_data:
                if not dictionary['temperature']['value'] is None:
                    time_duration_list.append(
                        dictionary['temperature']['time'])
                    temperature_list.append(dictionary['temperature']['value'])

            if not self.humidity_queue.full():
                self.temperature_queue.put(
                    (time_duration_list, temperature_list))
            else:
                self.humidity_queue.get()
                self.temperature_queue.put(
                    (time_duration_list, temperature_list))

        except Exception as e:
            print('ERROR: processing temperature:', e)

    def process_pressure_data(self, json_data):
        """ Process pressure  Data from a json file """

        try:
            time_duration_list = []
            pressure_list = []
            for dictionary in json_data:
                if not dictionary['pressure']['value'] is None:
                    time_duration_list.append(dictionary['pressure']['time'])
                    pressure_list.append(dictionary['pressure']['value'])

            if not self.humidity_queue.full():
                self.pressure_queue.put((time_duration_list, pressure_list))
            else:
                self.humidity_queue.get()
                self.pressure_queue.put((time_duration_list, pressure_list))

        except Exception as e:
            print('ERROR: processing pressure:', e)

    def process_humidity_data(self, json_data):
        """ Process humidity Data from a json file """

        try:
            time_duration_list = []
            humidity_list = []
            for dictionary in json_data:
                if not dictionary['humidity']['value'] is None:
                    time_duration_list.append(dictionary['humidity']['time'])
                    humidity_list.append(dictionary['humidity']['value'])

            if not self.humidity_queue.full():
                self.humidity_queue.put((time_duration_list, humidity_list))
            else:
                self.humidity_queue.get()
                self.humidity_queue.put((time_duration_list, humidity_list))

        except Exception as e:
            print('ERROR: processing humidity:', e)

    def process_frequency_data(self, json_data):
        """ Parses data from json_data variable and puts it into a queue """

        try:
            for key in self.sorted_keys:
                self.directory_of_frequency_channels[key]['x'].clear()
                self.directory_of_frequency_channels[key]['y'].clear()

            for dictionary in json_data:
                for position, key in enumerate(self.sorted_keys):
                    if not dictionary['frequency']['value'][str(position)] is None:
                        self.directory_of_frequency_channels[key]['x'].append(
                            dictionary['frequency']['time'])
                        self.directory_of_frequency_channels[key]['y'].append(
                            float(dictionary['frequency']['value'][str(position)]))

            if not self.frequency_queue.full():
                self.frequency_queue.put(
                    dict(self.directory_of_frequency_channels))
            else:
                self.frequency_queue.get()
                self.frequency_queue.put(
                    dict(self.directory_of_frequency_channels))

        except Exception as e:
            print('ERROR: process_frequency_data:', e)

    def process_resistance_data(self, json_data):
        """ Process resistance Data from a json file """
        try:

            time_duration_list = []
            resistance_list = []

            for dictionary in json_data:
                if not dictionary['resistance']['value'] is None:
                    time_duration_list.append(dictionary['resistance']['time'])
                    resistance_list.append(dictionary['resistance']['value'])

            if not self.resistance_queue.full():
                self.resistance_queue.put(
                    (time_duration_list, resistance_list))
            else:
                self.resistance_queue.get()
                self.resistance_queue.put(
                    (time_duration_list, resistance_list))

        except Exception as e:
            print('Error: process_resistance_data:', e)

    def get_frequency_data(self):
        """ Returns a value within frequency queue """
        if not self.frequency_queue.empty():
            return self.frequency_queue.get()
        else:
            return None

    def get_resistance_data(self):
        """ Returns a value within resistance queue """
        if not self.resistance_queue.empty():
            return self.resistance_queue.get()
        else:
            return None

    def get_temperature_data(self):
        """ Returns a value within temperature queue """
        if not self.temperature_queue.empty():
            return self.temperature_queue.get()
        else:
            return None

    def get_pressure_data(self):
        """ Returns a value within pressure queue """
        if not self.pressure_queue.empty():
            return self.pressure_queue.get()
        else:
            return None

    def get_humidity_data(self):
        """ Returns a value within humidity queue """
        if not self.humidity_queue.empty():
            return self.humidity_queue.get()
        else:
            return None
