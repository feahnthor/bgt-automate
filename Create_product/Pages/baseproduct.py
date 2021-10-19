"""
Author: Henry F.
Description: Contains functions that should only be called while on a base product url such as https://backgroundtown.com/Admin/Product/Edit/{id} 
    Things to note: 
      1. Only one function `upload_img()` is called here and also variants.py, as the upload of an image is exactly the same, only change what is appended to the image name
      2. If any changes has been made to the baseproduct make sure to call save_and_edit(). *add_tags()* does not save unless `save_and_edit()` is called
      3. Function `go_to_variants()` should be the last to be called as it switches to the variants page and should start using variants.py functions
"""


from selenium.webdriver.support import wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  # good for options
from selenium.common.exceptions import *

from locators import Locators
from dir_location import DirLocation
from dir_location import Variables
from dir_location import SubFolder
from helium import * # to see available methods hit F12 while using VS Code or Visual Studio
import collections
import re
import os
import logging
import sys

logger = logging.getLogger(__name__)

DESIGNER_CODE = {
  "lori nordstrorm" : "82100823,82100844",
  "jim churchill" : "82100824,82100843",
  "annie marie" : "82100825,82100834",
  "cindy romano" : "82100826,82100835",
  "dennis hammon" : "82100827,82100836",
  "doran wilson" : "82100828,82100837",
  "mark lane" : "82100829,82100838",
  "michael mowbray" : "82100830,82100839",
  "nancy emmerich" : "82100831,82100840",
  "tessa cole" : "82100832,82100841",
  "thom rouse" : "82100833,82100842",
  "christie newell" : "82100846,82100845",
  "cheri hammon" : "82100847,82100848",
  "jeni b" : "82100849,82100850",
  "molly long" : "82100851,82100852",
  "mitch green" : "82100853,82100854",
  "paul kestel" : "82100854,82100856",
  "chris garcia" : "82100857,82100858",
  "Barbara Yonts": "82100869",
}

