import argparse
import json

import matplotlib.pyplot as plt
import numpy as np
import skimage.draw

from face_morphing.PointDelaunay import PointDelaunay
from face_morphing.Morph import Morph
import os


class Caricature:
  SCALE_CONST = 2

  def __init__(self, origin: dict, mean: dict):
    self.origin = origin
    self.mean = mean
    self.im_ori = plt.imread(origin['path'])[..., :3] / 255.
    self.pts_ori = np.array([[x['y'], x['x']] for x in origin['points']])
    self.pts_mean = np.array([[x['y'], x['x']] for x in mean['points']])
    self.carica = (self.pts_ori - self.pts_mean) * self.SCALE_CONST + self.pts_mean
    self.output = np.empty(self.im_ori.shape)
    self.tri = PointDelaunay.delaunay(self.pts_mean)

  def save(self):
    out_dir, filename = os.path.split(self.origin['path'])
    img_path = f"{out_dir}\{filename.split('.')[0]}_c.jpg"
    plt.imsave(img_path, self.output, cmap='gray')
    result_dict = {'path': img_path,
                   'filename': f"{filename.split('.')[0]}_c.jpg",
                   'points': [{'x': x[1], 'y': x[0]} for x in self.carica.tolist()]
                   }
    result_json = json.dumps(result_dict)
    with open(f"{out_dir}/{filename.split('.')[0]}_c.json", 'w') as f:
      f.write(result_json)

  def generate_caricature(self):
    for triangle in self.tri.simplices:
      origin_tri = self.pts_ori[triangle]
      carica_tri = self.carica[triangle]
      affine = Morph.compute_affine(carica_tri, origin_tri)
      rows, columns = skimage.draw.polygon(carica_tri[:, 0], carica_tri[:, 1])
      matrix = np.ones([3, len(rows)])
      matrix[0] = rows
      matrix[1] = columns
      affine = np.dot(affine, matrix).astype(int)
      a = self.im_ori[affine[0], affine[1]]
      self.output[rows, columns] = a


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="compute and draw triangle on photos")
  parser.add_argument('-i1', '--image_one', required=True, type=str, help='path to first image config')
  parser.add_argument('-i2', '--image_two', required=True, type=str, help='path to second image config')
  args = vars(parser.parse_args())
  points1 = json.load(open(args['image_one']))
  points2 = json.load(open(args['image_two']))
  caricature = Caricature(points1, points2)
  caricature.generate_caricature()
  caricature.save()
