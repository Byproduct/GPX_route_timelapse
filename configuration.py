import multiprocessing

# Configuration
MAP_WIDTH = 1920
MAP_HEIGHT = 1080
INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

# Stamp the current date and year color legend in the output images.
TIMESTAMPS = True

# Define colors that represent years.
# Black (#000000) is used for years that have no color defined.
# Only defined years/colors will be included on the legend.
# Put these in chronological order.
YEAR_COLORS = {
    2018: '#000000',
    2019: '#0000FF',
    2020: '#6600BB',
    2021: '#FF0000',
    2022: '#00AA00',
    2023: '#888800',
    2024: '#FF88FF'
}

# Use False for default map tiles, or True for better-looking 'Alidade Smooth' map tiles. The latter requires a Stadia API key, but you can get one for free.
ALIDADE_MAP = False
STADIA_API_KEY = 'your stadia API key here'
EXTRA_MAP_TILES = 5

# The map zoom level is detected based on the lat/lon coordinates in routes.
# By default (0), all routes are completely visible on the map.
# Add positive values to zoom in or negative values to zoom out. 
ADDITIONAL_ZOOM_LEVELS = 1

# Map boundaries are based on the lat/lon coordinates in routes.
# You can adjust the autodetected view position with these values
ADJUST_BOUNDARIES = False
MIN_LAT_ADJUSTMENT = 0.00
MAX_LAT_ADJUSTMENT = -0.00
MIN_LON_ADJUSTMENT = 0.00
MAX_LON_ADJUSTMENT = -0.00

# More output text, for debugging purposes
VERBOSE_OUTPUT = False

# Seconds to wait between loading the html and capturing it. It takes some time for the tiles to load and the map to adjust itself into position.
# Increase this value if your map images have not fully loaded / adjusted into position.
CAPTURE_DELAY = 0.6

# If True, deletes all files in the output folder before proceeding
CLEAR_OUTPUT_FOLDER = True

# This script uses (logical processors - 1) workers for multithreading. Set a custom value if desired.
number_of_workers = max(1, multiprocessing.cpu_count() - 1)