# coding=utf-8
from PIL import Image
import random
import argparse

ASSETS_PATH = '../assets/'
TEXTURE_PATH = ASSETS_PATH + 'texture_redpot.png'


def quilt_random(sample: str, outsize: int, patchsize: int) -> None:
  texture = Image.open(sample)
  im = Image.new('RGB', size=(outsize, outsize))
  for i in range(0, outsize, patchsize):
    for j in range(0, outsize, patchsize):
      random_shift = random.randrange(0, min(texture.size) - patchsize)
      texture_region = texture.crop((random_shift, random_shift, patchsize + random_shift, patchsize + random_shift))
      im.paste(texture_region, (i, j, i + patchsize, j + patchsize))
  im.show()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-f', '--file', required=True, type=str, help='path to texture image')
  parser.add_argument('-o', '--outsize', required=True, type=int, help='output size')
  parser.add_argument('-p', '--patchsize', required=True, type=int, help='patch size')
  args = vars(parser.parse_args())
  quilt_random(args['file'], args['outsize'], args['patchsize'])
