import argparse
import json

import numpy as np
from face_morphing.PointDelaunay import PointDelaunay
import skimage.draw
import matplotlib.pyplot as plt


class Morph:
  def __init__(self, im_one: dict, im_two: dict):
    self.im1 = plt.imread(im_one['path'])[..., :3] / 255.
    self.im2 = plt.imread(im_two['path'])[..., :3] / 255.
    self.im1_pts = np.array([[x['y'], x['x']] for x in im_one['points']])
    self.im2_pts = np.array([[x['y'], x['x']] for x in im_two['points']])
    self.output = np.empty(self.im1.shape)
    self.triangles = PointDelaunay.delaunay((self.im1_pts + self.im2_pts) / 2)

  def morph(self, warp_ratio: float, dissolve_ratio: float):
    self.output = np.empty(self.im1.shape)
    for triangle in self.triangles.simplices:
      im1_tri = self.im1_pts[triangle]
      im2_tri = self.im2_pts[triangle]
      mid_tri = im1_tri * warp_ratio + im2_tri * (1 - warp_ratio)
      mid_to_img1 = Morph.compute_affine(mid_tri, im1_tri)
      mid_to_img2 = Morph.compute_affine(mid_tri, im2_tri)
      rows, columns = skimage.draw.polygon(mid_tri[:, 0], mid_tri[:, 1])
      matrix = np.ones([3, len(rows)])
      matrix[0] = rows
      matrix[1] = columns
      mid_to_img1 = np.dot(mid_to_img1, matrix).astype(int)
      mid_to_img2 = np.dot(mid_to_img2, matrix).astype(int)
      a = dissolve_ratio * self.im1[mid_to_img1[0], mid_to_img1[1]]
      b = (1 - dissolve_ratio) * self.im2[mid_to_img2[0], mid_to_img2[1]]
      self.output[rows, columns] = a + b

  def save(self, path: str):
    plt.imsave(path, self.output)

  def display(self):
    plt.imshow(self.output)
    plt.show()

  @staticmethod
  def compute_affine(tri1_pts, tri2_pts):
    tri1 = np.ones([3, 3])
    tri2 = np.ones([3, 3])
    tri1[:, :-1] = tri1_pts
    tri2[:, :-1] = tri2_pts
    return np.dot(tri2.T, np.linalg.inv(tri1.T))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="compute and draw triangle on photos")
  parser.add_argument('-i1', '--image_one', required=True, type=str, help='path to first image config')
  parser.add_argument('-i2', '--image_two', required=True, type=str, help='path to second image config')
  args = vars(parser.parse_args())
  points1 = json.load(open(args['image_one']))
  points2 = json.load(open(args['image_two']))
  morph = Morph(points2, points1)
  iteration = 46
  for i in range(1, iteration):
    morph.morph(i / (iteration - 1), i / (iteration - 1))
    morph.save('../assets/morph/morph-mean-ptk-{:02d}.jpg'.format(i))
  # morph.morph(1, 1)
  # morph.display()
