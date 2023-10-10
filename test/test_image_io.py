from image_io import ImageMetadata, ImageWriter, FileFormat, PixelType, ImageLayout
from image_io import read_image, read_image_exif, write_image, write_image_exif
import numpy as np

import pytest
from pathlib import Path
import hashlib

test_images_dir = Path('./test/images/')
test_npy_dir = Path('./test/npy/')
test_outputs_dir = Path('./test/_outputs/')

raw_path = str(test_images_dir / 'plain_raw_16bit.raw')
bmp_path = str(test_images_dir / 'rgb_8bit.bmp')
jpg_path = str(test_images_dir / 'rgb_8bit.jpg')
png_path = str(test_images_dir / 'rgba_8bit.png')
tif_path = str(test_images_dir / 'rgb_8bit.tif')
cfa_path = str(test_images_dir / 'bayer_10bit.cfa')
rawmipi12_path = str(test_images_dir / 'raw_12bit.RAWMIPI12')
rawmipi10_path = str(test_images_dir / 'raw_10bit.RAWMIPI')
dng_path = str(test_images_dir / 'raw.DNG')


output_raw_path = str(test_outputs_dir / 'plain_raw_16bit.raw')
output_bmp_path = str(test_outputs_dir / 'rgb_8bit.bmp')
output_jpg_path = str(test_outputs_dir / 'rgb_8bit.jpg')
output_png_path = str(test_outputs_dir / 'rgba_8bit.png')
output_tif_path = str(test_outputs_dir / 'rgb_8bit.tif')
output_cfa_path = str(test_outputs_dir / 'bayer_10bit.cfa')
output_rawmipi12_path = str(test_outputs_dir / 'raw_12bit.RAWMIPI12')
output_rawmipi10_path = str(test_outputs_dir / 'raw_10bit.RAWMIPI')
output_dng_path = str(test_outputs_dir / 'raw.DNG')

raw_npy_path = str(test_npy_dir / 'ref_plain_raw_16bit.npy')
bmp_npy_path = str(test_npy_dir /'ref_rgb_8bit_bmp.npy')
jpg_npy_path = str(test_npy_dir /'ref_rgb_8bit_jpg.npy')
png_npy_path = str(test_npy_dir /'ref_rgba_8bit_png.npy')
tif_npy_path = str(test_npy_dir /'ref_rgb_8bit_tif.npy')
cfa_npy_path = str(test_npy_dir /'ref_bayer_10bit_cfa.npy')
rawmipi12_npy_path = str(test_npy_dir /'ref_bayer_12bit_rawmipi.npy')
rawmipi10_npy_path = str(test_npy_dir /'ref_bayer_10bit_rawmipi.npy')
dng_npy_path = str(test_npy_dir /'ref_bayer_dng.npy')

# exif_jpg_path = str(test_images_base_dir / 'Canon_40D.jpg')
# exif = read_image_exif(exif_jpg_path)


# exif.isoSpeedRatings = 200
# exif.imageWidth = 100
# exif.imageHeight = 68
# exif.make = 'LHY'
# print('exif', exif.imageWidth, exif.imageHeight, exif.orientation, exif.isoSpeedRatings)

# exif_jpg_out_path = str(test_images_base_dir / 'write_test.jpg')
# write_image_exif(exif_jpg_out_path, exif)


def __get_file_hash(file_name):
    content = open(file_name, 'rb').read()
    hash = hashlib.md5(content).hexdigest()
    return hash


@pytest.fixture()
def regression(pytestconfig):
    return Regression('test_image_io_binding', pytestconfig)



