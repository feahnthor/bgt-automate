from selenium.webdriver import FirefoxOptions
from selenium import webdriver
from helium import * # Helium is a higher level webdriver that still allows for use of selenium webdriver
import logging

logger = logging.getLogger(__name__)

class DriverSetup:
  """
  Helium: https://selenium-python-helium.readthedocs.io/en/latest/api.html
  """
  def __init__(self, url) -> None:
    super().__init__()
    self.url = url
    # self.options = FirefoxOptions()
    # self.options.add_argument('--width=1920')
    # self.options.add_argument('--height=1020')
    # self.driver = start_firefox(self.url, options=self.options)

    # start_firefox() accpets a url and launches a instance of a firefox browser, *method from Helium*
    
    logger.info('Starting Firefox driver')
    try:
      self.driver = start_firefox(self.url, headless=True).maximize_window()
    except Exception as e:
      logger.critical('Firefox driver Failed to start')
      DriverSetup.done(self)

  def done(self) -> None:
    if self.driver != None:
      kill_browser()