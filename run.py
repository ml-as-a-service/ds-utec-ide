import mylib
import time

url = 'https://visualizador.ide.uy/ideuy/core/load_public_project/ideuy/'
driver = mylib.getDriver(url)

mylib.getRootIframeSource(driver)

driver.quit() 