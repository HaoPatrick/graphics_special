import argparse
from PIL import Image, ImageChops
import random
from functools import wraps
from time import time
import numpy as np
from typing import Tuple

ALPHA = 0.5


def timeit(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    start = time()
    result = f(*args, **kwargs)
    end = time()
    print('Elapsed time: {}'.format(end - start))
    return result
  
  return wrapper


class TextureTransfer:
  def __init__(self, texture: str, target: str, patch_size=60):
    self.texture_image = Image.open(texture)
    self.target_image = Image.open(target)
    self.output_image = Image.new('RGB', size=self.target_image.size)
    self.patch_size = patch_size
    self.overlap = int(self.patch_size / 12)
    self.full_size = self.patch_size + self.overlap * 2
    self.out_size = self.target_image.size
  
  def get_target_patch(self, pos: Tuple[int, int]):
    return self.target_image.crop((pos[0], pos[1], pos[0] + self.patch_size, pos[1] + self.patch_size))
  
  def get_random_patch(self, size=None):
    if size is None:
      size = self.patch_size + self.overlap * 2
    j = random.randrange(0, self.out_size[0] - size)
    i = random.randrange(0, self.out_size[1] - size)
    return self.texture_image.crop((j, i, j + size, i + size))
  
  @staticmethod
  def patch_difference(rg1, rg2) -> int:
    if rg1.size != rg2.size:
      raise ArithmeticError('region size does not match')
    
    difference = ImageChops.difference(rg1.convert('L'), rg2.convert('L'))
    return sum(difference.getdata())
  
  def cost_on_first(self):
    min_difference = -1
    min_patch = None
    target_patch = self.get_target_patch((0, 0))
    for _ in range(1000):
      random_texture = self.get_random_patch()
      difference_on_patches = self.patch_difference(
        target_patch,
        random_texture.crop((self.overlap, self.overlap, self.full_size - self.overlap,
                             self.full_size - self.overlap))
      )
      if difference_on_patches < min_difference or min_difference < 0:
        min_difference = difference_on_patches
        min_patch = random_texture
    return min_patch
  
  def cost_on_first_row(self, pos: Tuple[int, int], left_reg):
    min_difference = -1
    min_patch = None
    target_patch = self.get_target_patch(pos)
    for _ in range(1000):
      random_texture = self.get_random_patch()
      difference_on_patches = self.patch_difference(
        target_patch,
        random_texture.crop((self.overlap, self.overlap, self.full_size - self.overlap,
                             self.full_size - self.overlap))
      )
      difference_on_left_region = self.patch_difference(
        left_reg,
        random_texture.crop((0, self.overlap, 2 * self.overlap, self.full_size))
      )
      total_diff = ALPHA * difference_on_patches + (1 - ALPHA) * difference_on_left_region
      if total_diff < min_difference or min_difference < 0:
        min_patch = random_texture
        min_difference = total_diff
    return min_patch
  
  def cost_on_first_column(self, pos: Tuple[int, int], top_reg):
    min_difference = -1
    min_patch = None
    target_patch = self.get_target_patch(pos)
    for _ in range(1000):
      random_texture = self.get_random_patch()
      difference_on_patches = self.patch_difference(
        target_patch,
        random_texture.crop((self.overlap, self.overlap, self.full_size - self.overlap,
                             self.full_size - self.overlap))
      )
      difference_on_left_region = self.patch_difference(
        top_reg,
        random_texture.crop((self.overlap, 0, self.full_size, 2 * self.overlap))
      )
      total_diff = ALPHA * difference_on_patches + (1 - ALPHA) * difference_on_left_region
      if total_diff < min_difference or min_difference < 0:
        min_patch = random_texture
        min_difference = total_diff
    return min_patch
  
  def cost_on_both(self, pos, top_reg, left_reg):
    min_difference = -1
    min_patch = None
    target_patch = self.get_target_patch(pos)
    for _ in range(100):
      random_texture = self.get_random_patch()
      difference_on_patches = self.patch_difference(
        target_patch,
        random_texture.crop((self.overlap, self.overlap, self.full_size - self.overlap,
                             self.full_size - self.overlap))
      )
      difference_on_over_lap = self.patch_difference(
        top_reg,
        random_texture.crop((0, 0, self.full_size, 2 * self.overlap))
      )
      difference_on_over_lap += self.patch_difference(
        left_reg,
        random_texture.crop((0, 2 * self.overlap, 2 * self.overlap, self.full_size))
      )
      total_diff = ALPHA * difference_on_patches + (1 - ALPHA) * difference_on_over_lap
      if total_diff < min_difference or min_difference < 0:
        min_patch = random_texture
        min_difference = total_diff
    return min_patch
  
  @staticmethod
  def find_path_matrix(array):
    size = array.shape
    dp_array = np.zeros(size, dtype=int)
    for i in range(size[0]):
      for j in range(size[1]):
        if i == 0:
          dp_array[i][j] = array[i][j]
        elif j == 0:
          dp_array[i][j] = array[i][j] + min(dp_array[i - 1][j], dp_array[i - 1][j + 1])
        elif j == size[1] - 1:
          dp_array[i][j] = array[i][j] + min(dp_array[i - 1][j], dp_array[i - 1][j - 1])
        else:
          dp_array[i][j] = array[i][j] + min(dp_array[i - 1][j], dp_array[i - 1][j + 1], dp_array[i - 1][j - 1])
    path_array = np.zeros(size, dtype=int)
    min_index = 0
    for i in range(size[0] - 1, -1, -1):
      if i == size[0] - 1:
        min_index = np.argmin(dp_array[i])
      path_array[i][min_index] = 1
      
      if min_index == 0:
        min_index += np.argmin([dp_array[i - 1][min_index], dp_array[i - 1][min_index + 1]])
      elif min_index == size[1] - 1:
        min_index += np.argmin([dp_array[i - 1][min_index - 1], dp_array[i - 1][min_index]]) - 1
      else:
        min_index += np.argmin([
          dp_array[i - 1][min_index - 1], dp_array[i - 1][min_index], dp_array[i - 1][min_index + 1]
        ]) - 1
    return path_array
  
  def find_mask(self, pc1, pc2, horizontal=True):
    difference = ImageChops.difference(pc1, pc2).convert('L')
    size = (pc1.size[1], pc1.size[0])
    
    np_array = np.asarray(difference.getdata())
    np_array = np.reshape(np_array, size)
    if horizontal:
      np_array = np_array.T
      size = (size[1], size[0])
    
    path_array = self.find_path_matrix(np_array)
    for i in range(0, size[0]):
      for j in range(0, size[1]):
        if path_array[i][j] == 1:
          break
        path_array[i][j] = 1
    if horizontal:
      path_array = path_array.T
    return path_array
  
  def get_seam_merged(self, pc1, pc2, horizontal=False):
    size = (pc1.size[1], pc1.size[0])
    path_matrix = self.find_mask(pc1, pc2, horizontal)
    color_image1 = np.array(pc1)
    color_image2 = np.array(pc2)
    for i in range(size[0]):
      for j in range(size[1]):
        if path_matrix[i][j] == 0:
          color_image1[i][j] = color_image2[i][j]
    return Image.fromarray(color_image1)
  
  def synthesize(self):
    for i in range(0, self.out_size[1], self.patch_size):
      for j in range(0, self.out_size[0], self.patch_size):
        if i == 0 and j == 0:
          rv = self.cost_on_first()
          self.output_image.paste(
            rv.crop((self.overlap, self.overlap, self.full_size, self.full_size)),
            (0, 0, self.overlap + self.patch_size, self.overlap + self.patch_size)
          )
        elif i == 0:
          left_region = self.output_image.crop(
            (j - self.overlap, i, j + self.overlap, i + self.overlap + self.patch_size))
          patch = self.cost_on_first_row((j, i), left_region)
          region2 = patch.crop((0, self.overlap, 2 * self.overlap, self.full_size))
          merged = self.get_seam_merged(left_region, region2)
          self.output_image.paste(merged, (j - self.overlap, i, j + self.overlap, i + self.patch_size + self.overlap))
          self.output_image.paste(
            patch.crop(
              (2 * self.overlap, self.overlap, self.overlap * 2 + self.patch_size, self.overlap * 2 + self.patch_size)),
            (j + self.overlap, i, j + self.patch_size + self.overlap, i + self.patch_size + self.overlap)
          )
        elif j == 0:
          region1 = self.output_image.crop((j, i - self.overlap, j + self.overlap + self.patch_size, i + self.overlap))
          patch = self.cost_on_first_column((j, i), region1)
          region2 = patch.crop((self.overlap, 0, 2 * self.overlap + self.patch_size, 2 * self.overlap))
          merged = self.get_seam_merged(region1, region2, True)
          self.output_image.paste(merged, (j, i - self.overlap, j + self.overlap + self.patch_size, i + self.overlap))
          self.output_image.paste(
            patch.crop(
              (self.overlap, self.overlap * 2, self.overlap * 2 + self.patch_size, self.overlap * 2 + self.patch_size)
            ),
            (j, i + self.overlap, j + self.patch_size + self.overlap, i + self.patch_size + self.overlap)
          )
        else:
          region_up = self.output_image.crop(
            (j - self.overlap, i - self.overlap, j + self.patch_size + self.overlap, i + self.overlap))
          region_left = self.output_image.crop(
            (j - self.overlap, i + self.overlap, j + self.overlap, i + self.overlap + self.patch_size))
          patch = self.cost_on_both((j, i), region_up, region_left)
          region2 = patch.crop((0, 0, self.overlap * 2 + self.patch_size, self.overlap * 2))
          merged1 = self.get_seam_merged(region_up, region2, True)
          
          region2 = patch.crop((0, self.overlap * 2, self.overlap * 2, self.overlap * 2 + self.patch_size))
          merged2 = self.get_seam_merged(region_left, region2)
          self.output_image.paste(merged1,
                                  (j - self.overlap, i - self.overlap, j + self.patch_size + self.overlap,
                                   i + self.overlap))
          self.output_image.paste(merged2,
                                  (j - self.overlap, i + self.overlap, j + self.overlap,
                                   i + self.overlap + self.patch_size))
          self.output_image.paste(patch.crop(
            (2 * self.overlap, 2 * self.overlap, 2 * self.overlap + self.patch_size,
             2 * self.overlap + self.patch_size)),
            (j + self.overlap, i + self.overlap, j + self.overlap + self.patch_size, i + self.overlap + self.patch_size)
          )
    self.output_image.show()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-tx', '--texture', required=True, type=str, help='path to texture image')
  parser.add_argument('-tr', '--target', required=True, type=str, help='path to target image')
  args = vars(parser.parse_args())
  tt = TextureTransfer(args['texture'], args['target'])
  tt.synthesize()
  # result.save(args['file'][:-4] + '_simple.jpg')