@pytest.mark.parametrize('image_path, ref_numpy_info, ref_image_info, ref_pixel_values',
                            [
                            (raw_path, (np.dtype('uint16'), (3072, 4080), 2 ), (PixelType.BAYER_GBRG, 16, ImageLayout.PLANAR), raw_npy_path),
                            (bmp_path, (np.dtype('uint8'), (551, 603, 3), 3), (PixelType.RGB, 8, ImageLayout.INTERLEAVED), bmp_npy_path),
                            (jpg_path, (np.dtype('uint8'), (3024, 4032, 3), 3), (PixelType.RGB, 8, ImageLayout.INTERLEAVED), jpg_npy_path),
                            (png_path, (np.dtype('uint8'), (826, 3632, 4), 3), (PixelType.RGBA, 8, ImageLayout.INTERLEAVED), png_npy_path),
                            (tif_path, (np.dtype('uint8'), (576, 740, 3), 3), (PixelType.RGB, 8, ImageLayout.INTERLEAVED), tif_npy_path),
                            (cfa_path, (np.dtype('uint16'), (3000, 4000), 2), (PixelType.BAYER_RGGB, 10, ImageLayout.PLANAR), cfa_npy_path),
                            (rawmipi10_path, (np.dtype('uint16'), (4512, 6016), 2), (PixelType.BAYER_GRBG, 10, ImageLayout.PLANAR), rawmipi10_npy_path),
                            (rawmipi12_path, (np.dtype('uint16'), (3072, 4080), 2), (PixelType.BAYER_GBRG, 12, ImageLayout.PLANAR), rawmipi12_npy_path),
                            (dng_path, (np.dtype('uint16'), (2250, 4000), 2), (PixelType.BAYER_RGGB, 16, ImageLayout.PLANAR), dng_npy_path),
                            ])
def test_read_image(image_path, ref_numpy_info, ref_image_info, ref_pixel_values):

    image, metadata = read_image(image_path)

    assert isinstance(image, np.ndarray)
    assert (image.dtype, image.shape, image.ndim) == ref_numpy_info
    assert (metadata.fileInfo.pixelType,  metadata.fileInfo.pixelPrecision, metadata.fileInfo.imageLayout) == ref_image_info
    ref_image = np.load(ref_pixel_values)
    assert np.array_equal(ref_image, image)

@pytest.mark.parametrize('output_path, numpy_array_path, pixel_type, image_layout, pixel_precision, file_format, ref_path',
                [
                    (output_raw_path, raw_npy_path, PixelType.BAYER_GBRG, ImageLayout.PLANAR, 0, FileFormat.PLAIN, raw_path),
                    (output_bmp_path, bmp_npy_path, PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, bmp_path),
                    # (output_jpg_path, jpg_npy_path, PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, jpg_path),
                    # (output_png_path, png_npy_path, PixelType.RGBA, ImageLayout.INTERLEAVED, 0, None, png_path),
                    # (output_tif_path, tif_npy_path, PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, tif_path),
                    # (output_cfa_path, cfa_npy_path, PixelType.BAYER_RGGB, ImageLayout.PLANAR, 0, None, cfa_path),
                    # (output_rawmipi12_path, rawmipi12_npy_path, PixelType.BAYER_GBRG, ImageLayout.PLANAR, 12, None, rawmipi12_path),
                    # (output_rawmipi10_path, rawmipi10_npy_path, PixelType.BAYER_RGGB, ImageLayout.PLANAR, 10, None, rawmipi10_path),
                    # (output_dng_path, dng_npy_path, PixelType.BAYER_RGGB, ImageLayout.PLANAR, 0, None, dng_path),
                ])
def test_write_image(output_path, numpy_array_path, pixel_type, image_layout, pixel_precision, file_format, ref_path):
    
    metadata = ImageMetadata()
    metadata.fileInfo.pixelType, metadata.fileInfo.imageLayout, metadata.fileInfo.pixelPrecision, metadata.fileInfo.fileFormat = pixel_type, image_layout, pixel_precision, file_format
    write_options = ImageWriter.Options(metadata)
    write_options.fileFormat = metadata.fileInfo.fileFormat
    image = np.load(numpy_array_path)
    write_image(output_path, image, write_options=write_options)

    output_hash = __get_file_hash(output_path)
    ref_hash = __get_file_hash(ref_path)

    assert output_hash == ref_hash
    

