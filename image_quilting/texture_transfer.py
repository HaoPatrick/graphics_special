import argparse
from typing import Tuple
from image_quilting.Quilting import Quilt


class TextureTransfer(Quilt):
  def __init__(self, texture: str, target: str, patch_size=30):
    Quilt.__init__(self, texture_path=texture, target_path=target, patch_size=patch_size)
  
  def get_target_patch(self, pos: Tuple[int, int]):
    return self.target_image.crop((pos[0], pos[1], pos[0] + self.patch_size, pos[1] + self.patch_size))
  
  def get_patch_by_cost(self, pos: Tuple[int, int], left_region=None, top_region=None):
    min_difference = -1
    min_patch = None
    target_patch = self.get_target_patch(pos)
    for _ in range(1000):
      random_texture = self.get_random_texture_patch()
      difference_on_patches = self.patch_difference(
        target_patch,
        random_texture.crop((self.overlap, self.overlap, self.full_length - self.overlap,
                             self.full_length - self.overlap))
      )
      if left_region and not top_region:
        difference_on_overlap = self.patch_difference(
          left_region,
          random_texture.crop((0, self.overlap, 2 * self.overlap, self.full_length))
        )
      elif top_region and not left_region:
        difference_on_overlap = self.patch_difference(
          top_region,
          random_texture.crop((self.overlap, 0, self.full_length, 2 * self.overlap))
        )
      elif not top_region and not left_region:
        difference_on_overlap = 0
      else:
        difference_on_overlap = self.patch_difference(
          top_region,
          random_texture.crop((0, 0, self.full_length, 2 * self.overlap))
        )
        difference_on_overlap += self.patch_difference(
          left_region,
          random_texture.crop((0, 2 * self.overlap, 2 * self.overlap, self.full_length))
        )
      total_diff = self.ALPHA * difference_on_patches + (1 - self.ALPHA) * difference_on_overlap
      if total_diff < min_difference or min_difference < 0:
        min_difference = total_diff
        min_patch = random_texture
    return min_patch
  
  def synthesize(self):
    for i in range(0, self.output_size[1], self.patch_size):
      for j in range(0, self.output_size[0], self.patch_size):
        if i == 0 and j == 0:
          rv = self.get_patch_by_cost((j, i))
          self.output_image.paste(
            rv.crop((self.overlap, self.overlap, self.full_length, self.full_length)),
            (0, 0, self.overlap + self.patch_size, self.overlap + self.patch_size)
          )
        elif i == 0:
          left_region = self.output_image.crop(
            (j - self.overlap, i, j + self.overlap, i + self.overlap + self.patch_size))
          patch = self.get_patch_by_cost((j, i), left_region=left_region)
          region2 = patch.crop((0, self.overlap, 2 * self.overlap, self.full_length))
          merged = self.get_seam_merged(left_region, region2)
          self.output_image.paste(merged, (j - self.overlap, i, j + self.overlap, i + self.patch_size + self.overlap))
          self.output_image.paste(
            patch.crop(
              (2 * self.overlap, self.overlap, self.overlap * 2 + self.patch_size, self.overlap * 2 + self.patch_size)),
            (j + self.overlap, i, j + self.patch_size + self.overlap, i + self.patch_size + self.overlap)
          )
        elif j == 0:
          region1 = self.output_image.crop((j, i - self.overlap, j + self.overlap + self.patch_size, i + self.overlap))
          patch = self.get_patch_by_cost((j, i), top_region=region1)
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
          patch = self.get_patch_by_cost((j, i), top_region=region_up, left_region=region_left)
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
    self.output_image.show()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="quilt random function")
  parser.add_argument('-tx', '--texture', required=True, type=str, help='path to texture image')
  parser.add_argument('-tr', '--target', required=True, type=str, help='path to target image')
  args = vars(parser.parse_args())
  tt = TextureTransfer(args['texture'], args['target'])
  tt.synthesize()
