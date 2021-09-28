from Pages.login import Login
from locators import Locators
from Pages.baseproduct import BaseProduct
from dir_location import DirLocation
from file_handler import FileHandler
from Pages.variants import Variants
from helium import *
import logging
import logging.config
from pythonjsonlogger import jsonlogger #https://github.com/madzak/python-json-logger
## loggin with python https://blog.guilatrova.dev/how-to-log-in-python-like-a-pro/
import os
import shutil
from pathlib import Path
#selenium.common.exceptions.UnexpectedAlertPresentException
#selenium.common.exceptions.StaleElementReferenceException
# Path.cwd('\\\\work\\tech\\Henry\\Programs\\Python\\Infigo Automation\\automation pom')
logging.config.dictConfig(FileHandler('\\\\work\\tech\\Henry\\Programs\\Python\\Infigo Automation\\automation pom\\loggin_config.json').open_json())
# Create logger
logger = logging.getLogger(__name__)


def main():
  os.chdir(DirLocation.add_to_bgtown)
  first_json_object = FileHandler(os.listdir()[0]).open_json()
  url, is_floor = get_base_url(first_json_object) #determines which template url to use

  Login(url)
  # Login('https://backgroundtown.com/Admin/Product/Edit/2514')

  logger.info(f'Retrieving json from {DirLocation.add_to_bgtown}')
  count = 0
  for file in os.listdir():

    json_object = FileHandler(file).open_json()
    logger.info(f'Retrieved data from {json_object}.\n {count}/{len(os.listdir())}')
    count+=1
    url, is_floor = get_base_url(json_object)

    wait_until(Text(Locators.save_and_continue).exists) # important to avoid reloading the page
    go_to(url)
    
    prod_home = BaseProduct(**json_object)
    variants_page = Variants(**json_object)
    logger.info(f'Available sizes {len(json_object["sizes"])}: {json_object["sizes"]}')
    prod_home.copy_product()
    prod_home.add_tags()
    prod_home.prod_img()
    prod_home.add_category()
    prod_home.save_and_edit()
    wait_until(Text(Locators.published).exists)
    if is_floor != True: # floors do not have attribute logic to delete
      prod_home.go_to_variants()
      variants_page.delete_logic()
    logger.info(f'Done with {file}. \n Moving to {DirLocation.bgt_done}')
    shutil.move(file, DirLocation.bgt_done)
  logger.info(f'PROGRAM COMPLETED SUCCESSFULLY. Completed {count} Products')
  

def get_base_url(json_object):
  # Determine product type based on json key
  is_floor = False
  if 'floor_themes' in json_object:
    is_floor = True
    logger.info('Floor found! Using floor layout')
    url = Locators.base_floor_prod_url
    return url, is_floor
  else:
    logger.info('No floor found! Using backdrop layout')
    url = Locators.base_prod_url
    return url, is_floor



if __name__ == '__main__':
  main()