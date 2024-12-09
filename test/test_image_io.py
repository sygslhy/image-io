import hashlib
from pathlib import Path

import numpy as np
import pytest

from test import root_dir
from cxx_image_io import (ExifMetadata, FileFormat, ImageLayout, ImageMetadata,
                          PixelRepresentation, RgbColorSpace, ImageWriter,
                          Matrix3, UnorderdMapSemanticMasks, PixelType,
                          read_exif, read_image, write_exif, write_image)

test_images_dir = Path(root_dir, 'images/')
test_npy_dir = Path(root_dir, 'npy/')
test_outputs_dir = Path(root_dir, '_outputs/')

test_data = {
    'raw': {
        'file': 'bayer_16bit.plain16',
        'npy': 'bayer_16bit_plain.npy'
    },
    'bmp': {
        'file': 'rgb_8bit.bmp',
        'npy': 'rgb_8bit_bmp.npy'
    },
    'jpg': {
        'file': 'rgb_8bit.jpg',
        'npy': 'rgb_8bit_jpg.npy'
    },
    'png': {
        'file': 'rgb_8bit.png',
        'npy': 'rgb_8bit_png.npy'
    },
    'png_16bit': {
        'file': 'gray_16bit.png',
        'npy': 'gray_16bit_png.npy'
    },

    'tif': {
        'file': 'rgb_8bit.tif',
        'npy': 'rgb_8bit_tif.npy'
    },
    'tif_16bit': {
        'file': 'bayer_16bit.tif',
        'npy': 'bayer_16bit_tif.npy'
    },

    'cfa': {
        'file': 'bayer_16bit.cfa',
        'npy': 'bayer_16bit_cfa.npy'
    },
    'rawmipi12': {
        'file': 'bayer_12bit.RAWMIPI12',
        'npy': 'bayer_12bit_rawmipi.npy'
    },
    'rawmipi10': {
        'file': 'bayer_10bit.RAWMIPI',
        'npy': 'bayer_10bit_rawmipi.npy'
    },
    'dng': {
        'file': 'bayer_12bit.dng',
        'npy': 'bayer_12bit_dng.npy'
    },
    'yuv': {
        'file': 'raw_420.yuv',
        'npy': 'raw_420_yuv.npy'
    },
    'nv12': {
        'file': 'raw.nv12',
        'npy': 'raw_nv12.npy'
    }
}

__epsilon = 0.0000001
__exif = ExifMetadata()
__exif.make = 'Canon'
__exif.model = 'Canon EOS 350D DIGITAL'
__exif.isoSpeedRatings = 100
__exif.exposureTime = ExifMetadata.Rational(1, 800)
__exif.focalLength = ExifMetadata.Rational(20, 1)
__exif.fNumber = ExifMetadata.Rational(71, 10)
__exif.dateTimeOriginal = '2008:12:14 15:54:54'
__exif.orientation = 1
__exif.software = 'change'
__exif.exposureBiasValue = ExifMetadata.SRational(0, 1)


def __get_file_hash(file_name):
    content = open(file_name, 'rb').read()
    hash = hashlib.md5(content).hexdigest()
    return hash


def __check_exif_values(exif, ref_exif):
    assert exif.dateTimeOriginal == ref_exif[0]
    assert abs(exif.exposureTime.asDouble() - ref_exif[1]) < __epsilon
    assert abs(exif.focalLength.asDouble() - ref_exif[2]) < __epsilon
    assert abs(exif.fNumber.asDouble() - ref_exif[3]) < __epsilon
    assert (exif.isoSpeedRatings, exif.make, exif.model, exif.orientation,
            exif.software) == ref_exif[4:]


