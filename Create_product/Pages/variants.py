"""
Author: Henry F.
Description: Contains functions that should only be called while on a variant product url such as https://backgroundtown.com/Admin/ProductVariant/Edit/{id} 

"""


import logging
from helium import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from Pages.baseproduct import BaseProduct
from locators import Locators
from dir_location import DirLocation
from dir_location import Variables
from dir_location import SubFolder
from file_handler import FileHandler
import os
import re
import sys
import numpy as np
import pathlib
from dotmap import DotMap


"""
Stale element reference 
https://stackoverflow.com/questions/16166261/selenium-webdriver-how-to-resolve-stale-element-reference-exception
"""
logger = logging.getLogger(__name__)

NEW_SIZES = {

}

class Variants(BaseProduct): # Implements BaseProduct

  def __init__(self, **kwargs) -> None:
    # invoke BaseProduct.__init__
    super().__init__(**kwargs) # Allows for this method to call methods variables as though in the baseproduct.py file
    print(self.name) # test to make sure that BaseProduct has been implemented correctly, as self.name is the first thing declared in the __init__()
    # `self` is an object that now contains all functions and variables stored to in in baseproduct.py
    self.url = self.driver.current_url
    self.conf = FileHandler('\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\Update_product\\Config\\.toml').open_toml()
    self.m_design_conf = DotMap(self.conf).designer_code # now able to use dot notation for object/dict : means mapped designer config
    

  def get_combination_elements(self):
    """
    Function to get the buttons that will be clicked, sizes, and columns for each of the 
    attribute combination elements.
    Assumes there is at least 1 element present
    Returns list containing list
    https://stackoverflow.com/questions/28022764/python-and-how-to-get-text-from-selenium-element-webelement-object
    
    If there happens to be a deleted name still remaining. Make sure that things are spelled correctly and the correct case.
      Ex: 8'x10' UltraCloth !=  8'x10' Ultracloth     ---there is a lower case 'c'----
    """
    self.base_image_loc = DirLocation.production + self.designer + SubFolder.web + self.name
    
    elements_list = []
    elements_dict = {}
    # Stores elements for each rows
    row_elements = np.array(self.driver.find_elements_by_css_selector(Locators.attribute_combinations))
    # Store columns from row_elements such as SKU, Attributes
    # row_column_elements = row_elements.find_element_by_css_selector('td')
    for row_element in row_elements:
      WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td')))
      column_elements = row_element.find_elements_by_css_selector('td')
      attribute = column_elements[0].text # use getText() to keep <br> from ignoring \n
      sku = column_elements[3].get_attribute('textContent')
      edit_btn = row_element.find_element_by_css_selector('td input')
      delete_btn = column_elements[-1]
      attribute = re.sub('\\n.*', '', attribute)
      combination_size = re.sub('^.*: ', '', attribute) # can be found in regex notes
      combination_size = re.sub('"', '', combination_size) # string
      size = re.sub(' .*', '', combination_size)
      size = re.sub("'", '', size) # size should now be something like 8x8
      elements_list.append([combination_size, size,  attribute, sku, edit_btn, delete_btn])
      elements_dict[combination_size] = delete_btn
    return elements_list, elements_dict

  def add_variant_image(self):
    """
    ***Page does not need to reload to add an image, so only calling get_combination_elements() once is enough***
    Helium does not seem to be able to recognize when selenium switches to a new window. No idea why it doesn't work in this function
    but is able to work perfectly fine and make helium calls in the BaseProduct.upload_img() method
    so its best to use selenium methods to find elements, then use helium for clicks using the selenium web-element
    """
    click('Attribute Combination')
    combination_elements_list, foo = self.get_combination_elements() # index 0 is the string of the size

    for row_elements in combination_elements_list:
      print(row_elements[0], row_elements[1])
      comb_size, size, attr, sku, edit_btn, del_btn = row_elements
      file = pathlib.Path(f'{self.base_image_loc}_{row_elements[1]}.jpg') # now a file object
      if file.exists():
        logger.info(f'Found image variant {file}')
        edit_btn.location_once_scrolled_into_view
        click(edit_btn)
        browser_windows = self.driver.window_handles
        self.driver.switch_to.window(browser_windows[-1]) # switch to newest browser
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.image_tab)))
        img_tab = self.driver.find_elements_by_css_selector(Locators.image_tab)
        click(img_tab[1])
        BaseProduct.upload_img(self, pop_up_window=True, img_name_variant=file)
        self.close_window() # closes window without saving to prevent staleelement exception
    variant_top = self.driver.find_element_by_id(Locators.top_of_variant_page)
    variant_top.location_once_scrolled_into_view
  
  def delete_combination(self):
    """
    ***Deleting an element will reload the page, will need to call get_combination_element in a loop to
    avoid Stale Element Exceptions***
    ***An alert pops up after hitting delete with options 'Ok' and 'Cancel'***
    # Need to increase speed of these loops, much slower than `delete_sizes()`
    """

    click('Attribute Combination')
    try:
      row_elements = np.array(self.driver.find_elements_by_css_selector(Locators.attribute_combinations))
      total_combinations = len(row_elements)
      while total_combinations != len(self.sizes): # becomes an infinite loop if extra sizes were deleted manually in delete_sizes as each attribute will no longer match when on this page
        foo, combination_elements_dict = self.get_combination_elements()
        for size, del_btn in combination_elements_dict.items():
          foo, combination_elements_dict = self.get_combination_elements()
          if size not in self.sizes:
            total_combinations = len(foo)
            combination_elements_dict[size].location_once_scrolled_into_view
            click(combination_elements_dict[size])
            Alert().accept() #page will be refreshed after and elements will become stale
            WebDriverWait(self.driver, 10).until(EC.staleness_of(combination_elements_dict[size]))
    
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.attribute_combinations)))
    except Exception as e:
      logger.critical(f'{self.name}\n{self.driver.current_url}\n', sys.stderr, f'Something went wrong in Variants.delete_combinations()n\nProduct: {self.driver.current_url} \nException: {e}' )
      pass
    variant_top = self.driver.find_element_by_id(Locators.top_of_variant_page)
    variant_top.location_once_scrolled_into_view 
    logger.info(f'Attribute Combinations deleted')

  def split_list(self, list, amount=2, filler=None):
    """ 
    ***Currently not in use by this program, but is still a useful function***
    Splits an array/list into equal smaller lists. Default amount is set to 2
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
        completed_chunks.append(chunk) # add the list containing chunks to the whole 
      except Exception as e:
        logger.critical(f'{self.name}' f'{sys.stderr}\nSpliting failed, please ensure that a list was sent through and the amount was a positive integer\
          {e}')
      if len(chunk) < amount:
        # chunk.append([filler for y in range(amount - len(chunk))]) # add filler content to chunk
        np.append(chunk, [filler for y in range(amount - len(chunk))])
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
    """
    this function may no longer be needed as selenium has the expected conditions of 
    `new_window_is_opened(current_handles)` and `number_of_windows_to_be(num_windows)`
    https://www.selenium.dev/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.expected_conditions.html#module-selenium.webdriver.support.expected_conditions
    """
    windows = self.driver.window_handles
    if len(windows) > 1:
      print(f'Attempting to close second window {self.driver.close()}')
      self.driver.switch_to.window(windows[0])
    else:
      self.driver.switch_to.window(windows[0])

  def delete_logic(self):
    """
    ------Deprecated: delete sizes does this as a side effect--------
    ***Major issue that keeps presenting a stale element exception after successfully deleting
    a item, trying to call logic_elements[i] fails --COMPLETED used expected condition .stalenessof
    https://stackoverflow.com/questions/60535663/how-to-scroll-a-web-page-down-until-specific-button-to-click
    Used ids in id_list as references to find elements using ids since they do not change on reload thanks to Jarred,
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
          WebDriverWait(self.driver, 10).until(EC.staleness_of(delete_btn))
          WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.attribute_logic_list_id)))
        if len(total_elements) == len(self.sizes): #should be done.
          break
    except Exception as e:
      logger.critical(f'{self.name}', sys.stderr, f'Could not find Logic delete button\nProduct: {self.driver.current_url} \nException: {e}' )
      pass
    variant_top = self.driver.find_element_by_id(Locators.top_of_variant_page)
    variant_top.location_once_scrolled_into_view  

  def update_codes(self):
    """
    Need to update to take in a unknown amount of attributes
    ***issue where exception pops up on attributes page  ***
    """

    designer = re.sub('\s', '_', self.designer.lower()) # will provide the string used to access the config and get the right product code
    nf_code = self.m_design_conf[designer]['new_fab']
    reg_code = self.m_design_conf[designer]['regular']
    handles = self.driver.window_handles
    cur_url = self.driver.current_url


    try: 
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_2).exists) # to the right of "Mentor"
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_2))
      wait_until(Text(self.edit).exists)
      
      ############## Add Regular Code ###############
      click(Text(self.edit, to_right_of='40')) # Regular designs have a price of $40
      WebDriverWait(self.driver, 5).until(EC.number_of_windows_to_be(2)) # wait for new window to open
      self.driver.switch_to.window(self.driver.window_handles[-1])
      wait_until(Text(Locators.code_name).exists)
      write(reg_code, into=TextField(to_right_of=Locators.code_name))
      write(reg_code, into=TextField(to_right_of=Locators.code_f_name))
      click('Save')

      self.driver.switch_to_window(handles[0])
      wait_until(Text(self.edit).exists)

      ############# Add NewFab code ################
      click(Text(self.edit, to_right_of='12.5'))
      WebDriverWait(self.driver, 5).until(EC.number_of_windows_to_be(2))
      wait_until(Text(Locators.code_name).exists)
      write(nf_code, into=TextField(to_right_of=Locators.code_name))
      write(nf_code, into=TextField(to_right_of=Locators.code_f_name))
      click('Save')
      self.driver.switch_to_window(handles[0])
    except Exception as e:
      logger.warning(f'Unhandled exception  when trying to Update Codes for designer in config {designer} {self.name} \n{self.driver.current_url}\n{e}')
    finally:
      #### Go back to variants ####
      self.driver.switch_to_window(handles[0])
      go_to(cur_url)
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)

  def update_price_aci(self, *args):
    """
    ***NO LONGER VALID***
    """
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
    # self explanatory
    go_to(self.url)

  def delete_size(self):
    """
    1. Takes in no arguments, uses similar method to delete fields as `Varants.delete_combination()`
    Notes:
      1. Any New size added after that contains a special character besides " can be handled in `size_compare` variable, its best to create a `sanitize_string()` function
      2. `nth-of-type` can be found in mozilla docs is Extremely useful as before i had to create my own functions to separate the array/list of table elements. see `get_combination_elements()` if it hasn't been
      deleted
    2. This MUST run after delete_logic as Infigo will not allow a size to be deleted if the logic still exists.
      *** ABOVE IS NO LONGER TRUE as of 10/13/21. Infigo seems to have updated so if a size is deleted here, it also deletes the logic***
    3. `count` needS to be set back to 0 once a size has been deleted so it starts
    """
    # To change these values go to Locators file
    url = self.driver.current_url
    try:
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))
    except StaleElementReferenceException as e:
      logger.warning(f'Stale Element exception  when trying to find {Locators.attribute_label_1} in delete_logic {self.name} \n{self.driver.current_url}')
      refresh() # after refresh need to get back to Attributes tab
      click(Locators.attribute)
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))

    name_selector = Locators.variant_name
    del_btn_selector = Locators.var_delete_btn
    row_selector = Locators.var_row_selector

    # nth-of-type(11) ensures delete field is present on the dom too
    WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, row_selector)))
    WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, del_btn_selector)))

    try:
      size_list = np.array(self.driver.find_elements_by_css_selector(name_selector))
      delete_btn_list = np.array(self.driver.find_elements_by_css_selector(del_btn_selector))
      while len(delete_btn_list) != len(self.sizes):
        size_list = np.array(self.driver.find_elements_by_css_selector(name_selector))
        delete_btn_list = np.array(self.driver.find_elements_by_css_selector(del_btn_selector))
        count = 0

        for i in range(len(delete_btn_list)): # assumption is that both size and delete_btn are sorted by their order
          size_list = np.array(self.driver.find_elements_by_css_selector(name_selector))
          delete_btn_list = np.array(self.driver.find_elements_by_css_selector(del_btn_selector))
          # so the goal is to use the index to remove the corresponding size
          size_compare = re.sub('"', '', size_list[count].get_attribute('textContent')) # get rid of double quotes Ex: 3'9"x5' NewFab
          count += 1 # want count to keep increasing if value is an accepted size
          if size_compare not in self.sizes:
            logger.info(f'Size {size_compare} not in {self.sizes} deleting Attribute')
            delete_btn_list[count - 1].location_once_scrolled_into_view # count - 1 to use the same value as size_compare
            click(delete_btn_list[count - 1])
            Alert().accept() # page will be refreshed after and elements will become stale
            WebDriverWait(self.driver, 10).until(EC.staleness_of(delete_btn_list[i])) # waits for button to actually be off the DOM 
            count = 0 # reset count back to 0 once size has been deleted. *IMPORTANT*
    except Exception as e:
      logger.critical(f'{self.name} \n{self.driver.current_url}\n'  f'Unhandled exception {e}')
      pass
    finally: # will always be executed, not matter if there is an error
      go_to(url)
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)
  