from pathlib import Path

import numpy as np
import rawpy

from cxx_image_io import LibRaw, read_image, read_image_libraw

print('Canon-----------')
ref_image, metadata = read_image(Path('test/images/RAW_CANON_EOS_1DX.CR2'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_CANON_EOS_1DX.CR2')
print(raw.raw_image_visible.shape)


print('Sony-----------')
ref_image, metadata = read_image(Path('test/images/RAW_SONY_RX100.ARW'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_SONY_RX100.ARW')
print(raw.raw_image_visible.shape)



print('Nikon-----------')
ref_image, metadata = read_image(Path('test/images/RAW_NIKON_D3X.NEF'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_NIKON_D3X.NEF')
print(raw.raw_image_visible.shape)

print('PANASONIC-----------')
ref_image, metadata = read_image(Path('test/images/RAW_PANASONIC_LX3.RW2'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_PANASONIC_LX3.RW2')
print(raw.raw_image_visible.shape)


print('FUJI----------')
ref_image, metadata = read_image(Path('test/images/RAW_FUJI_E550.RAF'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_FUJI_E550.RAF')
print(raw.raw_image_visible.shape)


print('kodak----------')
ref_image, metadata = read_image(Path('test/images/RAW_KODAK_DC120.KDC'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_KODAK_DC120.KDC')
print(raw.raw_image_visible.shape)


print('kodak_slr----------')
ref_image, metadata = read_image(Path('test/images/RAW_KODAK_DCSPRO.DCR'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_KODAK_DCSPRO.DCR')
print(raw.raw_image_visible.shape)

print('leica----------')
ref_image, metadata = read_image(Path('test/images/RAW_LEICA_DLUX3.RAW'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_LEICA_DLUX3.RAW')
print(raw.raw_image_visible.shape)

print('olympus----------')
ref_image, metadata = read_image(Path('test/images/RAW_OLYMPUS_E3.ORF'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_OLYMPUS_E3.ORF')
print(raw.raw_image_visible.shape)

print('pentax----------')
ref_image, metadata = read_image(Path('test/images/RAW_PENTAX_KX.PEF'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_PENTAX_KX.PEF')
print(raw.raw_image_visible.shape)


print('samsung----------')
ref_image, metadata = read_image(Path('test/images/RAW_SAMSUNG_NX300M.SRW'))
print(ref_image.shape, metadata)
raw = rawpy.imread('test/images/RAW_SAMSUNG_NX300M.SRW')
print(raw.raw_image_visible.shape)