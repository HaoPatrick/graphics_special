import matplotlib.pyplot as plt
import numpy as np
from face_morphing.PointDelaunay import PointDelaunay
from face_morphing.Morph import Morph
from typing import List
import skimage.draw


class Face:
  ASSETS_BASE = '../assets'
  IMAGE_DIR = ASSETS_BASE + '/face_images'
  POINTS_DIR = ASSETS_BASE + '/face_points'

  def __init__(self, face_index: str, argument_pts=False):
    self.im_path = f'{self.IMAGE_DIR}/{face_index}.jpg'
    self.pts_path = f'{self.POINTS_DIR}/{face_index}.pts'
    self.im = plt.imread(self.im_path)
    self.pts = Face.load_points(self.pts_path)
    if argument_pts:
      self.pts = np.vstack((self.pts, self._generate_argument_pts()))

  @staticmethod
  def load_points(pts_path: str) -> np.ndarray:
    with open(pts_path) as f:
      all_lines = f.readlines()
    all_lines = all_lines[3:-1]
    pts_lines = [x.strip().split(' ') for x in all_lines]
    total_pts = np.array([[float(x[0]), float(x[1])] for x in pts_lines])
    return total_pts

  def _generate_argument_pts(self):
    width, height = self.im.shape
    return np.array([[0, 0], [0, width - 1], [height - 1, 0], [height - 1, width - 1],
                     [height / 2, 0], [height / 2, width - 1], [height, width / 2], [0, width / 2]])

  def show(self):
    tri = PointDelaunay.delaunay(self.pts)
    plt.imshow(self.im, cmap='gray')
    plt.triplot(self.pts[:, 0], self.pts[:, 1], tri.simplices.copy(), linewidth=1)
    plt.plot(self.pts[:, 0], self.pts[:, 1], 'o', markersize=2)
    plt.show()


class MeanFace:

  def __init__(self, face_count=50, face_type='a'):
    self.COUNT = face_count
    self.TYPE = face_type
    self.all_faces = self._load_all_faces()
    self.mean_pts = self._get_mean_point()
    self.output = np.empty(self.all_faces[0].im.shape)
    self.mean_tri = PointDelaunay.delaunay(self.mean_pts)

  def _load_all_faces(self) -> List[Face]:
    return [Face(f'{i+1}{self.TYPE}', True) for i in range(self.COUNT)]

  def _get_mean_point(self) -> np.ndarray:
    return sum([x.pts for x in self.all_faces]) / len(self.all_faces)

  def calculate_face(self):
    [self._get_one_to_mean_faces(i) for i in range(self.COUNT)]

  def show(self):
    plt.imshow(self.output, cmap='gray')
    plt.show()

  def save(self, path: str):
    plt.imsave(path, self.output, cmap='gray')

  def _get_one_to_mean_faces(self, face_index: int):
    dissolve_ratio = 1
    curr_face = self.all_faces[face_index]
    for triangle in self.mean_tri.simplices:
      face_tri = curr_face.pts[triangle]
      mean_tri = self.mean_pts[triangle]
      mean_to_face = Morph.compute_affine(mean_tri, face_tri)
      rows, columns = skimage.draw.polygon(mean_tri[:, 0], mean_tri[:, 1])
      matrix = np.ones([3, len(rows)])
      matrix[0] = rows
      matrix[1] = columns
      mean_to_face = np.dot(mean_to_face, matrix).astype(int)
      try:
        a = dissolve_ratio * curr_face.im[mean_to_face[1], mean_to_face[0]]
      except IndexError as e:
        print(f'error on {face_index}{self.TYPE}, msg: {e}')
        continue
      self.output[columns, rows] += a


if __name__ == '__main__':
  count, faces_type = 50, 'b'
  mean_face = MeanFace(count, faces_type)
  mean_face.calculate_face()
  mean_face.save(f'../assets/mean/mean-{count}{faces_type}.jpg')
