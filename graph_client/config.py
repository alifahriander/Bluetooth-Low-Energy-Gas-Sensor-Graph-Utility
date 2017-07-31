import os

# This corriponds to the path of where the config.py is located
LOCAL_DIRECTORY_OF_FILE = os.path.dirname(os.path.realpath(__file__))

# This uses the path of config.py to then find the /sensor_data/ folder
# NOTE: You can change this to which ever path holds the JSON files
LOCAL_DIRECTORY_OF_SENSOR_DATA = LOCAL_DIRECTORY_OF_FILE + '/sensor_data/'
if not os.path.exists(LOCAL_DIRECTORY_OF_SENSOR_DATA):
    os.mkdir(LOCAL_DIRECTORY_OF_SENSOR_DATA)


# Checks if path has a '/' or '\' at the end of the string.
# This is important since the string is used to look through files
if LOCAL_DIRECTORY_OF_SENSOR_DATA[-1:] != '/' and LOCAL_DIRECTORY_OF_SENSOR_DATA[-1:] != '\\':
    LOCAL_DIRECTORY_OF_SENSOR_DATA = LOCAL_DIRECTORY_OF_SENSOR_DATA + '/'

# These are the attributes that  corispond to the RaspberryPi's configuration
RASPBERRY_PI_HOST = '10.139.69.59'
RASPBERRY_PI_USERNAME = 'piUser'
RASPBERRY_PI_PASSWORD = 'password'
RASPBERRY_PI_PORT = 22

# This constant corisponds to the folder that the json files are created within
RASPBERRY_PI_SENSOR_DATA_FOLDER = '/home/pi/sensor_folder/sensor_data/'
# Checks to see if the folder path has an ending '/'
if RASPBERRY_PI_SENSOR_DATA_FOLDER[-1:] != '/' and RASPBERRY_PI_SENSOR_DATA_FOLDER[-1:] != '\\':
    RASPBERRY_PI_SENSOR_DATA_FOLDER = RASPBERRY_PI_SENSOR_DATA_FOLDER + '/'


# Each tuple corisponds to each channel's color
# within the order that they are put in
LINE_COLORS = [(155, 113, 104),
               (178, 186, 187),
               (238, 58,  140),
               (125, 206, 160),
               (127, 179, 213),
               (231, 76,  60),
               (204, 127, 213),
               (248, 196, 113)]

# Base configuration of a dictonary to place the data of each channel
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

# The thickness of each line on the graph
LINE_THICKNESS = 1.0

# Weather we are downlaoding the files once the program runs
DOWNLOADING_FILES = False

# If set to true, a legend will be shown within the frequency graph
ADD_FREQUENCY_LEGEND = False

# A bool that will toogle antialiasing
ANTIALIAS = True
