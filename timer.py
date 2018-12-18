FIVE_MINUTE_DELAY = 60 * 5

class MyThread(Thread):
  def __init__(self, event):
    Thread.__init__(self)
    self.stopped = event

  def run(self):
    while not self.stopped.wait(FIVE_MINUTE_DELAY):
      print("my thread")
      # call a function