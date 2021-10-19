import json

class FileHandler:
   def __init__(self, file_object) -> None:
      self.file_object = file_object

   def open_json(self):
      with open(self.file_object) as f:
         data = json.load(f)
      return data
