from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

import time 
import csv 
import os 
import numpy as np
import pandas as pd

import requests
from multiprocessing.pool import ThreadPool

# Download Dir
dir_path_download = os.path.abspath(os.getcwd())+'/download/'
dir_path_data = dir_path_download+'data/'

levels = {
    'name': 'CN_Remesa',
    'is_root': True,
    'childs':[
        {"name": "01_MDT", "childs":[
            {"name": "01_MDT_LAS_Resolucion", "childs":[] },
            {"name": "02_MDT_GeoTIFF_Resolucion", "childs":[] },
        ] },
        {"name": "02_Ortoimagenes", "childs":[
            {"name": "01_RGBI_16bits", "childs":[] },
            {"name": "02_RGBI_8bits", "childs":[] },
            {"name": "03_RGB_8bits", "childs":[] },
            {"name": "04_Herramientas_de_apoyo", "childs":[] },

        ] },
        {"name": "03_Hidrografia", "childs":[
            {"name": "Shapefile", "childs":[] },
        ] },
    ]
}
 

def getDriver(url): 
    # settings
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : dir_path_download}
    chromeOptions.add_experimental_option("prefs",prefs)
    chromedriver = "chromedriver"

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chromeOptions)
    # driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

    # Open the main page
    driver.get(url)    
    
    time.sleep(3)
    # click + for Relieve
    ele = driver.find_elements_by_xpath("//*[contains(text(), 'Relieve (IDEuy)')]/parent::*")
    ele[0].find_element(By.CSS_SELECTOR, "i.fa").click()
    time.sleep(2)

    # click MDT Nacional
    driver.find_element(By.CSS_SELECTOR, "#gol-layer-83").click()
    driver.find_element(By.CSS_SELECTOR, "#layer-box-gol-layer-83 .box-tools .fa").click()
    time.sleep(2)

    # click Tools
    driver.find_element(By.LINK_TEXT, "Tools").click()
    time.sleep(2)

    # tools Download
    driver.find_element(By.ID, "staticdownloads").click()
    time.sleep(2)
    
    return driver


def file_put_contents(filename, content):
    with open(filename, 'w') as f_in: 
        f_in.write(content)

def file_get_contents(filename):
    with open(filename, 'r') as f_in: 
        return f_in.read()       

def getRootIframeSource(driver):
    time.sleep(5)
    driver.switch_to.frame(0)
    print("Save root iframe content")
    file_put_contents(dir_path_data+'/iframeRoot.html',driver.page_source)


def getChildsOf(current_level):
    return current_level['childs']

def create_folder_from_url(url, base_url, to_dir):
    href = url.replace(base_url,'')
    dir_parent = os.path.dirname(to_dir+href)
    if not os.path.isdir(dir_parent):
        os.makedirs(dir_parent)    
    return dir_parent
 
def getFilesToDownload(driver):
    links = []
    items = driver.find_elements_by_css_selector("#indexlist a")
    for item in items:
        link = item.get_attribute('href')
        text = item.get_attribute('text')    
        links.append({'href': link, 'text': text})   

    link = links[0]
    dir_parent = create_folder_from_url(link['href'], 'https://visualizador.ide.uy/descargas/datos/', dir_path_data)
    file_name = dir_parent+'/download.csv'
    print('----------->Create csv', file_name)
    pd.DataFrame(links).to_csv(file_name, index=False, quoting=csv.QUOTE_NONNUMERIC)

    return links

def explore(driver, current_level=levels):
    links = []
    items = driver.find_elements_by_css_selector("#indexlist a")
    for item in items:
        link = item.get_attribute('href')
        text = item.get_attribute('text')    
        if text.find(current_level['name']) != -1:
            links.append({'href': link, 'text': text})

    for link in links:
        print('Downloading ..', link['href'], link['text'] )

        file_name = link['text'].replace('/','')+'.html'
        dir_parent = create_folder_from_url(link['href']+file_name, 'https://visualizador.ide.uy/descargas/datos/', dir_path_data)
        file_name = dir_parent+'/'+file_name

        # if not os.path.isfile(file_name):
        driver.find_element(By.LINK_TEXT, link['text']).click()
        file_put_contents(file_name,driver.page_source)
        time.sleep(2)

        # downloading next
        childs = getChildsOf(current_level)
        if childs:
            # has childs
            for child_level in childs:
                explore(driver, child_level )
                time.sleep(3)
        else:
            # is a child
            files_to_download = getFilesToDownload(driver)
            

        driver.find_element(By.LINK_TEXT, "Parent Directory").click() 
        time.sleep(2)    

def download_url(url):
    print("downloading: ",url)
    dir_parent = create_folder_from_url(url, 'https://visualizador.ide.uy/descargas/datos/', dir_path_data)

    file_name_start_pos = url.rfind("/") + 1
    file_name = url[file_name_start_pos:]
    file_name = dir_parent+'/'+file_name 
    if not os.path.isfile(file_name):
        print(" ---> Saving file to ",file_name)

        r = requests.get(url, stream=True)
        if r.status_code == requests.codes.ok:
            with open(file_name, 'wb') as f:
                for data in r:
                    f.write(data)
    else:
        print(" ---> Already downloaded file ",file_name)

    return url

# https://www.quickprogrammingtips.com/python/how-to-download-multiple-files-concurrently-in-python.html
def download_all(directory, pattern):
    for root,dirs,files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                if root.find(pattern) != -1:
                    # print('File ', file, dirs, root)    
                    file_name = root+'/'+file
                    print("Starting to download ..." , file_name)
                    df = pd.read_csv(file_name)
                    # urls = df.iloc[3:,0].tail(2).values
                    urls = df.iloc[3:,0].values
                    # download 5 in parallel
                    results = ThreadPool(5).imap_unordered(download_url, urls)
                    for r in results:
                        print(r)   

                    time.sleep(np.random.randint(30,90))
                    
