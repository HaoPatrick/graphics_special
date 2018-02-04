from PIL import Image, ImageChops
import random


class Quilt:
  def __init__(self, texture_path: str, target_path=None, patch_size=None, output_size=None):
    self.texture_image = Image.open(texture_path)
    if target_path:
      self.target_image = Image.open(target_path)
    self.output_size = (output_size, output_size) if output_size else self.target_image.size
    self.patch_size = patch_size if patch_size else 50
    self.overlap = self.patch_size / 12
    self.full_length = self.patch_size + self.overlap * 2
  
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
