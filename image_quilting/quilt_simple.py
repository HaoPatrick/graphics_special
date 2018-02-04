import argparse
import random
from image_quilting.Quilting import Quilt


class QuiltSimple(Quilt):
  def __init__(self, sample: str, outsize: int, patch_size: int):
    Quilt.__init__(self, texture_path=sample, output_size=outsize, patch_size=patch_size)
    self.patch_size = patch_size
  
  def select_patch(self, region1=None, region2=None):
    smallest_diff = -1
    smallest_point = None
    count = 0
    while count < 1000:
      count += 1
      random_i = random.randrange(self.overlap, self.texture_image.size[0] - self.patch_size)
      random_j = random.randrange(self.overlap, self.texture_image.size[1] - self.patch_size)
      random_region1 = self.texture_image.crop(
        (random_i - self.overlap, random_j - self.overlap, self.patch_size + random_i, random_j)
      )
      random_region2 = self.texture_image.crop(
        (random_i - self.overlap, random_j, random_i, random_j + self.patch_size)
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
    return self.texture_image.crop(
      (smallest_point[0], smallest_point[1], smallest_point[0] + self.patch_size, smallest_point[1] + self.patch_size)
    )
  
  def quilt_simple(self):
    for j in range(0, self.output_size[0], self.patch_size):
      for i in range(0, self.output_size[0], self.patch_size):
        region_up = None if j == 0 else self.output_image.crop(
          (i - self.overlap, j - self.overlap, i + self.patch_size, j))
        region_left = None if i == 0 else self.output_image.crop((i - self.overlap, j, i, j + self.patch_size))
        texture_region = self.select_patch(
          region_up, region_left,
        )
        self.output_image.paste(texture_region, (i, j, i + self.patch_size, j + self.patch_size))
    return self.output_image


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-f', '--file', required=True, type=str, help='path to texture image')
  parser.add_argument('-o', '--outsize', required=True, type=int, help='output size')
  parser.add_argument('-p', '--patch_size', required=True, type=int, help='patch size')
  args = vars(parser.parse_args())
  quilt_simple = QuiltSimple(args['file'], args['outsize'], args['patch_size'])
  result = quilt_simple.quilt_simple()
  result.show()
