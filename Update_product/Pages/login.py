from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import os
import sys
from dotmap import DotMap # pip install dotmap, allows for dict objects to be accessed using periods

sys.path += ['\\\\work\\tech\\henry\\programs\\python\\bgt-automate\\create_product'] # adds to path
from credentials import Credentials
from file_handler import FileHandler
from dir_location import DirLocation


logger = logging.getLogger(__name__)

class Login:
  def __init__(self) -> None:
    directory = DirLocation()    
    self.conf = FileHandler(f'{directory.update_prod_location}\\config\\.toml').open_toml()
    self.m_conf = DotMap(self.conf).elements # now able to use dot notation for object/dict : means mapped_config
  
  def login(self, driver): # driver needs to remain driver and not added to self or fields will only populate 1 window
    
    """
    :param driver: Single Selenium webdriver object, one for each driver instance
    Multithreaded version: 

    After testing, Multithreading is not possible while using helium as in the few seconds of thought it took to consider
        there is no way to directly use a specific selenium WebDriver object in helium. With the default Selenium methods
        we are able to make changes to each browser instance individually as driver.find_element_by_id() references a specific
        instance of a browser.
    """
    m = self.m_conf
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, m.login.email)))
    email_field = driver.find_element_by_id(m.login.email)
    email_field.clear()
    # type email
    email_field.send_keys(Credentials.email)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, m.login.password)))
    # find password field
    password_field = driver.find_element_by_id(m.login.password)
    password_field.clear()
    # type password
    password_field.send_keys(Credentials.password)
    submit = driver.find_element_by_class_name(m.login.btn)
    submit.click()