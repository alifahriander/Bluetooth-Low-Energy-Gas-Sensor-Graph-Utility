import os
LOCAL_DIRECTORY_OF_FILE = os.path.dirname(os.path.realpath(__file__))
LOCAL_DIRECTORY_OF_SENSOR_DATA = LOCAL_DIRECTORY_OF_FILE + '/sensor_data/'

RASPBERRY_PI_SENSOR_DATA_FOLDER = '/home/pi/bluetooth_stuff/sensor_data/'
RASPBERRY_PI_HOST = '10.139.69.59'
RASPBERRY_PI_USERNAME = 'pi'
RASPBERRY_PI_PASSWORD = 'password'
RASPBERRY_PI_PORT = 22

#LINE_COLORS = [(212, 230, 241),
#               (178, 186, 187),
#               (248, 196, 113),
#               (125, 206, 160),
#               (127, 179, 213),
#               (231, 76, 60),
#               (204, 127, 213),
#               (248, 196, 113)]

LINE_COLORS = ['b',
               'g',
               'r',
               'c',
               'm',
               'y',
               'k',
               (248, 196, 113)]

DICTIONARY_OF_CHANNEL_KEYS = {
                            0: {'x':[], 'y':[]},
                            16:{'x':[], 'y':[]},
                            32:{'x':[], 'y':[]},
                            48:{'x':[], 'y':[]},
                            64:{'x':[], 'y':[]},
                            80:{'x':[], 'y':[]},
                            96:{'x':[], 'y':[]},
                            112:{'x':[], 'y':[]}
                            }

LINE_THICKNESS = 1.0
