# Functions related to capturing and editing image files

import os
import random
import time

from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


from configuration import * 

def add_timestamp_to_image(image_path, dt, year_only = False):
    image = Image.open(image_path)
    current_y_coord = 10
    year = dt.year
    date = dt.strftime('%Y-%m-%d')

    try:
        font = ImageFont.truetype('arial.ttf', 35)
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(image)

    if YEAR_COLORS:
        i = min(YEAR_COLORS.keys())

        # timestamp previously defined years if any
        while i < year:
            try:
                color = YEAR_COLORS.get(i, '#000000')
                text_bbox = draw.textbbox((0, 0), str(year), font=font)
                text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])
                text_position = (10, current_y_coord)
                draw.text(text_position, str(i), font=font, fill=color, stroke_width=1, stroke_fill='black')
                current_y_coord += 40
            except Exception as e:
                print(f'Error creating timestamp: {e}')
            i += 1

    if year_only:
        stamp = str(year)
    else:
        stamp = str(date)

    color = YEAR_COLORS.get(year, '#000000')      

    text_bbox = draw.textbbox((0, 0), stamp, font=font)
    text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])
    text_position = (10, current_y_coord)
    draw.text(text_position, stamp, font=font, fill=color, stroke_width=1, stroke_fill='black')

    image.save(image_path)

def add_timestamp_to_image_task(args):
    image_path, date = args
    add_timestamp_to_image(image_path, date)
    return image_path    

def capture_html_map(driver, html_path, date):
    try:
        driver.get(f'file://{os.path.abspath(html_path)}')
        filename = os.path.basename(html_path)[:-4] + 'png'
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        # Wait for the map to load and move into position before capturing
        # + short random to avoid all threads waiting and working at the exact same times
        time.sleep(CAPTURE_DELAY + random.uniform(0, 0.1))
        
        image_capture_data = driver.get_screenshot_as_png()
        
        with open(output_path, 'wb') as f:
            f.write(image_capture_data)

        print(f'\r{filename}                    \r', end='', flush=True)

    except Exception as e:
        print(f"Error capturing {html_path}: {e}")
        
def set_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument(f'--window-size={MAP_WIDTH}x{MAP_HEIGHT}')

#   gpu is enabled by default - can be disabled for troubleshooting
#    options.add_argument('--disable-gpu')

#   headless mode can be enabled to hide the windows that pop up during the image creation process (but it works as a fun progress indicator)
#    options.add_argument('--headless')

# Options to mute the chrome output messages in console window - can try commenting/uncommenting these if the messages persist.
    options.add_argument('--silent')
    options.add_argument('disable-infobars')
    options.add_argument('disable-logging')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
#    options.add_argument('--log-level=3')

    return options

def capture_chunk(html_paths, dates):
    service = Service(log_path=os.devnull)
    options = set_chrome_options()
    driver = webdriver.Chrome(options=options)
    for html_path, date in zip(html_paths, dates):
        capture_html_map(driver, html_path, date)
    driver.quit()    

def save_map(folium_map, output_path):
    try:
        folium_map.save(output_path)
    except Exception as e:
        with open('error_log.txt', 'a') as f:
            f.write(f"Error saving {output_path}: {e}\n")
        print(f"Error saving {output_path}: {e}\n")
        sys.exit(1)