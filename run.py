import os
import mylib
 
# Download Dir
dir_path_download = os.path.abspath(os.getcwd())+'/download/'
 
url = 'https://visualizador.ide.uy/ideuy/core/load_public_project/ideuy/'
driver = mylib.getDriver(url)

driver.quit() 