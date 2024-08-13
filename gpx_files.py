# Functions related to .gpx files

import concurrent.futures
import gpxpy
import os
import re
import sys

from datetime import datetime

from configuration import *
from util import current_directory



def get_datetime_from_gpx(file_path):
    """Search for the first <time> tag in the gpx file and extract it as datetime"""
    time_pattern = re.compile(r'<time>(.*?)</time>')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = time_pattern.search(line)
            if match:
                time_str = match.group(1)
                try:
                    time_dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
                    return time_dt
                except ValueError as e:
                    print(f"Error parsing date: {e}")
                    sys.exit(1)
    print(f"Error getting date from {file_path}")
    sys.exit(1)
    

def get_all_coordinates_from_gpx(file_path):
    """ Get all coordinates from a gpx file"""
    latitudes = []
    longitudes = []
    
    print(f'\r{file_path}    ', end='', flush=True)
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    latitudes.append(point.latitude)
                    longitudes.append(point.longitude)
                    
    return latitudes, longitudes

def get_center_and_bounds(gpx_files, number_of_workers):
    latitudes = []
    longitudes = [] 

    with concurrent.futures.ProcessPoolExecutor(max_workers=number_of_workers) as executor:
        results = list(executor.map(get_all_coordinates_from_gpx, gpx_files))
        
    for lat_list, lon_list in results:
        latitudes.extend(lat_list)
        longitudes.extend(lon_list)
    
    if latitudes and longitudes:
        center_lat = sum(latitudes) / len(latitudes)
        center_lon = sum(longitudes) / len(longitudes)
        
        min_lat = min(latitudes)
        max_lat = max(latitudes)
        min_lon = min(longitudes)
        max_lon = max(longitudes)
        
        # Manual adjustment of map boundaries if defined in configuration
        if ADJUST_BOUNDARIES:
            min_lat += MIN_LAT_ADJUSTMENT
            max_lat += MAX_LAT_ADJUSTMENT
            min_lon += MIN_LON_ADJUSTMENT
            max_lon += MAX_LON_ADJUSTMENT
        
        print('\r                                                              \r', end ='')
        return center_lat, center_lon, min_lat, max_lat, min_lon, max_lon
    else:
        print('Unable to find map boundaries - no gpx files?')
        sys.exit(1)
        

def get_gpx_filenames_and_dates():
    """Create a sorted list of tuples with the gpx filename and the date in it."""
    files_with_dates = []
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith('.gpx'):
            file_path = os.path.join(current_directory, INPUT_FOLDER, filename)
            dt = get_datetime_from_gpx(file_path)
            file_date = dt
            if file_date:
                files_with_dates.append((file_path, file_date))
            print(f'\r{filename}: {dt}                   ', end='', flush=True)
    files_with_dates.sort(key=lambda x: x[1])
    print(f'\r                                                  ')
    return files_with_dates