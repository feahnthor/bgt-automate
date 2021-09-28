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

def test_logic():
  os.chdir(DirLocation.add_to_bgtown)
  json_object = FileHandler(os.listdir()[0]).open_json()
  url = 'https://backgroundtown.com/Admin/Product/Edit/2514'
  Login(url)
  foo = BaseProduct(**json_object)
  foo.copy_product()
  foo.go_to_variants()
  assert Variants(**json_object).delete_logic == True

