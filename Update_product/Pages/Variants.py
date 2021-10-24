from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import logging
import os
import sys
import time
import numpy as np
from natsort import natsorted # sorts into human understandable sort. So no [1, 11, 12, 3] but [1, 3, 11, 12]
from dotmap import DotMap # pip install dotmap, allows for dict objects to be accessed using periods

sys.path += ['\\\\work\\tech\\henry\\programs\\python\\bgt-automate\\create_product'] # adds to path
from file_handler import FileHandler

logger = logging.getLogger(__name__)

class Variants:
  """
  Functions to make changes to existing products on their variants pages, only works as Multithreading if `helium`
  isn't used. 
  """
  def __init__(self) -> None: 
    # unlike the functions from Create_product drivers must go in the individual functions and not be declared in the init  
    self.conf = FileHandler('\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\Update_product\\Config\\.toml').open_toml()
    self.m_conf = DotMap(self.conf).var # now able to use dot notation for object/dict : means mapped_config
    self.start_time = time.perf_counter()

  def sort_sizes(self, driver, order_difference=5):
    """
    :param driver: (Webdriver Object) takes an instance of the webdriver object. If there is an attribute error check driver_setup.py 
        to make sure the driver was setup correctly. Drivers should have access to a simple method like `driver.current_url`
    :param order_difference: (int) of what each size will be sorted by. i.e. 0, 5, 10, 15
    """
    m = self.m_conf
    url = driver.current_url

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, m.attr_tab)))
    attribute_tab = driver.find_element_by_css_selector(m.attr_tab)
    attribute_tab.click() # find Attributes tab then clicks it

    # Go to sizes
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, m.get_size_page)))
    try:
      size_link = driver.find_element_by_css_selector(m.get_size_page)
      driver.get(size_link.get_attribute('href'))

    except StaleElementReferenceException as e:
      logger.warning(f'Stale Element exception  when trying to find Size Link in sort_sizes() \n{driver.current_url}')
      driver.refresh()
      WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, m.get_size_page)))
      size_link = driver.find_element_by_css_selector(m.get_size_page)
      driver.get(size_link.get_attribute('href'))

    ########## Actual Start of Sort ###############
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.row)))
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, m.size.size_name)))
    original_window = driver.current_window_handle

    try:
      size_list = np.array(driver.find_elements_by_css_selector(m.size.size_name))
      edit_btn_list = np.array(driver.find_elements_by_css_selector(m.size.edit_btn))

      readable_size_list = [size.get_attribute('textContent') for size in size_list] # get values from position 2 onwards
      sorted_size_list = natsorted(readable_size_list) # use the index * 5 to set display order
      _sorted = False

      ####### Check to make sure things are sorted before looping ###### 
      # compare_sort_size_list = sorted_size_list
      # compare_readable_size_list = readable_size_list
      # try:
      #   compare_sort_size_list.remove
      # except Exception as e:
      #   pass

      if sorted_size_list == readable_size_list:
        _sorted = True
        logger.info(f'This product is already sorted \n{sorted_size_list}')

      while _sorted != True:
        # Check to make sure that current sort is the same as sorted_size
        count = 0
        for i in range(len(edit_btn_list)): # This is only too loop through the total number of sizes
          """
          Does not do its own sort, merely uses the natsorted() result as a reference to what each Display order item should
            be. If there
          1. We find elements again inside the for loop to prevent a StaleElementError on the second and subsequent loops
          """
          WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.edit_btn)))
          WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, m.size.edit_btn)))
          size_list = np.array(driver.find_elements_by_css_selector(m.size.size_name))
          edit_btn_list = np.array(driver.find_elements_by_css_selector(m.size.edit_btn))
      
          attr_dict = dict(zip(readable_size_list, edit_btn_list)) # Stores size as key and Edit button as value
          sorted_size_key = sorted_size_list[i]
          
          attr_dict[sorted_size_key].location_once_scrolled_into_view # Make sure item is scroll in order to click and avoid errors

          attr_dict[sorted_size_key].click() # Use size as key to access the related button store in attr_dict
          WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
          driver.switch_to.window(driver.window_handles[-1]) # switch to newest windows to edit size

          ##### Update Display order ######
          WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, m.size.window.order)))
          if 'NewFab' not in sorted_size_key: # makes it so if a value like NewFab is encountered the sequence continues, so no 0, 0, 10, 15
            count += 1 
            new_order = str(count*order_difference)
            print(f'Size: {sorted_size_key}: {count} * {order_difference} = {count*order_difference}: passed {new_order} \t\t{driver.current_url}')
          ##### Assign Custom Display Order ######
          if 'NewFab' in sorted_size_key:
            new_order = '0'
          order_field = driver.find_element_by_id(m.size.window.order)
          order_field.clear()

          ##### Close Window #######
          save_btn = driver.find_element_by_css_selector(m.size.window.save_btn)
          save_btn.click()
          WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
          driver.switch_to.window(original_window)
        _sorted = True # Exit Loop

      elapsed_time = time.perf_counter() - self.start_time
      logger.info(f"Elapsed time for Variants sort sizes: {elapsed_time:0.4f} seconds")
    except Exception as e:
      logger.critical(f'Unhandled exception in \\Update_product\\Pages\\variants.py while trying to sort_sizes() \n{driver.current_url}\n{e}')