import mylib
import time
import os 
import zipfile

directory_download = os.path.join(os.path.abspath(os.getcwd()),"download/")
directory = directory_download+"/data/"

with zipfile.ZipFile(directory_download+'/data.zip', 'r') as zip_ref:
    zip_ref.extractall(directory_download)


pattern = "GeoTIFF"
mylib.download_all(directory, pattern)

