#---------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------CLEANING FOLDERS---------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------
import os
def empty_folders(folder_list):
    for folder in folder_list:
        folder_path = './' + folder + '/'
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
folder_list = ['accel', 'coords', 'disp', 'info', 'reaction']
empty_folders(folder_list)