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


class Server_Handler(QThread):
    def __init__(self, passed_parent_widget):
        QThread.__init__(self)

        self.parent_widget = passed_parent_widget

        self.current_data = []
        self.is_running = True

        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None

        self.attempt_connection = True

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
            print (e)
            return False

        finally:
            ping_test_socket.close()

    def get_file_from_server(self, passed_file_path_frequency_resistance):
        if not self.ping_test():
            return

        passed_file_path_frequency_resistance = passed_file_path_frequency_resistance.replace('\\','/')
        position_to_cut = len(LOCAL_DIRECTORY_OF_SENSOR_DATA)


        with pysftp.Connection(host = RASPBERRY_PI_HOST,
                               username = RASPBERRY_PI_USERNAME,
                               password=RASPBERRY_PI_PASSWORD,
                               cnopts=self.cnopts,
                               port = RASPBERRY_PI_PORT) as sftp:

            remote_path = RASPBERRY_PI_SENSOR_DATA_FOLDER + passed_file_path_frequency_resistance[position_to_cut:]

            global DOWNLOADING_FILES
            if sftp.exists(remote_path) and not DOWNLOADING_FILES:
                DOWNLOADING_FILES = True
                sftp.get(remote_path, LOCAL_DIRECTORY_OF_SENSOR_DATA + passed_file_path_frequency_resistance[position_to_cut:], preserve_mtime=True)
                DOWNLOADING_FILES = False

    def get_sensor_data_from_server(self):

        if not self.ping_test():
            return

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(host = RASPBERRY_PI_HOST,
                               username = RASPBERRY_PI_USERNAME,
                               password = RASPBERRY_PI_PASSWORD,
                               cnopts = self.cnopts,
                               port = RASPBERRY_PI_PORT) as stfp:
            global DOWNLOADING_FILES
            DOWNLOADING_FILES = True
            stfp.get_d(RASPBERRY_PI_SENSOR_DATA_FOLDER, LOCAL_DIRECTORY_OF_SENSOR_DATA, preserve_mtime=True)
            DOWNLOADING_FILES = False

    def run(self):
        while (self.is_running):
            try:
                if self.attempt_connection:
                    self.get_file_from_server(str(self.parent_widget.file_path_frequency_resistance))
                    self.get_file_from_server(str(self.parent_widget.file_path_environment))

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
            if self.parent_widget.file_path_frequency_resistance is None:
                pass
            elif self.parent_widget.file_path_frequency_resistance[-len('Frequency.csv'):] == 'Frequency.csv':
                self.process_frequency_data()

            elif self.parent_widget.file_path_frequency_resistance[-len('Resistance.csv'):] == 'Resistance.csv':
                self.process_resistance_data()

            if self.parent_widget.file_path_environment is None:
                pass
            elif self.parent_widget.file_path_environment[-len('Environment.csv'):] == 'Environment.csv':
                self.process_environment_data()

        except Exception as e:
            print ('ERROR: Processing Data Thread:', e)

        finally:
            print ('Process Function took: %0.4f ms' % float(time() - time_to_process))
            sleep(0.1)

    def process_environment_data(self):

        try:
            if DOWNLOADING_FILES:
                return

            with open(self.parent_widget.file_path_environment, 'r') as current_file:
                data = current_file.read().split('\n')

            temperature_time_duration_list = []
            temperature_list = []

            pressure_time_duration_list = []
            pressure_list = []

            humidity_time_duration_list = []
            humidity_list = []

            for line in data:
                line = line.split(',')

                if '' in line:
                    line.remove('')
                if len(line) == 0:
                    continue

                temperature_time_duration_list.append(float(line[0]))
                temperature_list.append(float(line[1]))
                pressure_time_duration_list.append(float(line[2]))
                pressure_list.append(float(line[3]))
                humidity_time_duration_list.append(float(line[4]))
                humidity_list.append(float(line[5]))


            self.temperature_queue.put((temperature_time_duration_list,temperature_list))
            self.pressure_queue.put((pressure_time_duration_list, pressure_list))
            self.humidity_queue.put((humidity_time_duration_list, humidity_list))
        except Exception as e:
            print('ERROR: processing environment:', e)

    def process_frequency_data(self):
        # Reads data from latest file and splits into a list of lines

        if self.frequency_queue.full():
            return
        try:
            # Don't read when downloading
            # NOTE: Instead of using a while loop to wait until its done downloading
            # we can just return and let the next loop around handle it.
            # This is done since if we use a while loop it can cause preformance drops
            if DOWNLOADING_FILES:
                return

            with open(self.parent_widget.file_path_frequency_resistance, 'r') as current_file:
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

            # Don't read while downloading
            # NOTE: Instead of using a while loop to wait until its done downloading
            # we can just return and let the next loop around handle it.
            # This is done since if we use a while loop it can cause preformance drops
            if DOWNLOADING_FILES:
                return

            with open(self.parent_widget.file_path_frequency_resistance, 'r') as current_file:
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

    def get_temperature_data(self):
        return self.temperature_queue.get()

    def get_pressure_data(self):
        return self.pressure_queue.get()

    def get_humidity_data(self):
        return self.humidity_queue.get()
