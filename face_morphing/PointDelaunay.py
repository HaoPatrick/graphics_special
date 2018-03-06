from scipy.spatial import Delaunay
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import argparse
import json


# points = np.array([[0, 0], [0, 1.1], [1, 0], [1, 1]])
# tri = Delaunay(points)
# 
# plt.triplot(points[:, 0], points[:, 1], tri.simplices.copy())
# plt.plot(points[:, 0], points[:, 1], 'o')
# plt.show()

class PointDelaunay:
  def __init__(self, image_one: dict, image_two: dict):
    self.im1 = image_one
    self.im2 = image_two

  @staticmethod
  def delaunay(d_points: np.ndarray):
    return Delaunay(d_points)

  def draw_tri(self):
    np_points1 = np.array([[x['x'], x['y']] for x in self.im1['points']])
    np_points2 = np.array([[x['x'], x['y']] for x in self.im2['points']])

    tri = PointDelaunay.delaunay((np_points1 + np_points2) / 2)

    plt.subplot(121)
    img = Image.open(self.im1['path'])
    plt.imshow(img)
    plt.triplot(np_points1[:, 0], np_points1[:, 1], tri.simplices.copy(), linewidth=1)
    plt.plot(np_points1[:, 0], np_points1[:, 1], 'o', markersize=2)

    plt.subplot(122)
    img2 = Image.open(self.im2['path'])
    plt.imshow(img2)
    plt.triplot(np_points2[:, 0], np_points2[:, 1], tri.simplices.copy(), linewidth=1)
    plt.plot(np_points2[:, 0], np_points2[:, 1], 'o', markersize=2)
    plt.show()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="compute and draw triangle on photos")
  parser.add_argument('-i1', '--image_one', required=True, type=str, help='path to first image config')
  parser.add_argument('-i2', '--image_two', required=True, type=str, help='path to second image config')
  args = vars(parser.parse_args())
  points1 = json.load(open(args['image_one']))
  points2 = json.load(open(args['image_two']))
  point_delaunay = PointDelaunay(points1, points2)
  point_delaunay.draw_tri()
