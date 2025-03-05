from pathlib import Path

import numpy as np
import rawpy

from cxx_image_io import LibRaw, read_image, read_image_libraw

ref_image, metadata = read_image(Path('test/images/RAW_SONY_RX100.ARW'))
# ref_image, metadata = read_image_libraw(Path('test\\images\\bayer_12bits.dng'))
# ref_image, metadata = read_image_libraw(Path('test\\images\\RAW_NIKON_D3X.NEF'))
# ref_image, metadata = read_image_libraw(Path('test\\images\\RAW_PANASONIC_FZ8.RAW'))
# ref_image, metadata = read_image_libraw(Path('test\\images\\RAW_LEICA_M240.DNG'))

print(ref_image.shape, ref_image.ndim)

print(metadata)


print('-------color_matrix')
raw = rawpy.imread('test/images/RAW_SONY_RX100.ARW')
print(raw.raw_image_visible.shape, raw.raw_image.shape)
print(raw.color_matrix)
