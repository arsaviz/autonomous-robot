from websocket import create_connection

# this class connects to the websocket server and sends the car's position requests
class Car:
   def __init__(self, ip = "192.168.1.105", port = 80):
      self.url = f"ws://{ip}:{port}/ws"
      self.ws = create_connection(self.url)
      self.stop()

   def forward(self):
      self.ws.send("forward")

   def backward(self):
      self.ws.send("backward")

   def left(self):
      self.ws.send("left")

   def right(self):
      self.ws.send("right")

   def stop(self):
      self.ws.send("parked")

   def close(self):
      self.ws.close()

   def get_distance(self):
      return self.ws.recv()

   def set_speed(self, speed):
      self.ws.send(f"speed:{speed}")