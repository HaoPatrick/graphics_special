import argparse
from PIL import Image, ImageChops
import random
from functools import wraps
from time import time
import numpy as np
from typing import Tuple


def timeit(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    start = time()
    result = f(*args, **kwargs)
    end = time()
    print('Elapsed time: {}'.format(end - start))
    return result
  
  return wrapper


class QuiltSimple:
  def __init__(self, sample: str, outsize: int, patchsize: int, overlap: int):
    self.texture = Image.open(sample)
    self.im = Image.new('RGB', size=(outsize, outsize))
    self.patchsize = patchsize
    self.outsize = outsize
    self.overlap = overlap
  
  def patch_difference(self, rg1, rg2) -> int:
    if rg1.size != rg2.size:
      raise ArithmeticError('region size do not match')
    
    difference = ImageChops.difference(rg1.convert('L'), rg2.convert('L'))
    return sum(difference.getdata())
  
  @timeit
  def select_patch(self, region1=None, region2=None):
    smallest_diff = -1
    smallest_point = None
    count = 0
    while count < 1000:
      count += 1
      random_i = random.randrange(self.overlap, self.texture.size[0] - self.patchsize)
      random_j = random.randrange(self.overlap, self.texture.size[1] - self.patchsize)
      random_region1 = self.texture.crop(
        (random_i - self.overlap, random_j - self.overlap, self.patchsize + random_i, random_j)
      )
      random_region2 = self.texture.crop(
        (random_i - self.overlap, random_j, random_i, random_j + self.patchsize)
      )
      if region1 is None and region2 is None:
        smallest_point = (random_i, random_j)
        break
      elif region1 is None:
        difference_sum = self.patch_difference(random_region2, region2)
      elif region2 is None:
        difference_sum = self.patch_difference(random_region1, region1)
      else:
        difference_sum = self.patch_difference(random_region1, region1) + self.patch_difference(random_region2, region2)
      if smallest_diff < 0 or difference_sum < smallest_diff:
        smallest_diff = difference_sum
        smallest_point = (random_i, random_j)
      # print(difference_sum)
    return self.texture.crop(
      (smallest_point[0], smallest_point[1], smallest_point[0] + self.patchsize, smallest_point[1] + self.patchsize)
    )
  
  def quilt_simple(self):
    for j in range(0, self.outsize, self.patchsize):
      for i in range(0, self.outsize, self.patchsize):
        region_up = None if j == 0 else self.im.crop((i - self.overlap, j - self.overlap, i + self.patchsize, j))
        region_left = None if i == 0 else self.im.crop((i - self.overlap, j, i, j + self.patchsize))
        texture_region = self.select_patch(
          region_up, region_left,
        )
        self.im.paste(texture_region, (i, j, i + self.patchsize, j + self.patchsize))
        print("==================", i, j)
    return self.im


class TextureTransfer:
  def __init__(self, texture: str, target: str, patch_size=60):
    self.texture_image = Image.open(texture)
    self.target_image = Image.open(target)
    self.output_image = Image.new('RGB', size=self.target_image.size)
    self.patch_size = patch_size
    self.overlap = self.patch_size / 12
    self.out_size = self.target_image.size
  
  def get_target_patch(self, pos: Tuple[int, int]):
    return self.target_image.crop((pos[0], pos[1], pos[0] + self.patch_size, pos[1] + self.patch_size))
  
  def cost(self, pos: Tuple[int, int], patch2, ):
    target_patch = self.get_target_patch(pos)
    
    pass
  
  def synthesize(self):
    for i in range(0, self.out_size, self.patch_size):
      for j in range(0, self.out_size, self.patch_size):
        if i == 0 and j == 0:
          pass
        elif i == 0:
          pass
        elif j == 0:
          pass
        else:
          pass


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-tx', '--texture', required=True, type=str, help='path to texture image')
  parser.add_argument('-tr', '--target', required=True, type=str, help='path to target image')
  args = vars(parser.parse_args())
  tt = TextureTransfer(args['texture'], args['target'])
  result = tt.quilt_simple()
  result.save(args['file'][:-4] + '_simple.jpg')
