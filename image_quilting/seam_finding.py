from PIL import Image, ImageChops
import random
import numpy as np
import argparse


class SeamFining:
  def __init__(self, sample: str, outsize: int, patchsize: int, overlap: int):
    self.texture = Image.open(sample)
    self.im = Image.new('RGB', size=(outsize, outsize))
    self.patchsize = patchsize
    self.outsize = outsize
    self.overlap = overlap
  
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
  
  def random_texture(self, size):
    i = random.randrange(0, self.texture.size[0] - size)
    j = random.randrange(0, self.texture.size[1] - size)
    return self.texture.crop((i, j, i + size, j + size))
  
  def find_mask(self, pc1, pc2, horizontal=True):
    difference = ImageChops.difference(pc1, pc2).convert('L')
    # difference.show()
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
    # Image.fromarray(path_array * 255).show()
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
  
  def find(self):
    for i in range(0, self.outsize, self.patchsize):
      for j in range(0, self.outsize, self.patchsize):
        if i == 0 and j == 0:
          self.im.paste(self.random_texture(self.patchsize + self.overlap),
                        (0, 0, self.patchsize + self.overlap, self.patchsize + self.overlap))
        elif i == 0:
          region1 = self.im.crop(
            (j - self.overlap, i, j + self.overlap, i + self.overlap + self.patchsize))
          patch = self.random_texture(self.patchsize + self.overlap * 2)
          region2 = patch.crop((0, self.overlap, 2 * self.overlap, self.overlap * 2 + self.patchsize))
          merged = self.get_seam_merged(region1, region2)
          # merged.show()
          self.im.paste(merged, (j - self.overlap, i, j + self.overlap, i + self.patchsize + self.overlap))
          self.im.paste(
            patch.crop(
              (2 * self.overlap, self.overlap, self.overlap * 2 + self.patchsize, self.overlap * 2 + self.patchsize)),
            (j + self.overlap, i, j + self.patchsize + self.overlap, i + self.patchsize + self.overlap)
          )
        elif j == 0:
          region1 = self.im.crop((j, i - self.overlap, j + self.overlap + self.patchsize, i + self.overlap))
          patch = self.random_texture(self.patchsize + self.overlap * 2)
          region2 = patch.crop((self.overlap, 0, 2 * self.overlap + self.patchsize, 2 * self.overlap))
          merged = self.get_seam_merged(region1, region2, True)
          self.im.paste(merged, (j, i - self.overlap, j + self.overlap + self.patchsize, i + self.overlap))
          self.im.paste(
            patch.crop(
              (self.overlap, self.overlap * 2, self.overlap * 2 + self.patchsize, self.overlap * 2 + self.patchsize)
            ),
            (j, i + self.overlap, j + self.patchsize + self.overlap, i + self.patchsize + self.overlap)
          )
        else:
          region1 = self.im.crop(
            (j - self.overlap, i - self.overlap, j + self.patchsize + self.overlap, i + self.overlap))
          patch = self.random_texture(self.patchsize + self.overlap * 2)
          region2 = patch.crop((0, 0, self.overlap * 2 + self.patchsize, self.overlap * 2))
          merged1 = self.get_seam_merged(region1, region2, True)
          region1 = self.im.crop(
            (j - self.overlap, i + self.overlap, j + self.overlap, i + self.overlap + self.patchsize))
          region2 = patch.crop((0, self.overlap * 2, self.overlap * 2, self.overlap * 2 + self.patchsize))
          merged2 = self.get_seam_merged(region1, region2)
          self.im.paste(merged1,
                        (j - self.overlap, i - self.overlap, j + self.patchsize + self.overlap, i + self.overlap))
          self.im.paste(merged2,
                        (j - self.overlap, i + self.overlap, j + self.overlap, i + self.overlap + self.patchsize))
          self.im.paste(patch.crop(
            (2 * self.overlap, 2 * self.overlap, 2 * self.overlap + self.patchsize, 2 * self.overlap + self.patchsize)),
            (j + self.overlap, i + self.overlap, j + self.overlap + self.patchsize, i + self.overlap + self.patchsize)
          )
    self.im.show()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-f', '--file', required=True, type=str, help='path to texture image')
  parser.add_argument('-o', '--outsize', required=True, type=int, help='output size')
  parser.add_argument('-p', '--patchsize', required=True, type=int, help='patch size')
  args = vars(parser.parse_args())
  quilt_simple = SeamFining(args['file'], args['outsize'], args['patchsize'], int(args['patchsize'] / 12))
  quilt_simple.find()
