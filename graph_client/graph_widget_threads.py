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
        # pysftp does not have a way to see if they device is online
        # without raising an excception, so this socket will be responsible
        # for this action.

        try:
            ping_test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ping_test_socket.settimeout(0.08)
            ping_test_socket.connect((RASPBERRY_PI_HOST, RASPBERRY_PI_PORT))
            return True
        except socket.error as e:
            print(e)
            return False

        finally:
            ping_test_socket.close()

    def get_file_from_server(self, passed_file_path_json):
        if not self.ping_test():
            return

        passed_file_path_json = passed_file_path_json.replace('\\', '/')
        position_to_cut = len(LOCAL_DIRECTORY_OF_SENSOR_DATA)

        with pysftp.Connection(host=RASPBERRY_PI_HOST,
                               username=RASPBERRY_PI_USERNAME,
                               password=RASPBERRY_PI_PASSWORD,
                               cnopts=self.cnopts,
                               port=RASPBERRY_PI_PORT) as sftp:

            remote_path = RASPBERRY_PI_SENSOR_DATA_FOLDER + passed_file_path_json[position_to_cut:]

            global DOWNLOADING_FILES
            if sftp.exists(remote_path) and not DOWNLOADING_FILES:
                DOWNLOADING_FILES = True
                sftp.get(remote_path, LOCAL_DIRECTORY_OF_SENSOR_DATA + passed_file_path_json[position_to_cut:],
                         preserve_mtime=True)
                DOWNLOADING_FILES = False

    def get_sensor_data_from_server(self):

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
            stfp.get_d(RASPBERRY_PI_SENSOR_DATA_FOLDER, LOCAL_DIRECTORY_OF_SENSOR_DATA, preserve_mtime=True)
            DOWNLOADING_FILES = False

    def run(self):
        while (self.is_running):
            try:
                if self.attempt_connection:
                    self.attempt_connection_button.setStyleSheet("background-color:rgb(0,255,0)")
                    self.get_file_from_server(str(self.parent_widget.file_path_json))
                    # self.get_file_from_server(str(self.parent_widget.file_path_environment))
                else:
                    self.attempt_connection_button.setStyleSheet("background-color:rgb(255,0,0)")

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
        self.is_running = False

    def __del__(self):
        self.stop_thread()
        self.quit()
        self.wait()

    def run(self):
        while self.is_running:
            self.process()

    def process(self):

        time_to_process = time()

        try:
            if self.parent_widget.file_path_json is None:
                return

            if self.parent_widget.file_path_json[-len('csv'):]:
                if DOWNLOADING_FILES:
                    return

                with open(self.parent_widget.file_path_json, 'r') as current_file:
                    json_data = json.load(current_file)

                self.process_frequency_data(json_data)
                self.process_resistance_data(json_data)
                self.process_temperature_data(json_data)
                self.process_pressure_data(json_data)
                self.process_humidity_data(json_data)


        except Exception as e:
            print('ERROR: Processing Data Thread:', e)

        finally:
            print('Process Function took: %0.4f ms' % float(time() - time_to_process))
            sleep(0.1)

    def process_temperature_data(self, json_data):

        try:
            time_duration_list = []
            temperature_list = []
            for dictionary in json_data:
                if not dictionary['temperature']['value'] is None:
                    time_duration_list.append(dictionary['temperature']['time'])
                    temperature_list.append(dictionary['temperature']['value'])

            if not self.humidity_queue.full():
                self.temperature_queue.put((time_duration_list, temperature_list))
            else:
                self.humidity_queue.get()
                self.temperature_queue.put((time_duration_list, temperature_list))


        except Exception as e:
            print('ERROR: processing temperature:', e)

    def process_pressure_data(self, json_data):

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
        # Reads data from latest file and splits into a list of lines

        try:
            for key in self.sorted_keys:
                self.directory_of_frequency_channels[key]['x'].clear()
                self.directory_of_frequency_channels[key]['y'].clear()

            for dictionary in json_data:
                for position, key in enumerate(self.sorted_keys):
                    if not dictionary['frequency']['value'][str(position)] is None:
                        self.directory_of_frequency_channels[key]['x'].append(dictionary['frequency']['time'])
                        self.directory_of_frequency_channels[key]['y'].append(
                            float(dictionary['frequency']['value'][str(position)]))

            if not self.frequency_queue.full():
                self.frequency_queue.put(dict(self.directory_of_frequency_channels))
            else:
                self.frequency_queue.get()
                self.frequency_queue.put(dict(self.directory_of_frequency_channels))

        except Exception as e:
            print('ERROR: process_frequency_data:', e)

    def process_resistance_data(self, json_data):
        try:

            time_duration_list = []
            resistance_list = []

            for dictionary in json_data:
                if not dictionary['resistance']['value'] is None:
                    time_duration_list.append(dictionary['resistance']['time'])
                    resistance_list.append(dictionary['resistance']['value'])

            if not self.resistance_queue.full():
                self.resistance_queue.put((time_duration_list, resistance_list))
            else:
                self.resistance_queue.get()
                self.resistance_queue.put((time_duration_list, resistance_list))

        except Exception as e:
            print('Error: process_resistance_data:', e)

    def get_frequency_data(self):
        return self.frequency_queue.get()

    def get_resistance_data(self):
        return self.resistance_queue.get()

    def get_temperature_data(self):
        return self.temperature_queue.get()

    def get_pressure_data(self):
        return self.pressure_queue.get()

    def get_humidity_data(self):
        return self.humidity_queue.get()
