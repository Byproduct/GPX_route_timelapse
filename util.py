# Utility functions not specific to this program
import os
import shutil

current_directory = os.path.dirname(os.path.realpath(__file__))

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')
    
def clear_directory(directory_path):
    """Clear directory of files, but leave subdirectories intact"""
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path} while clearing output folder. Reason: {e}')
          
def create_progress_bar_string(current, total, width=100):  
    bar = '['
    percentage = int(round((max(1, current) / total) * width))
    for x in range(percentage):
        bar += '█'
    for x in range(width-percentage):
        bar += ' '
    bar += ']'
    return bar