# Functions related to map tiles

import math
import os
import requests

from configuration import *

def deg_to_rad(deg):
    return deg * (math.pi / 180)

def lat_to_tile(zoom, lat):
    lat_rad = deg_to_rad(lat)
    return (1 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2 * (2 ** zoom)

def lon_to_tile(zoom, lon):
    return (lon + 180) / 360 * (2 ** zoom)

def get_zoom_level(min_lat, max_lat, min_lon, max_lon, map_width, map_height):
    for zoom in range(20, -1, -1):
        lat_tile_diff = abs(lat_to_tile(zoom, min_lat) - lat_to_tile(zoom, max_lat))
        lon_tile_diff = abs(lon_to_tile(zoom, min_lon) - lon_to_tile(zoom, max_lon))
        
        lat_pixel_diff = lat_tile_diff * 256
        lon_pixel_diff = lon_tile_diff * 256
        
        if lat_pixel_diff <= map_height and lon_pixel_diff <= map_width:
            return zoom + ADDITIONAL_ZOOM_LEVELS
    return 0

def coordinates_to_tile(zoom, lat, lon):
    """Convert latitude and longitude to map tile coordinates"""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def get_tile_bounds(zoom, min_lat, max_lat, min_lon, max_lon):
    min_x, min_y = coordinates_to_tile(zoom, max_lat, min_lon)
    max_x, max_y = coordinates_to_tile(zoom, min_lat, max_lon)
    return min_x, max_x, min_y, max_y

def download_tile(zoom, x, y, STADIA_API_KEY):
    tile_folder = os.path.join('html_maps/map_tiles', str(zoom), str(x))
    tile_path = os.path.join(tile_folder, f'{y}.png')
    
    if os.path.exists(tile_path):
        return False
  
    if ALIDADE_MAP:
        url = f'https://tiles.stadiamaps.com/tiles/alidade_smooth/{zoom}/{x}/{y}.png?api_key={STADIA_API_KEY}'
        response = requests.get(url)
    else:
        url = f'https://tile.openstreetmap.org/{zoom}/{x}/{y}.png'
        headers = {'User-Agent': 'Byprodcut gpx timelapse creator (byproduct@iki.fi)'}
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        os.makedirs(tile_folder, exist_ok=True)
        with open(tile_path, 'wb') as file:
            file.write(response.content)
        return True
    else:
        print(f'Failed to download tile {zoom}/{x}/{y}. HTTP Status code: {response.status_code}')

def download_tiles(zoom, min_x, max_x, min_y, max_y, STADIA_API_KEY):
    downloaded_tiles = 0
    skipped_tiles = 0
    for x in range(min_x - EXTRA_MAP_TILES, max_x + EXTRA_MAP_TILES + 1):
        for y in range(min_y - EXTRA_MAP_TILES, max_y + EXTRA_MAP_TILES + 1):
            downloaded = download_tile(zoom, x, y, STADIA_API_KEY)
            if downloaded:
                downloaded_tiles += 1
            else:
                skipped_tiles += 1
            if skipped_tiles:
                print(f'\r{downloaded_tiles} tiles downloaded, {skipped_tiles} already existed.     ', end='', flush=True)
            else:
                print(f'\r{downloaded_tiles} tiles downloaded.                                      ', end='', flush=True)
    print(' ')
       