
import logging
from helium import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Pages.baseproduct import BaseProduct
from locators import Locators
from dir_location import DirLocation
from dir_location import Variables
from dir_location import SubFolder
import os
import re
import sys
import numpy as np
"""
Stale element reference 
https://stackoverflow.com/questions/16166261/selenium-webdriver-how-to-resolve-stale-element-reference-exception
"""
logger = logging.getLogger(__name__)

class Variants(BaseProduct):

  def __init__(self, **kwargs) -> None:
    # invoke BaseProduct.__init__
    super().__init__(**kwargs)
    print('Variants', self.name)

  def add_variant_image(self):
    """
    
    """
    self.images = Locators.images
    self.web = SubFolder.web
    self.base_image_loc = DirLocation.production + self.designer + self.web + self.name
    click('Attribute Combination')
    combination_elements = np.array(self.driver.find_elements_by_css_selector(Locators.attribute_combinations))
    print(len(combination_elements))
    
    rows_of_td = self.split_list(combination_elements, amount=7)

    # list slice method to start at the first element, then get every 6th element until the last which is the length of the list
    #splits array into parts. Does not split evenly which is why we used split_list() 
    # rows_of_td = np.array_split(combination_elements, len(combination_elements)//6)

    count = 0
    for td_row in rows_of_td:
      print(td_row[0].get_attribute('textContent'))
      for td_element in td_row:
        print(td_element)
        print(count, '. ', td_element.get_attribute('textContent'))
        count +=1
        if "8'x6'" in rows_of_td[0]:
          print('dhfafshdsdfh')

  def split_list(self, list, amount=2, filler=None):
    """ 
    ***Should be made into a help function in another class***
    taken from https://appdividend.com/2021/06/15/how-to-split-list-in-python/
    :param list: The (list) that needs to be separated 
    :param amount: (int) value to separate each list/array into, defaults to 2 
    :param filter: Can be any type, will fill any remaining indexes of the list/array, default none
      Ex: [[1,2,5,20], [21, 28, None, None, None]] 
    """
    completed_chunks = []
    for i in range(0, len(list), amount):
      try:
        chunk = list[i: amount+i]
        completed_chunks.append(chunk)
      except Exception as e:
        logger.critical(f'{sys.stderr}\nSpliting failed, please ensure that a list was sent through and the amount was a positive integer\
          {e}')
      if len(chunk) < amount:
        chunk.append([filler for y in range(amount - len(chunk))])
    
    return completed_chunks
  # New Page Attributes
  def edit_combinations(self):
    """
    Assumes attribute combinations are already present,
    Assumes SKUs are present as well
    Must have sizes be visible before scrolling on the current window or get a LookupError
    Should only call upload method if there exist a variant size of the image
    Do not need to upload the normal version of the image here as that has been done in the baseProduct() class
    """
    self.images = Locators.images
    self.web = SubFolder.web
    self.foo = DirLocation.production + self.designer + self.web + self.name
    self.img_type = '.jpg'
    click('Attribute combinations')
    scroll_down(num_pixels=380)
    for v in self.sizes:
      "v is the (string) of the size in this case ex. 8x20 Background"
      a = re.sub(' RubberMat', '', v)
      a = re.sub(' UltraCloth', '', a)
      a = re.sub(' NewFab', '', a)
      
      variant_size = f'_' + re.sub("'", "", a)
      
      variant_size2 = f' ' + re.sub("'", "", a)
      self.variant_image = self.foo + variant_size + self.img_type
      self.variant_image2 = self.foo + variant_size2 + self.img_type
      print(f'trying {self.variant_image}\n')
      if os.path.isfile(self.variant_image) or os.path.isfile(self.variant_image2):
        
        print(self.variant_image, 'EXIST')
        while True:
          try:
            print(v)
            #value for pixels gotten from $("#attributecombinations-grid").offset().top + window.screenY;
            wait_until(Button(self.edit).exists)

            scroll_down(num_pixels=20)
            print('buttttosdfhdsdf',Button(self.edit, to_right_of=Text(v)))
            
            click(Button(self.edit, to_right_of=Text(v)))
            wait_until(Text(self.images).exists)
            click(self.images)
            BaseProduct.upload_img(self, pop_up_window=True, img_name_variant=self.variant_image)
            break
          except Exception as e:
            print('Caught ', e, 'at size', v)
            self.close_window(self)
            
      else:
        print(self.variant_image,  'DOES NOT EXIST')
        
        pass
    # go_to(Locators.base_prod_url)       

  def close_window(self):
    windows = self.driver.window_handles
    if len(windows) > 1:
      print(f'Attempting to close second window {self.driver.close()}')

  def delete_logic(self):
    """
    ***Major issue that keeps presenting a stale element exception after successfully deleting
    a item, trying to call logic_elements[i] fails --COMPLETED
    https://stackoverflow.com/questions/60535663/how-to-scroll-a-web-page-down-until-specific-button-to-click
    Used id in id_list thanks to Jarred,
    ***Searching by id attribute to find the id must be done with find_element_by_id()***
    """
    try:
      logic_elements = self.driver.find_elements_by_css_selector(Locators.attribute_logic_list_id)
      id_list = [element.get_attribute('id') for element in logic_elements]

      for id in id_list:
        wait_until(Text('Show').exists)
        total_elements = self.driver.find_elements_by_css_selector(Locators.attribute_logic_list_id)
        current_element = self.driver.find_element_by_id(f'{id}')
        size = current_element.find_elements_by_css_selector('span')[3].get_attribute('textContent')
        delete_btn = current_element.find_element_by_css_selector(f'a')
        size = re.sub('"', '', size)
        if size not in self.sizes:
          delete_btn.location_once_scrolled_into_view
          delete_btn.click()
          WebDriverWait(self.driver, 30).until(EC.staleness_of(delete_btn))
          WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.attribute_logic_list_id)))
        if len(total_elements) == len(self.sizes): #should be done.
          break
    except Exception as e:
      logger.critical(sys.stderr, f'Could not find Logic delete button\nProduct: {self.driver.current_url} \nException: {e}' )
      pass
    variant_top = self.driver.find_element_by_id(Locators.top_of_variant_page)
    variant_top.location_once_scrolled_into_view  

  def update_codes(self):
    """
    Need to update to take in a unknown amount of attributes
    ***issue where exception pops up on attributes page  ***
    """
    self.codes = self.prod_attr[Variables.json_codes][self.designer.lower()].split(',')
    handles = self.driver.window_handles

    print(f'UPDATING CODES! CODES AVAIALABLE: {self.codes}')
    wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_2).exists)
    click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_2))
    wait_until(Text(self.edit).exists)
    
    click(Text(self.edit, to_right_of='40'))
    wait_until(Text(Locators.code_name).exists)
    write(self.codes[0], into=TextField(to_right_of=Locators.code_name))
    write(self.codes[0], into=TextField(to_right_of=Locators.code_f_name))
    click('Save')
    self.driver.switch_to_window(handles[0])
    wait_until(Text(self.edit).exists)
    click(Text(self.edit, to_right_of='12.5'))
    wait_until(Text(Locators.code_name).exists)
    write(self.codes[1], into=TextField(to_right_of=Locators.code_name))
    write(self.codes[1], into=TextField(to_right_of=Locators.code_f_name))
    click('Save')
    self.driver.switch_to_window(handles[0])
    BaseProduct.go_to_variants(self)

  def update_price_aci(self, *args):
    handles = self.driver.window_handles

    wait_until(Text('Tier prices').exists)
    click(Locators.attribute)
    print(f'UPDATING Prices! Prices AVAILABLE')
    wait_until(Text(Locators.attribute_edit).exists)
    # total = re.findall('[0-9]',Text(Locators.attribute_edit).value)[0]
    
    click(Locators.attribute_edit)

    # wait_until(Button('Edit').exists)
    
    print('bttuon sdfsdfd')                                                                            
    # foo = re.sub('[0-9]+', Text(Locators.attribute_edit).value)[0]
    
    # print('Total', foo)
    # click(Text(Locators.attribute_edit))
    # wait_until(Text(self.edit).exists)
    wait_until(Button('Edit').exists)
    edit_btns = find_all(Button('Edit'))
    # print(edit_btns,)
    print('Total sizes available', len(edit_btns))
    for i in range(len(edit_btns)):
      print('before while true')
      while True:
        print('before try')
        try:
          print('before conditions', print(edit_btns[i]))
          wait_until(Text('Edit').exists)
          print('found button')
          # click(edit_btns[i])
          click('edit')
          print('after click')
          wait_until(Text(Locators.price).exists)
          price = int(TextField(to_right_of=Locators.price).value)
          print('PRICE:', price)
          if price == 72:
            write('84.50', into=TextField(to_right_of=Locators.price))
            click('Save')
            self.driver.switch_to_window(handles[0])
          elif price == 110:
            write('122.50', into=TextField(to_right_of=Locators.price))
            click('Save')
            self.driver.switch_to_window(handles[0])
          else:
            new_price = price + 40
            write(new_price, into=TextField(to_right_of=Locators.price))
            click('Save')
            self.driver.switch_to_window(handles[0])
          break
        except Exception as e:
          print('Caught ', e, 'update price aci')
          break
          # BaseProduct.close_window(self)
    pass
  
  def go_back_to_variant(self):
    wait_until(Text(Locators.back_to_variants).exists)
    click(Text(Locators.back_to_variants))
    click(Locators.attributes)

  def delete_sizes(self):
    wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
    click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_2))
    pass
