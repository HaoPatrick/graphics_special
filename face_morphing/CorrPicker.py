import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from typing import List, Tuple
import json
import os
import argparse


class CorrPicker:
  NUM_POINTS = 42

  def __init__(self, image_path: str, output=None):
    self.image_path = os.path.abspath(image_path)
    self.image_dir, self.image_name = os.path.split(self.image_path)
    self.output_path: str = output if output else f"{self.image_dir}/{self.image_name.split('.')[0]}.json"
    self.img = Image.open(self.image_path)

  def pick(self):
    plt.imshow(self.img)
    x = plt.ginput(n=-1, timeout=-1)
    x.append([0, 0])
    x.append([0, self.img.size[1] - 1])
    x.append([self.img.size[0] - 1, 0])
    x.append([self.img.size[0] - 1, self.img.size[1] - 1])
    self._serialize(x)

  def _serialize(self, points: List[Tuple[int, int]]):
    result_dict = {'path': self.image_path,
                   'filename': self.image_name,
                   'points': [{'x': x[0], 'y': x[1]} for x in points]
                   }
    result_json = json.dumps(result_dict)
    with open(self.output_path, 'w') as f:
      f.write(result_json)

  def show(self):
    plt.imshow(self.img)
    plt.show()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="pick key points of an image")
  parser.add_argument('-f', '--file', required=True, type=str, help='path to your photos')
  parser.add_argument('-o', '--output', required=False, type=str, help='path to output')
  args = vars(parser.parse_args())
  picker = CorrPicker(args['file'], args['output'])
  picker.pick()
