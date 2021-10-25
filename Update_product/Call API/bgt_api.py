from typing import List
import requests
import json
from bs4 import BeautifulSoup as sp
import time
import dotmap
import sys
import numpy as np

sys.path += ['\\\\work\\tech\\henry\\programs\\python\\bgt-automate\\create_product'] # adds to path
from file_handler import FileHandler

class Bgt_Api:
  """
  Functions to get data from backgroundtown as quickly as possible
  backgroundtown required "Basic" authorization, as demonstrated here
          answer show here: https://stackoverflow.com/questions/19069701/python-requests-library-how-to-pass-authorization-header-with-single-token
          ***Requests natively supports basic auth only with user-pass params, not with tokens.

      You could, if you wanted, add the following class to have requests support token based basic authentication:***
  """
  def __init__(self) -> None:
    # unlike the functions from Create_product `drivers` must go in the individual functions and not be declared in the init  
    self.conf = FileHandler('\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\Update_product\\Config\\.toml').open_toml()
    self.m_conf = DotMap(self.conf).bgt_api # now able to use dot notation for object/dict : means mapped_config
    self.start_time = time.perf_counter()
    self.headers = {'Authorization': f'Basic {self.m_conf.key}'}

  def get_url_ids(self) -> List:
    """
    
    """    
    with requests.Session() as session:
      session.headers.update(self.headers)
      res = session.get('https://backgroundtown.com/services/api/catalog/productlist')
      product_id_list = np.array(json.loads(res.text))
      for id in product_id_list:
        results = session.get(f'https://backgroundtown.com/p/{id}')
        soup = sp(results.content, 'html.parser')
        