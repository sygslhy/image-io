from image_io import ImageMetadata, ExifMetadata, ImageWriter, FileFormat, PixelType, ImageLayout
from image_io import read_image, read_image_exif, write_image, write_image_exif
import numpy as np

import pytest
from pathlib import Path
import hashlib

test_images_dir = Path('./test/images/')
test_npy_dir = Path('./test/npy/')
test_outputs_dir = Path('./test/_outputs/')
test_ref_dir = Path('./test/ref/')
test_exif_dir = Path('./test/exif/')

raw_path = str(test_images_dir / 'plain_raw_16bit.raw')
bmp_path = str(test_images_dir / 'rgb_8bit.bmp')
jpg_path = str(test_images_dir / 'rgb_8bit.jpg')
png_path = str(test_images_dir / 'rgba_8bit.png')
tif_path = str(test_images_dir / 'rgb_8bit.tif')
cfa_path = str(test_images_dir / 'bayer_10bit.cfa')
rawmipi12_path = str(test_images_dir / 'raw_12bit.RAWMIPI12')
rawmipi10_path = str(test_images_dir / 'raw_10bit.RAWMIPI')
dng_path = str(test_images_dir / 'raw.DNG')


exif_read_jpg_path = str(test_exif_dir / 'Canon_40D.jpg')
exif_read_tif_path = str(test_exif_dir / 'dwsample-tiff-1280.tif')
exif_read_dng_path = str(test_exif_dir / 'raw.DNG')
exif_write_jpg_path = str(test_exif_dir / 'rgb_8bit.jpg')
exif_write_tif_path = str(test_exif_dir / 'rgb_8bit.tif')

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


ref_raw_path = str(test_ref_dir / 'plain_raw_16bit.raw')
ref_bmp_path = str(test_ref_dir /'rgb_8bit.bmp')
ref_jpg_path = str(test_ref_dir /'rgb_8bit.jpg')
ref_png_path = str(test_ref_dir /'rgba_8bit.png')
ref_tif_path = str(test_ref_dir /'rgb_8bit.tif')
ref_cfa_path = str(test_ref_dir /'bayer_10bit.cfa')
ref_rawmipi12_path = str(test_ref_dir /'raw_12bit.RAWMIPI12')
ref_rawmipi10_path = str(test_ref_dir /'raw_10bit.RAWMIPI')
ref_dng_path = str(test_ref_dir /'raw.DNG')


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
                    (output_raw_path, raw_npy_path, PixelType.BAYER_GBRG, ImageLayout.PLANAR, 0, FileFormat.PLAIN, ref_raw_path),
                    (output_bmp_path, bmp_npy_path, PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, ref_bmp_path),
                    # (output_jpg_path, jpg_npy_path, PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, ref_jpg_path),
                    (output_png_path, png_npy_path, PixelType.RGBA, ImageLayout.INTERLEAVED, 0, None, ref_png_path),
                    (output_tif_path, tif_npy_path, PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, ref_tif_path),
                    (output_cfa_path, cfa_npy_path, PixelType.BAYER_RGGB, ImageLayout.PLANAR, 0, None, ref_cfa_path),
                    (output_rawmipi12_path, rawmipi12_npy_path, PixelType.BAYER_GBRG, ImageLayout.PLANAR, 12, None, ref_rawmipi12_path),
                    (output_rawmipi10_path, rawmipi10_npy_path, PixelType.BAYER_RGGB, ImageLayout.PLANAR, 10, None, ref_rawmipi10_path),
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

@pytest.mark.parametrize('image_path, ref_exif',
                        [ (exif_read_jpg_path, ('2008:05:30 15:56:01\x00', 1/160, 135, 71/10, 100, 'Canon\x00', 'Canon EOS 40D\x00', 1, 'GIMP 2.4.5\x00')),
                           (exif_read_dng_path, ('2021:07:21 17:13:42', 1/40, 4.5, 28/10, 800, 'DJI', 'FC3170', 1, 'Adobe Photoshop Lightroom 11.4.1 Classic (Macintosh)')),
                          (exif_read_tif_path, ('2022-06-23 15:35:43', 1/10, 125, 17/10, 200, 'Test tif', 'Impact', 1, 'Adobe Photoshop CC 2017 (Windows)')) 

                        ]
)
def test_read_exif(image_path, ref_exif):
    exif = read_image_exif(image_path)
    epsilon = 0.000001
    assert exif.dateTimeOriginal == ref_exif[0]
    assert abs(exif.exposureTime.asDouble() - ref_exif[1]) < epsilon
    assert abs(exif.focalLength.asDouble() - ref_exif[2]) < epsilon
    assert abs(exif.fNumber.asDouble() - ref_exif[3]) < epsilon
    assert (exif.isoSpeedRatings, exif.make, exif.model, exif.orientation, exif.software) == ref_exif[4:]




@pytest.mark.parametrize('image_path',
                        [ (exif_write_jpg_path),
                          (exif_write_tif_path) 
                        ]
)

def test_write_exif(image_path):
    
    assert Path(image_path).exists()
    
    exif = ExifMetadata()

    exif.make = 'Test write exif'
    exif.model = 'exif writer'
    exif.isoSpeedRatings = 850
    exif.exposureTime = ExifMetadata.Rational(1, 100)
    exif.focalLength = ExifMetadata.Rational(35, 1)
    exif.fNumber = ExifMetadata.Rational(22, 10)
    exif.dateTimeOriginal = '2023-10-23 12:30:43'
    exif.orientation = 1
    exif.software = 'change'
    write_image_exif(image_path, exif)

    epsilon = 0.000001
    parsed_exif = read_image_exif(image_path) 
    assert parsed_exif.dateTimeOriginal == exif.dateTimeOriginal
    assert abs(parsed_exif.exposureTime.asDouble() - exif.exposureTime.asDouble()) < epsilon
    assert abs(parsed_exif.focalLength.asDouble() - exif.focalLength.asDouble()) < epsilon
    assert abs(parsed_exif.fNumber.asDouble() - exif.fNumber.asDouble()) < epsilon
    assert (parsed_exif.make, parsed_exif.model) == (exif.make, exif.model) 
    assert (parsed_exif.isoSpeedRatings, parsed_exif.make, parsed_exif.model, parsed_exif.orientation, parsed_exif.software) == (exif.isoSpeedRatings, exif.make, exif.model, exif.orientation, exif.software)


