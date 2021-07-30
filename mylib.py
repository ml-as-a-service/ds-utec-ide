from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

import time 

import os 
 
# Download Dir
dir_path_download = os.path.abspath(os.getcwd())+'/download/'


def getDriver(url): 
    # settings
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : dir_path_download}
    chromeOptions.add_experimental_option("prefs",prefs)
    chromedriver = "chromedriver"

    driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

    # Open the main page
    driver.get(url)    
    
    time.sleep(3)
    # click + for Relieve
    ele = driver.find_elements_by_xpath("//*[contains(text(), 'Relieve (IDEuy)')]/parent::*")
    ele[0].find_element(By.CSS_SELECTOR, "i.fa").click()
    time.sleep(2)

    # click MDT Nacional
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
    file_put_contents(dir_path_download+'/iframeRoot.html',driver.page_source)

