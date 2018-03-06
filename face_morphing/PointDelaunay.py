from scipy.spatial import Delaunay
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict
import json


# points = np.array([[0, 0], [0, 1.1], [1, 0], [1, 1]])
# tri = Delaunay(points)
# 
# plt.triplot(points[:, 0], points[:, 1], tri.simplices.copy())
# plt.plot(points[:, 0], points[:, 1], 'o')
# plt.show()

class PointDelaunay:
  def __init__(self, points_config: dict):
    self.filename = points_config['filename']
    self.path = points_config['path']
    self.points: List[Dict[str, float]] = points_config['points']

  @staticmethod
  def delaunay(d_points: np.ndarray):
    return Delaunay(d_points)

  @staticmethod
  def draw_tri(image_one: dict, image_two: dict):
    np_points1 = np.array([[x['x'], x['y']] for x in image_one['points']])
    np_points2 = np.array([[x['x'], x['y']] for x in image_two['points']])

    tri = PointDelaunay.delaunay(np_points1)

    plt.subplot(121)
    img = Image.open(image_one['path'])
    plt.imshow(img)
    plt.triplot(np_points1[:, 0], np_points1[:, 1], tri.simplices.copy(), linewidth=1)
    plt.plot(np_points1[:, 0], np_points1[:, 1], 'o', markersize=2)

    plt.subplot(122)
    img2 = Image.open(image_two['path'])
    plt.imshow(img2)
    plt.triplot(np_points2[:, 0], np_points2[:, 1], tri.simplices.copy(), linewidth=1)
    plt.plot(np_points2[:, 0], np_points2[:, 1], 'o', markersize=2)
    plt.show()


if __name__ == '__main__':
  points1 = json.load(open('../assets/justin_700_800_bck.json'))
  points2 = json.load(open('../assets/selfie_700_800_bck.json'))
  PointDelaunay.draw_tri(points1, points2)