def test_parse_metadata():
    _, metadata = read_image(test_images_dir / test_data['rawmipi12']['file'])
    assert metadata is not None

    # Check fileInfo members
    assert metadata.fileInfo is not None
    assert metadata.fileInfo.fileFormat == FileFormat.RAW12
    assert metadata.fileInfo.imageLayout == ImageLayout.PLANAR
    assert metadata.fileInfo.pixelType == PixelType.BAYER_GBRG
    assert metadata.fileInfo.pixelPrecision == 12
    assert metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT16
    assert metadata.fileInfo.width == 400
    assert metadata.fileInfo.height == 300

    # Check shootingParams members
    assert metadata.shootingParams is not None
    assert abs(metadata.shootingParams.aperture - 2.2) < __epsilon
    assert abs(metadata.shootingParams.exposureTime - 0.016631526) < __epsilon
    assert abs(metadata.shootingParams.sensitivity - 1.2) < __epsilon
    assert abs(metadata.shootingParams.totalGain - 1.001035) < __epsilon
    assert metadata.shootingParams.sensorGain == 1.0
    assert abs(metadata.shootingParams.ispGain - 1.001035) < __epsilon

    # Check cameraControls members
    assert metadata.cameraControls is not None
    assert abs(metadata.cameraControls.whiteBalance.gainR -
               2.223459892023346) < __epsilon
    assert abs(metadata.cameraControls.whiteBalance.gainB -
               1.462103373540856) < __epsilon

    array_r = np.array(metadata.cameraControls.colorShading.gainR, copy=False)
    array_b = np.array(metadata.cameraControls.colorShading.gainB, copy=False)
    assert array_r.shape == (3, 3) and array_b.shape == (3, 3)
    np.array_equal(
        array_r, np.array([[2.0, 1.5, 2.0], [1.5, 1.0, 1.5], [2.0, 1.5, 2.0]]))
    np.array_equal(
        array_b, np.array([[3.0, 2.5, 3.0], [2.5, 1.0, 2.5], [3.0, 2.5, 3.0]]))
    assert metadata.cameraControls.faceDetection[
        0].x == metadata.cameraControls.faceDetection[0].y == 0
    assert metadata.cameraControls.faceDetection[0].width == 100
    assert metadata.cameraControls.faceDetection[0].height == 200
    assert metadata.cameraControls.faceDetection[
        1].x == metadata.cameraControls.faceDetection[1].y == 0
    assert metadata.cameraControls.faceDetection[1].width == 120
    assert metadata.cameraControls.faceDetection[1].height == 180

    # Check calibrationData members
    assert metadata.calibrationData is not None
    assert metadata.calibrationData.blackLevel == 256
    assert metadata.calibrationData.whiteLevel == 4095.0
    array_g = np.array(metadata.calibrationData.vignetting, copy=False)
    np.array_equal(
        array_g, np.array([[2.0, 1.5, 2.0], [1.5, 1.1, 1.5], [2.0, 1.5, 2.0]]))
    assert metadata.calibrationData.colorMatrixTarget == RgbColorSpace.SRGB
    array_color_matrix = np.array(metadata.calibrationData.colorMatrix,
                                  copy=False)
    np.array_equal(
        array_color_matrix,
        np.array([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]))

    # Check exifMetadata members
    assert metadata.exifMetadata is not None
    assert metadata.exifMetadata.imageWidth == 4080
    assert metadata.exifMetadata.imageHeight == 3072
    assert metadata.exifMetadata.imageDescription == 'Raw 12 bit image'
    assert metadata.exifMetadata.make == 'Xiaomi'
    assert metadata.exifMetadata.model == 'M2102K1G'
    assert metadata.exifMetadata.orientation == 1
    assert metadata.exifMetadata.software == 'Impact'
    assert metadata.exifMetadata.exposureTime.numerator == 1
    assert metadata.exifMetadata.exposureTime.denominator == 60
    assert metadata.exifMetadata.fNumber.numerator == 195
    assert metadata.exifMetadata.fNumber.denominator == 100
    assert metadata.exifMetadata.isoSpeedRatings == 50
    assert metadata.exifMetadata.dateTimeOriginal == '2021:11:16 13:15:20'
    assert metadata.exifMetadata.focalLength.numerator == 7590
    assert metadata.exifMetadata.focalLength.denominator == 1000
    assert metadata.exifMetadata.focalLengthIn35mmFilm == 7
    assert metadata.exifMetadata.brightnessValue.numerator == 0
    assert metadata.exifMetadata.brightnessValue.denominator == 100
    assert metadata.exifMetadata.exposureBiasValue.numerator == 0
    assert metadata.exifMetadata.exposureBiasValue.denominator == 6

    assert isinstance(metadata.semanticMasks, UnorderdMapSemanticMasks)


