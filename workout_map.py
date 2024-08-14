# Creates timelapse images out of GPX files. 
# The script generates HTML pages with folium/gpxpy, then captures them into images with Selenium/Chrome.
# User can then make a video of the screenshots using e.g. DaVinci Resolve.

# Put .gpx files in the 'input' folder.

# Requires pip install folium, gpxpy, pillow, selenium


import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

import folium
import gpxpy
from folium import TileLayer

from configuration import *
from gpx_files import get_center_and_bounds, get_gpx_filenames_and_dates
from image_files import add_timestamp_to_image, add_timestamp_to_image_task, capture_chunk, save_map
from map_tiles import download_tiles, get_zoom_level, get_tile_bounds
from util import clear_directory, current_directory, create_progress_bar_string, clear_screen


def main():
    clear_screen()
    print('-- GPX timelapse creator --\n')

    if CLEAR_OUTPUT_FOLDER:
        clear_directory(OUTPUT_FOLDER)
    clear_directory('html_maps')
        
    gpx_files = [os.path.join(INPUT_FOLDER, f) for f in os.listdir(INPUT_FOLDER) if f.endswith('.gpx')]
    if not gpx_files:
        print('Error: no gpx files found in input folder.')
        sys.exit(1)
    else:
        print(f'{len(gpx_files)} gpx files found.\n')
   
    print(f'Searching for map bounds.')
    center_lat, center_lon, min_lat, max_lat, min_lon, max_lon = get_center_and_bounds(gpx_files, number_of_workers)
    if VERBOSE_OUTPUT:
        print(f'latitude {min_lat} to {max_lat}\nlongitude {min_lon} to {max_lon}')

    zoom_level = get_zoom_level(min_lat, max_lat, min_lon, max_lon, MAP_WIDTH, MAP_HEIGHT)
    min_x, max_x, min_y, max_y = get_tile_bounds(zoom_level, min_lat, max_lat, min_lon, max_lon)
    if VERBOSE_OUTPUT:
        print(f'map zoom level {zoom_level}\ntiles x {min_x} to {max_x}\ntiles y {min_y} to {max_y}')

    print(f'\nDownloading map tiles.')
    download_tiles(zoom_level, min_x, max_x, min_y, max_y, STADIA_API_KEY)

    folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)  
    # folium_map.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    if ALIDADE_MAP:
        TileLayer(
            tiles="map_tiles/{z}/{x}/{y}.png",
            attr="&copy; <a href='https://stadiamaps.com/'>Stadia Maps</a>, &copy; <a href='https://openmaptiles.org/'>OpenMapTiles</a> &copy; <a href='http://openstreetmap.org/copyright'>OpenStreetMap contributors</a>",
            name='Alidade Smooth',
            control=False
        ).add_to(folium_map)
         
    if VERBOSE_OUTPUT:
        print('\nGetting date and time in gpx files.')
    gpx_filenames_with_dates = get_gpx_filenames_and_dates()  # list of tuples (filename, date)

    print('Creating html maps.')
    current_map = 0
    html_paths = []
    start_time = datetime.now()
    for file_and_date in gpx_filenames_with_dates:
        date = file_and_date[1]
        year = date.year
        file_path = file_and_date[0]
        color = YEAR_COLORS.get(year, '#000000')
        with open(file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)               
            for track in gpx.tracks:
                for segment in track.segments:
                    segment_coords = [(point.latitude, point.longitude) for point in segment.points]
                    folium.PolyLine(segment_coords, color=color, weight=3.5, opacity=1).add_to(folium_map)
        
        output_filename = str(current_map).zfill(8) + '.html'
        output_path = os.path.join(current_directory, 'html_maps', output_filename)
        html_paths.append(output_path)
        save_map(folium_map, output_path)
        progress_bar = create_progress_bar_string(current_map + 1, len(gpx_filenames_with_dates), width=50)
        print(f'\r{progress_bar} {current_map + 1} / {len(gpx_filenames_with_dates)}       ', end ='')
        current_map += 1
    print('\r                                                                                                 \r')
       
    print('Capturing html maps into images.')
    chunks = [html_paths[i::number_of_workers] for i in range(number_of_workers)]
    date_chunks = [gpx_filenames_with_dates[i::number_of_workers] for i in range(number_of_workers)]
    
    with ProcessPoolExecutor(max_workers=number_of_workers) as executor:
        futures = []
        for chunk, date_chunk in zip(chunks, date_chunks):
            future = executor.submit(capture_chunk, chunk, [date[1] for date in date_chunk])
            futures.append(future)

        for future in futures:
            future.result()

    print("\r                                          ")
    
    print('Timestamping images')
    image_paths = []
    for html_path in html_paths:
        filename = os.path.basename(html_path)[:-4] + 'png'
        image_path = os.path.join(current_directory, OUTPUT_FOLDER, filename)
        image_paths.append(image_path)

    tasks = [(image_path, gpx_filenames_with_dates[index][1]) for index, image_path in enumerate(image_paths)]

    # Create a copy of the last image, and stamp it with just the year (not displaying month or day)
    last_image_path = image_paths[-1]
    copied_filename = os.path.basename(last_image_path)[:-4] + '_last.png'
    copied_image_path = os.path.join(os.path.dirname(last_image_path), copied_filename)
    shutil.copyfile(last_image_path, copied_image_path)
        
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(add_timestamp_to_image_task, task): task for task in tasks}
        for index, _ in enumerate(as_completed(futures)):
            progress_bar = create_progress_bar_string(index + 1, len(image_paths), width=50)
            print(f'\r{progress_bar} {index + 1} / {len(image_paths)}       ', end='')
    
    add_timestamp_to_image(copied_image_path, gpx_filenames_with_dates[-1][1], year_only=True)  # Stamp an extra image with just the year (no month or day in the last image)

    # Create images.txt for use with ffmpeg
    textfile_path = os.path.join(current_directory, 'output', 'images.txt')
    with open(textfile_path, "w", encoding = 'utf-8') as f:
        for image_path in image_paths:
            f.write(f"file '{image_path}'\n")
        f.write(f"file '{copied_image_path}'")
    
    print('\r                                                                                                                       \r')
    
    print('All done ^_^ _b')

if __name__ == '__main__':
    main()
