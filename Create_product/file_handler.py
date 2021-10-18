import json
import os
from dir_location import DirLocation
import logging

logger = logging.getLogger(__name__)

class FileHandler:
  """
  Manages common file types i work with
  """
  def __init__(self, folder='', file='', logger=None) -> None:
    self.file = folder + file # currently does not account for other file types. need to clean up
    self.folder = folder

  def open_json(self) -> dict:
    with open(self.file, 'r+') as json_file:
      self.data = json.load(json_file)                                                                                                                                                               
    return self.data

  def get_files(self) -> list:
    return os.listdir(self.folder)