@pytest.mark.parametrize('image_type, ref_numpy_info, ref_image_info',
                         [('raw', (np.dtype('uint16'), (180, 240), 2),
                           (PixelType.BAYER_RGGB, 16, ImageLayout.PLANAR)),
                          ('bmp', (np.dtype('uint8'), (275, 301, 3), 3),
                           (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
                          ('jpg', (np.dtype('uint8'), (68, 100, 3), 3),
                           (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
                          ('png', (np.dtype('uint8'), (60, 180, 3), 3),
                           (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
                          ('png_16bit', (np.dtype('uint16'), (180, 240), 2),
                           (PixelType.GRAYSCALE, 16, ImageLayout.PLANAR)),
                          ('tif', (np.dtype('uint8'), (68, 100, 3), 3),
                           (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
                           ('tif_16bit', (np.dtype('uint16'), (180, 240), 2),
                           (PixelType.BAYER_RGGB, 16, ImageLayout.PLANAR)),
                          ('cfa', (np.dtype('uint16'), (180, 240), 2),
                           (PixelType.BAYER_RGGB, 16, ImageLayout.PLANAR)),
                          ('rawmipi10', (np.dtype('uint16'), (180, 240), 2),
                           (PixelType.BAYER_GRBG, 10, ImageLayout.PLANAR)),
                          ('rawmipi12', (np.dtype('uint16'), (300, 400), 2),
                           (PixelType.BAYER_GBRG, 12, ImageLayout.PLANAR)),
                          ('dng', (np.dtype('uint16'), (2314, 3474), 2),
                           (PixelType.BAYER_RGGB, 12, ImageLayout.PLANAR)),
                          ('yuv', (np.dtype('uint8'), (102, 100), 2),
                           (PixelType.YUV, 0, ImageLayout.YUV_420)),
                          ('nv12', (np.dtype('uint8'), (102, 100), 2),
                           (PixelType.YUV, 0, ImageLayout.NV12))])
def test_read_image(image_type, ref_numpy_info, ref_image_info):
    image, metadata = read_image(test_images_dir /
                                 test_data[image_type]['file'])
    assert isinstance(image, np.ndarray)
    assert (image.dtype, image.shape, image.ndim) == ref_numpy_info
    assert (metadata.fileInfo.pixelType, metadata.fileInfo.pixelPrecision,
            metadata.fileInfo.imageLayout) == ref_image_info

    ref_image = np.load(test_npy_dir / test_data[image_type]['npy'])

    assert np.array_equal(ref_image, image)


@pytest.mark.parametrize(
    'image_type, pixel_type, image_layout, pixel_precision, file_format, only_pixel_cmp',
    [
        ('raw', PixelType.BAYER_GBRG, ImageLayout.PLANAR, 0, FileFormat.PLAIN,
         False),
        ('bmp', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
        ('jpg', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
        ('png', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
        ('png_16bit', PixelType.GRAYSCALE, ImageLayout.PLANAR, 16, None, True),
        ('tif', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
        ('tif_16bit', PixelType.RGB, ImageLayout.PLANAR, 16, None, True),
        ('cfa', PixelType.BAYER_RGGB, ImageLayout.PLANAR, 0, None, True),
        ('rawmipi12', PixelType.BAYER_GBRG, ImageLayout.PLANAR, 12, None,
         False),
        ('rawmipi10', PixelType.BAYER_RGGB, ImageLayout.PLANAR, 10, None,
         False),
        ('dng', PixelType.BAYER_RGGB, ImageLayout.PLANAR, 12, None, True),
        ('yuv', PixelType.YUV, ImageLayout.YUV_420, 0, FileFormat.PLAIN,
         False),
        ('nv12', PixelType.YUV, ImageLayout.NV12, 0, FileFormat.PLAIN, False),
    ])
def test_write_image(image_type, pixel_type, image_layout, pixel_precision,
                     file_format, only_pixel_cmp):
    metadata = ImageMetadata()
    metadata.fileInfo.pixelType, metadata.fileInfo.imageLayout, metadata.fileInfo.pixelPrecision, metadata.fileInfo.fileFormat = pixel_type, image_layout, pixel_precision, file_format
    metadata.exifMetadata = __exif
    output_path = test_outputs_dir / test_data[image_type]['file']
    if '.dng' in output_path.suffix:
        metadata.cameraControls.whiteBalance = ImageMetadata.WhiteBalance()
        metadata.cameraControls.whiteBalance.gainR = 2.2502453327178955
        metadata.cameraControls.whiteBalance.gainB = 1.493620753288269
        metadata.shootingParams.ispGain = 1.1892070770263672
        metadata.calibrationData.blackLevel = 258
        metadata.calibrationData.whiteLevel = 4095
        metadata.calibrationData.colorMatrix = Matrix3(
            np.array([
                [1.7485008239746094, -0.9061940312385559, 0.15769319236278534],
                [0.017115920782089233, 1.318513035774231, -0.3356289267539978],
                [
                    0.03677308186888695,
                    -0.3459629416465759 - 0.3356289267539978, 1.309189796447754
                ]
            ]))

    write_options = ImageWriter.Options(metadata)
    write_options.fileFormat = metadata.fileInfo.fileFormat
    image = np.load(test_npy_dir / test_data[image_type]['npy'])
    write_image(output_path, image, write_options)

    # special case , jpg bmp header has different varaition due to different machine
    # so cannot compare the sha1, only compre the image content.
    if only_pixel_cmp:
        out_image, metadata = read_image(output_path)
        np.array_equal(out_image, image)
        return

    output_hash = __get_file_hash(output_path)
    ref_hash = __get_file_hash(test_images_dir / test_data[image_type]['file'])
    assert output_hash == ref_hash


@pytest.mark.parametrize('image_type, ref_exif', [
    ('jpg', ('2008:05:30 15:56:01\x00', 1 / 160, 135, 71 / 10, 100,
             'Canon\x00', 'Canon EOS 40D\x00', 1, 'GIMP 2.4.5\x00')),
    ('dng', ('2008:12:14 15:54:54', 1 / 800, 20, 71 / 10, 100, 'Canon',
             'Canon EOS 350D DIGITAL', 1, None)),
    ('tif', ('2008:05:30 15:56:01', 1 / 160, 135, 71 / 10, 100, 'Canon',
             'Canon EOS 40D', 1, 'GIMP 2.4.5')),
])
def test_read_exif(image_type, ref_exif):
    image_path = test_images_dir / test_data[image_type]['file']
    exif = read_exif(image_path)
    __check_exif_values(exif, ref_exif)

    _, metadata = read_image(image_path)
    __check_exif_values(metadata.exifMetadata, ref_exif)


@pytest.mark.parametrize('image_type', [('jpg'), ('tif')])
def test_write_exif(image_type):
    image_path = test_outputs_dir / test_data[image_type]['file']
    assert Path(image_path).exists()
    write_exif(image_path, __exif)
    parsed_exif = read_exif(image_path)
    assert parsed_exif.dateTimeOriginal == __exif.dateTimeOriginal
    assert abs(parsed_exif.exposureTime.asDouble() -
               __exif.exposureTime.asDouble()) < __epsilon
    assert abs(parsed_exif.focalLength.asDouble() -
               __exif.focalLength.asDouble()) < __epsilon
    assert abs(parsed_exif.fNumber.asDouble() -
               __exif.fNumber.asDouble()) < __epsilon
    assert (parsed_exif.make, parsed_exif.model) == (__exif.make, __exif.model)
    assert (parsed_exif.isoSpeedRatings, parsed_exif.orientation,
            parsed_exif.software) == (__exif.isoSpeedRatings,
                                      __exif.orientation, __exif.software)
