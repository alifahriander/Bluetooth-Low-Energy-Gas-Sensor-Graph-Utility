import os

LOCAL_DIRECTORY_OF_FILE = os.path.dirname(os.path.realpath(__file__))
LOCAL_DIRECTORY_OF_SENSOR_DATA = LOCAL_DIRECTORY_OF_FILE + '/sensor_data/'
LOCAL_DIRECTORY_OF_SENSOR_DATA = r'C:\Users\Tabby\Documents\GitHub\Bluetooth-Low-Energy-Gas-Sensor-Manager\sensor_client' + '/sensor_data/'

if LOCAL_DIRECTORY_OF_SENSOR_DATA[-1:] != '/' and LOCAL_DIRECTORY_OF_SENSOR_DATA[-1:] != '\\':
    LOCAL_DIRECTORY_OF_SENSOR_DATA = LOCAL_DIRECTORY_OF_SENSOR_DATA + '/'

RASPBERRY_PI_SENSOR_DATA_FOLDER = '/home/pi/bluetooth_stuff_copy/sensor_data/'

if RASPBERRY_PI_SENSOR_DATA_FOLDER[-1:] != '/' and RASPBERRY_PI_SENSOR_DATA_FOLDER[-1:] != '\\':
    RASPBERRY_PI_SENSOR_DATA_FOLDER = RASPBERRY_PI_SENSOR_DATA_FOLDER + '/'
RASPBERRY_PI_HOST = '10.139.69.59'
# RASPBERRY_PI_HOST = '192.168.78.243'
RASPBERRY_PI_USERNAME = 'pi'
RASPBERRY_PI_PASSWORD = 'password'
RASPBERRY_PI_PORT = 22

LINE_COLORS = [(155, 113, 104),
               (178, 186, 187),
               (248, 196, 113),
               (125, 206, 160),
               (127, 179, 213),
               (231, 76, 60),
               (204, 127, 213),
               (248, 196, 113)]

DICTIONARY_OF_CHANNEL_KEYS = {
    0: {'x': [], 'y': []},
    16: {'x': [], 'y': []},
    32: {'x': [], 'y': []},
    48: {'x': [], 'y': []},
    64: {'x': [], 'y': []},
    80: {'x': [], 'y': []},
    96: {'x': [], 'y': []},
    112: {'x': [], 'y': []}
}

LINE_THICKNESS = 1.0

DOWNLOADING_FILES = False
