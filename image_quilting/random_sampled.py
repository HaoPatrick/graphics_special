# coding=utf-8
from PIL import Image
import random
import argparse


def quilt_random(sample: str, outsize: int, patch_size: int):
  texture = Image.open(sample)
  im = Image.new('RGB', size=(outsize, outsize))
  for i in range(0, outsize, patch_size):
    for j in range(0, outsize, patch_size):
      random_shift = random.randrange(0, min(texture.size) - patch_size)
      texture_region = texture.crop((random_shift, random_shift, patch_size + random_shift, patch_size + random_shift))
      im.paste(texture_region, (i, j, i + patch_size, j + patch_size))
  return im


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-f', '--file', required=True, type=str, help='path to texture image')
  parser.add_argument('-o', '--outsize', required=True, type=int, help='output size')
  parser.add_argument('-p', '--patch_size', required=True, type=int, help='patch size')
  args = vars(parser.parse_args())
  result = quilt_random(args['file'], args['outsize'], args['patch_size'])
  result.save(args['file'][:-4] + '_random.jpg')
