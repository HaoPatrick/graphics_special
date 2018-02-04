import random
import argparse
from image_quilting.Quilting import Quilt


class SeamFining(Quilt):
  def __init__(self, sample: str, outsize: int, patch_size: int):
    Quilt.__init__(self, texture_path=sample, output_size=outsize, patch_size=patch_size)

  def get_patch_by_similarity(self, patch, patch2=None):
    size = patch.size
    size_returned = self.patch_size + 2 * self.overlap
    min_difference = -1
    min_point = ()
    for _ in range(30):
      j = random.randrange(0, self.texture_image.size[0] - size_returned)
      i = random.randrange(0, self.texture_image.size[1] - size_returned)
      if patch2 is None:
        if size[0] < size[1]:
          test_region = self.texture_image.crop((j, i + self.overlap, j + self.overlap * 2, i + size_returned))
        else:
          test_region = self.texture_image.crop((j + self.overlap, i, j + size_returned, i + self.overlap * 2))
        difference = self.patch_difference(test_region, patch)
      else:
        test_region = self.texture_image.crop((j, i, j + size_returned, i + 2 * self.overlap))
        difference = self.patch_difference(patch, test_region)
        test_region = self.texture_image.crop((j, i + self.overlap * 2, j + self.overlap * 2, i + size_returned))
        difference += self.patch_difference(patch2, test_region)
      if difference < min_difference or min_difference < 0:
        min_difference = difference
        min_point = (j, i)
    return self.texture_image.crop(
      (min_point[0], min_point[1], min_point[0] + size_returned, min_point[1] + size_returned))
  
  def random_texture(self, size):
    i = random.randrange(0, self.texture_image.size[0] - size)
    j = random.randrange(0, self.texture_image.size[1] - size)
    return self.texture_image.crop((i, j, i + size, j + size))
  
  def find(self):
    for i in range(0, self.output_size[0], self.patch_size):
      for j in range(0, self.output_size[0], self.patch_size):
        if i == 0 and j == 0:
          self.output_image.paste(self.random_texture(self.patch_size + self.overlap),
                                  (0, 0, self.patch_size + self.overlap, self.patch_size + self.overlap))
        elif i == 0:
          region1 = self.output_image.crop(
            (j - self.overlap, i, j + self.overlap, i + self.overlap + self.patch_size))
          patch = self.get_patch_by_similarity(region1)
          region2 = patch.crop((0, self.overlap, 2 * self.overlap, self.overlap * 2 + self.patch_size))
          merged = self.get_seam_merged(region1, region2)
          self.output_image.paste(merged, (j - self.overlap, i, j + self.overlap, i + self.patch_size + self.overlap))
          self.output_image.paste(
            patch.crop(
              (2 * self.overlap, self.overlap, self.overlap * 2 + self.patch_size, self.overlap * 2 + self.patch_size)),
            (j + self.overlap, i, j + self.patch_size + self.overlap, i + self.patch_size + self.overlap)
          )
        elif j == 0:
          region1 = self.output_image.crop((j, i - self.overlap, j + self.overlap + self.patch_size, i + self.overlap))
          patch = self.get_patch_by_similarity(region1)
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
          patch = self.get_patch_by_similarity(region_up, region_left)
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
    return self.output_image


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-f', '--file', required=True, type=str, help='path to texture image')
  parser.add_argument('-o', '--outsize', required=True, type=int, help='output size')
  parser.add_argument('-p', '--patch_size', required=True, type=int, help='patch size')
  args = vars(parser.parse_args())
  quilt_simple = SeamFining(args['file'], args['outsize'], 120)
  result = quilt_simple.find()
  result.save(args['file'][:-4] + '_seam.jpg')
  result.show()
