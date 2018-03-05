import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from typing import List, Tuple


class CorrPicker:
  NUM_POINTS = 42
  
  def __init__(self, image_path: str):
    self.image_path = image_path
    self.img = Image.open(self.image_path)
  
  def pick(self):
    plt.imshow(self.img)
    x = plt.ginput(self.NUM_POINTS)
    print("clicked", x)
  
  def _serialize(self, points: List[Tuple[int, int]]):
    pass
  
  def show(self):
    plt.imshow(self.img)
    plt.show()


picker = CorrPicker('../assets/face_morphing/patrick.jpg')
picker.pick()
