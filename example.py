from pathlib import Path

import numpy as np
import rawpy

from cxx_image_io import LibRaw, read_image

ref_image, metadata = read_image(Path('test\\images\\bayer_12bit.dng'))
print(ref_image.shape, ref_image.dtype)

raw = rawpy.imread('test\\images\\bayer_12bit.dng')
print(raw.raw_image_visible.shape, raw.raw_image_visible.dtype)

assert np.array_equal(ref_image, raw.raw_image_visible)
