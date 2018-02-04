from PIL import Image, ImageChops
import random
import numpy as np
from functools import wraps
from time import time


def timeit(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    start = time()
    result = f(*args, **kwargs)
    end = time()
    print('Elapsed time: {}'.format(end - start))
    return result
  
  return wrapper


class Quilt:
  def __init__(self, texture_path: str, target_path=None, patch_size=None, output_size=None, alpha=0.5):
    self.texture_image = Image.open(texture_path).convert('RGB')
    self.texture_path = texture_path
    if target_path:
      self.target_image = Image.open(target_path)
    self.output_size = (output_size, output_size) if output_size else self.target_image.size
    self.output_image = Image.new('RGB', size=self.output_size)
    self.patch_size = patch_size if patch_size else 50
    self.overlap = int(self.patch_size / 3)
    self.full_length = self.patch_size + self.overlap * 2
    self.ALPHA = alpha
  
  def get_random_texture_patch(self, size=None):
    if size is None:
      size = self.full_length
    texture_size = self.texture_image.size
    j = random.randrange(0, texture_size[0] - size)
    i = random.randrange(0, texture_size[1] - size)
    return self.texture_image.crop((j, i, j + size, i + size))
  
  @staticmethod
  def patch_difference(rg1, rg2) -> int:
    if rg1.size != rg2.size:
      raise ArithmeticError('region size does not match')
    difference = ImageChops.difference(rg1.convert('L'), rg2.convert('L'))
    return sum(difference.getdata())
  
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
    # temp_array = path_array * 255
    # temp_array += np_array
    # Image.fromarray(temp_array).show()
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
  
  def save_output(self):
    self.output_image.save(self.texture_path[:-4] + '_' + str(random.randrange(0, 1000)))