class BaseProduct:
  def __init__(self, key=None, value=None, **kwargs) -> None:
    """
    Key: string containing key which is a product name
    value: nested dictionary
    :param **kwargs accepts unpacked dictionary argument
    Example calling from main.py: BaseProduct(**dict_object)

    *** For methods that only modifies an existing product I will add these values ****
    """
    self.name = kwargs['name']
    self.designer = kwargs['designer']
    # self.code = DESIGNER_CODE[self.designer.lower()]
    self.sizes = kwargs['sizes']
    self.colors = kwargs['colors']
    self.tags = kwargs['tags']
    if 'themes' in kwargs:
      self.themes = kwargs['themes']
    elif 'floor_themes' in kwargs:
      self.themes = kwargs['floor_themes']
    else:
      logger.warn(f'No Theme provided! {self.name}')
    self.driver = get_driver()

    self.add = Locators.add_picture
    self.edit = Locators.edit
    self.popup_esc = Locators.popup_esc_tab
    self.update = Locators.update
    self.copy = Locators.copy_prod_btn
    self.edit = Locators.edit
    self.popup_esc = Locators.popup_esc_tab
    self.update = Locators.update
    self.copy = Locators.copy_prod_btn


  def copy_product(self):
    """
    Creates a copy of current product, best to create a template product to copy from
    to avoid corrupting the originals
    """
    self.name_field = Locators.new_prod_name
    copy_img = Locators.copy_images_checkbox
    self.check = Locators.copy_extended_checkbox # should only be used for non basic products such as Dynamic ones

    wait_until(Text(self.copy).exists)
    try:
      click(self.copy)
    except Exception as e:
      logger.critical(self.name, sys.stderr, f'Could not find Copy Product Button\nProduct: {self.driver.current_url} \nException: {e}' )
      if self.driver != None:
        kill_browser()
      sys.exit(1)
    write(self.name, into=self.name_field)
    click(CheckBox(copy_img)) # deselects the copy image option that is default
    click(self.copy)
    # Ensures that the copy product window no longer exist before trying to find anything else
    #https://stackoverflow.com/questions/24928582/expectedcondition-invisibility-of-element-located-takes-more-time-selenium-web
    WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((By.ID, Locators.copy_window)))
    self.current_url = self.driver.current_url
    logger.info(f'Product copied successfully.\nCurrent url: {self.current_url}')
    click(Locators.published) # Sets product to be visible to customers
    click(Locators.show_in_search) # Sets products to be visible in search results


  def save_and_edit(self):
    '''
    ***Must be called second to last as go_to_variants() will be called next***
    '''
    self.save = Locators.save_and_continue
    logger.info('Saving and Continuing Edit...')
    WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, Locators.tag_window)))
    self.copy_prod_btn_id.location_once_scrolled_into_view
    click(self.save)
    WebDriverWait(self.driver, 30).until(EC.staleness_of(self.copy_prod_btn_id))

  def upload_img(self, web=SubFolder.web, pop_up_window=False, img_name_variant=None, img_type='.jpg'):
    """
    Primarily made to  upload web icon image products,
    [x] ***will need to update handling random files - COMPLETED***
    :param web: The (string) of a subfolder i.e. \\web\\
    :param pop_up_window: Should only be True if this ```upload file``` appears within a \
    popup window as there are more steps needed to close it to return to main window
    :param img_name_variant: The (string) of a text to append to file name.
      Ex: Forest Loner.jpg vs Forest Loner_8x10.jpg
    :param img_typ: The (string) of the file extention, default is .jpg
    ***Will need to update parameters to either be variables in __init__ or remain here***
    ***Need to create check for image already existing***
    """
    # WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, Locators.product_edit_tabs)))
    # wait_until(Text('Pictures').exists)
    self.web = web
    self.upload = Locators.upload # Expected value to be "Upload a file". Open locators.py and search for "upload" to make edits
    self.pop_up = pop_up_window
    self.img_name_variant = img_name_variant
    self.img = DirLocation.production + self.designer + self.web + self.name
    self.img_type = img_type

    if self.img_name_variant != None:
      self.img = self.img_name_variant._str
    else:
      self.img = self.img + self.img_type
    logger.info(f'Image to upload in upload_img() {self.img}')
    if os.path.isfile(self.img):
      click(self.upload)
      logger.info(f'Available windows: {self.driver.window_handles}')
      write(self.img)
      press(ENTER+ENTER)
      wait_until(Text(self.add).exists)
      click(self.add)
      if self.pop_up == True:
        click(self.popup_esc)
        # click(self.update) # DO NOT WANT THE PAGE RELOADED TO GET A STALEELEMENT
        logger.info('Attribute combination page upload image pop closed successfully')
    else:
      logger.warning(f'{self.img} did not exist {self.driver.current_url}')
      pass
  def prod_img(self):
    """
    Clicks image tab then calls upload image
    """
    self.pic_tab = Locators.picture_tab
    self.url = self.driver.current_url

    wait_until(Text(self.pic_tab).exists, timeout_secs=10)
    click(self.pic_tab)
    BaseProduct.upload_img(self)

  def add_tags(self):
    """

    ***Does not yet handle new tags - `Complete`***
    For scrollable UI elements that do not create their own window handles such as list using methods\
      scroll_down(), press(```Keys for scrolling```) only affects the main window \
        driver().location_once_scrolled_into_view allows for scrolling into view
          https://stackoverflow.com/questions/41744368/scrolling-to-element-using-webdriver
    """
    tags = self.tags + [self.designer] + self.colors + self.themes # designer is a string, has to be made into a array for concatination
    # Resolves Karas issue of not having to type the tags into the intranet form. desinger, colors, and themes will be added to the tags
    self.tag_loc = Locators.tag_class
    wait_until(Text(self.copy).exists)
    self.copy_prod_btn_id = self.driver.find_element_by_id('copyproduct')

    press(END)

    click(TextField(to_right_of=Locators.tag_field))
    try:
      wait_until(Text(Locators.first_tag).exists) # wait for first element in tags to be visible
    except Exception as e:
      logger.critical(self.name, sys.stderr, f'Could not find Copy Product Button\nProduct: {self.driver.current_url} \nException: {e}' )

    # All elements available in the tag window. Not a string but an object that references the exact element on page
    self.tag_elements = self.driver.find_elements_by_class_name(self.tag_loc)
    converted_tag_dict = {}
    new_tags = ''
    for element_ref in self.tag_elements:
      # update dict with name as key and value as the reference to the element
      converted_tag_dict[element_ref.get_attribute('textContent').lower()] = element_ref

    for tag_to_add in tags:
      if tag_to_add.lower() not in converted_tag_dict: # no condition to handle numbers
        logger.warning(f'{tag_to_add.title()} tag does not exist. {self.name} \n{self.driver.current_url}')
        # Adds tags to tags to write
        new_tags += tag_to_add.title() + ', ' # Add tag if it doesn't exist
      else:
        try:
          logger.info(f'Adding {tag_to_add.title()}')
          # Brings tag into view using element reference provided by 'find_elements_by_class_name()
          converted_tag_dict[tag_to_add.lower()].location_once_scrolled_into_view
          click(tag_to_add)
        except Exception as e:
          # Not sure when this exception will trigger yet. Hopefully never
          logger.error(f'Exception occurred when trying to select tag: {tag_to_add.title()}\n Product: {self.driver.current_url} \n{sys.stderr}')
    # Write (str) of new tags into empty field. Must save the page to keep changes using Baseproduct.save_and_edit()
    write(new_tags, into=S('.'+Locators.tag_add_text)) # comma seperated
    click('ok')
    WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, Locators.tag_window)))
    self.copy_prod_btn_id.location_once_scrolled_into_view

  def add_category(self):
    """
    Assumes product is new and has no prior categories
    Assumes there is always no more than 1 designer or theme
    Assumes color is an object within json
    ***Need to check if categories have already been added to avoid repeats***
    """
    category = Locators.category
    add = Locators.add_record
    first = Locators.first

    if 'Backdrops' in self.themes[0]:
      product_type = Locators.backdrop
      extra = ' Backdrops' # Categories on bgt should have 'Backdrops' at the end of `Color` and `Themes`
    else: # Assumes the only other option available is a floor which does not use 'Backdrops' keyword
      product_type = Locators.floor
      extra = ''

    color_categories_to_add_list = [product_type + Locators.color_category + color + extra for color in self.colors ]
    theme_categories_to_add_list = [product_type + Locators.theme_category + theme for theme in self.themes ]
    categories_to_add_list = color_categories_to_add_list + theme_categories_to_add_list + [product_type + Locators.designer_category + self.designer]

    wait_until(Text(category).exists)
    click(category)

    for category_to_add in categories_to_add_list:
      logger.info(f'Adding Category: {category_to_add}')
      try:
        click(add)
        click(first)
        wait_until(Text('ACI Hot Drops').exists)
      except Exception as e:
       logger.error(sys.stderr, f'Could not find ACI Hot Drops in Category dropdown\n Failed to add Category {category_to_add}\
       \nProduct: {self.driver.current_url} \nException: {e}' )

      category_element_list = self.driver.find_elements_by_class_name('t-item')
      category_list = [category for category in category_element_list if category.get_attribute('textContent').lower() == category_to_add.lower()]

      try:
        category_list[-1].location_once_scrolled_into_view
      except IndexError as e:

        logger.critical(f'Index error when scrolling to category. The category may not exist \n{category_list}\n{self.name} \n{self.driver.current_url}')
      click(category_list[-1].get_attribute('textContent'))
      click('insert')

  def go_to_variants(self):
    """
    Assumes page url contains Admin/Product/Edit/ in order to switch variants tab
    """
    self.variants = Locators.variants
    self.unnamed = Locators.unnamed
    self.attr = Locators.attribute

    try:
      wait_until(Text(self.variants).exists)
      click(self.variants)
      wait_until(Text(self.unnamed).exists)
      click(self.unnamed)
      click(self.attr)
    except StaleElementReferenceException:
      logger.warning(f'Unable to go to product variants page. Trying again... {self.name} \n{self.driver.current_url}')