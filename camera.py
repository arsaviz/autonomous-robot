import requests

# this class controls the camera app
# for more information on the camera app, see: https://play.google.com/store/apps/details?id=com.pas.webcam
class Camera:
   def __init__(self, ip = "192.168.1.101", port = 8080, quality = 70, width = 800, height = 480, focusmode = 'continuous-picture', flashlight = True):
      self.ip = ip
      self.port = port
      self.url = "http://" + self.ip + ":" + str(self.port)
      self.quality = quality
      self.width = width
      self.height = height
      self.flashlight = flashlight
      self.focusmode = focusmode

      self.feed = f"{self.url}/video"

      self.setup()
      


   def setup(self):
      res = requests.get(f"{self.url}/settings/video_size?set={self.width}x{self.height}")
      res = requests.get(f"{self.url}/settings/quality?set={self.quality}")
      res = requests.get(f"{self.url}/settings/focusmode?set={self.focusmode}")
      if self.flashlight:
         res = requests.get(f"{self.url}/enabletorch")
      else:
         res = requests.get(f"{self.url}/disabletorch")
