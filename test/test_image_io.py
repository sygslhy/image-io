import hashlib
from pathlib import Path

from test import root_dir

import numpy as np
import pytest

from cxx_image_io import (ExifMetadata, FileFormat, ImageLayout, ImageMetadata, ImageWriter, Matrix3,
                          PixelRepresentation, PixelType, RgbColorSpace, UnorderdMapSemanticMasks, read_exif,
                          read_image, write_exif, write_image)

test_images_dir = Path(root_dir, 'images/')
test_npy_dir = Path(root_dir, 'npy/')
test_outputs_dir = Path(root_dir, '_outputs/')

test_data = {
    'raw': {
        'file': 'bayer_16bit.plain16',
        'npy': 'bayer_16bit_plain.npy',
        'hash': 'cb05abf125b0b5688bfba6e47d95e456ce2d791fa00a7edd9a22488701070df9'
    },
    'bmp': {
        'file': 'rgb_8bit.bmp',
        'npy': 'rgb_8bit_bmp.npy',
        'hash': 'c3f4017b0cdfc081c7fc7dd3915b24e62a4051b728233fc5675c2c9abea583fc'
    },
    'jpg': {
        'file': 'rgb_8bit.jpg',
        'npy': 'rgb_8bit_jpg.npy',
        'hash': '0f1dddb05d47ce7aedd708217745fdfcb80b686eb005afba6d2859a47ad5cdfa'
    },
    'png': {
        'file': 'rgb_8bit.png',
        'npy': 'rgb_8bit_png.npy',
        'hash': 'e6f0d601a79b4e0ba75e022f55434a57e8ff98bab7ed7f5809642c1bf06844e0'
    },
    'png_16bit': {
        'file': 'gray_16bit.png',
        'npy': 'gray_16bit_png.npy',
        'hash': 'cb05abf125b0b5688bfba6e47d95e456ce2d791fa00a7edd9a22488701070df9'
    },
    'tif': {
        'file': 'rgb_8bit.tif',
        'npy': 'rgb_8bit_tif.npy',
        'hash': '0f1dddb05d47ce7aedd708217745fdfcb80b686eb005afba6d2859a47ad5cdfa'
    },
    'tif_16bit': {
        'file': 'bayer_16bit.tif',
        'npy': 'bayer_16bit_tif.npy',
        'hash': 'cb05abf125b0b5688bfba6e47d95e456ce2d791fa00a7edd9a22488701070df9'
    },
    'cfa': {
        'file': 'bayer_16bit.cfa',
        'npy': 'bayer_16bit_cfa.npy',
        'hash': 'cb05abf125b0b5688bfba6e47d95e456ce2d791fa00a7edd9a22488701070df9'
    },
    'rawmipi12': {
        'file': 'bayer_12bit.RAWMIPI12',
        'npy': 'bayer_12bit_rawmipi.npy',
        'hash': '240e10a13e6e3dcf7e9949fa59fc270c43b06c9be90e38c739517b10d84f5b21'
    },
    'rawmipi10': {
        'file': 'bayer_10bit.RAWMIPI',
        'npy': 'bayer_10bit_rawmipi.npy',
        'hash': '4de8edeb92793be20d75136603c47e7bc8cb5ce1211d2f5ce8dfb9cebaa9a13d'
    },
    'dng': {
        'file': 'bayer_12bits.dng',
        'npy': 'bayer_12bits_dng.npy',
        'hash': '5ffb00590e087e2999423b25088122ad4d422e3542af75e3f116278e94effba6'
    },
    'yuv': {
        'file': 'raw_420.yuv',
        'npy': 'raw_420_yuv.npy',
        'hash': '2d050c28e96f686178913f0a07c9aaddfd6c8e346ddd824cbf5e9dd6854898b0'
    },
    'nv12': {
        'file': 'raw.nv12',
        'npy': 'raw_nv12.npy',
        'hash': '9364d42743d848f82f5a3b7e5065ca800b593388dbc66f8b04716781f9a6b811'
    },
    'canon': {
        'file': 'RAW_CANON_EOS_1DX.CR2',
        'hash': '9733725fb94b81e48fe3adce124a63fcc35b68f8b86948a595260476f98aed55'
    },
    'panasonic': {
        'file': 'RAW_PANASONIC_LX3.RW2',
        'hash': '05b693f1314facf0743a418f036042c5e98eb9e79ff03a7efa3db547dfdbadb2'
    },
    'sony': {
        'file': 'RAW_SONY_RX100.ARW',
        'hash': '03c2ba312fc7e026da40211b8273aad2a83bca40d43e28e895d9fd31044058ba'
    },
    'nikon': {
        'file': 'RAW_NIKON_D3X.NEF',
        'hash': '5113095837ef100d454d0230669e06c54b089aa8c075968ca59d681b7a618bd0'
    },
    'leica': {
        'file': 'RAW_LEICA_DLUX3.RAW',
        'hash': 'f918908ada149bc56837aa9db4a9fe741b9a8674340d636c71d936f4ba7b1489'
    },
    'pentax': {
        'file': 'RAW_PENTAX_KX.PEF',
        'hash': 'aaad2264581e3863f408289c1ce480ac4551705e1d4420f5a6fc52179dbb01fb'
    },
    'samsung': {
        'file': 'RAW_SAMSUNG_NX300M.SRW',
        'hash': 'e4892b734600f92575d4792d4c15727e88bd4d15d6a2263c3f8fa4740dd4f223'
    },
    'olympus': {
        'file': 'RAW_OLYMPUS_E3.ORF',
        'hash': '5e69f203e5062c9c760fb0aef333702c0e0d23642d2106acc3a2a63887982a22'
    },
    'kodak_slr': {
        'file': 'RAW_KODAK_DCSPRO.DCR',
        'hash': '16728a5a2afb8e13660dc49b070f5b3e372ac237c6e0a9081be237a0a53ceab2'
    },
    'kodak': {
        'file': 'RAW_KODAK_DC120.KDC',
        'hash': '3f83c8efeeb2f7ca4f5977b42f154fdcbf4e41a34d4ce9e149908f42919a2b97'
    },
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
    hash = hashlib.sha256(content).hexdigest()
    return hash


def __hash_image(image_array):
    image_bytes = image_array.tobytes()
    hash = hashlib.sha256(image_bytes).hexdigest()
    return hash


def __check_exif_values(exif, ref_exif):
    assert exif.dateTimeOriginal == ref_exif[0]
    assert abs(exif.exposureTime.asDouble() - ref_exif[1]) < __epsilon
    assert abs(exif.focalLength.asDouble() - ref_exif[2]) < __epsilon
    assert abs(exif.fNumber.asDouble() - ref_exif[3]) < __epsilon
    assert (exif.isoSpeedRatings, exif.make, exif.model, exif.orientation, exif.software) == ref_exif[4:]


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
    assert abs(metadata.cameraControls.whiteBalance.gainR - 2.223459892023346) < __epsilon
    assert abs(metadata.cameraControls.whiteBalance.gainB - 1.462103373540856) < __epsilon

    array_r = np.array(metadata.cameraControls.colorShading.gainR, copy=False)
    array_b = np.array(metadata.cameraControls.colorShading.gainB, copy=False)
    assert array_r.shape == (3, 3) and array_b.shape == (3, 3)
    np.array_equal(array_r, np.array([[2.0, 1.5, 2.0], [1.5, 1.0, 1.5], [2.0, 1.5, 2.0]]))
    np.array_equal(array_b, np.array([[3.0, 2.5, 3.0], [2.5, 1.0, 2.5], [3.0, 2.5, 3.0]]))
    assert metadata.cameraControls.faceDetection[0].x == metadata.cameraControls.faceDetection[0].y == 0
    assert metadata.cameraControls.faceDetection[0].width == 100
    assert metadata.cameraControls.faceDetection[0].height == 200
    assert metadata.cameraControls.faceDetection[1].x == metadata.cameraControls.faceDetection[1].y == 0
    assert metadata.cameraControls.faceDetection[1].width == 120
    assert metadata.cameraControls.faceDetection[1].height == 180

    # Check calibrationData members
    assert metadata.calibrationData is not None
    assert metadata.calibrationData.blackLevel == 256
    assert metadata.calibrationData.whiteLevel == 4095.0
    array_g = np.array(metadata.calibrationData.vignetting, copy=False)
    np.array_equal(array_g, np.array([[2.0, 1.5, 2.0], [1.5, 1.1, 1.5], [2.0, 1.5, 2.0]]))
    assert metadata.calibrationData.colorMatrixTarget == RgbColorSpace.SRGB
    array_color_matrix = np.array(metadata.calibrationData.colorMatrix, copy=False)
    np.array_equal(array_color_matrix, np.array([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]))

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


def test_camera_raw_metadata():
    _, metadata = read_image(test_images_dir / test_data['canon']['file'])
    assert metadata is not None

    # Check fileInfo members
    assert metadata.fileInfo is not None
    assert metadata.fileInfo.imageLayout == ImageLayout.PLANAR
    assert metadata.fileInfo.pixelType == PixelType.BAYER_RGGB
    assert metadata.fileInfo.pixelPrecision == 14
    assert metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT16
    assert metadata.fileInfo.width == 5218
    assert metadata.fileInfo.height == 3482

    # Check cameraControls members
    assert metadata.cameraControls is not None
    assert abs(metadata.cameraControls.whiteBalance.gainR - 1.75390625) < __epsilon
    assert abs(metadata.cameraControls.whiteBalance.gainB - 1.4775390625) < __epsilon

    # Check calibrationData members
    assert metadata.calibrationData is not None
    assert metadata.calibrationData.blackLevel == 2048
    assert metadata.calibrationData.whiteLevel == 15438
    array_color_matrix = np.array(metadata.calibrationData.colorMatrix, copy=False)
    np.array_equal(
        array_color_matrix,
        np.array([[1.9404515027999878, -1.1166307926177979, 0.17617927491664886],
                  [-0.21374493837356567, 1.6440128087997437, -0.430267870426178],
                  [0.021280933171510696, -0.5217925906181335, 1.500511646270752]]))

    # Check exifMetadata members
    assert metadata.exifMetadata is not None
    assert metadata.exifMetadata.make == 'Canon'
    assert metadata.exifMetadata.model == 'EOS-1D X'
    assert metadata.exifMetadata.orientation == 1
    assert metadata.exifMetadata.exposureTime.numerator == 1
    assert metadata.exifMetadata.exposureTime.denominator == 80
    assert metadata.exifMetadata.fNumber.numerator == 56
    assert metadata.exifMetadata.fNumber.denominator == 10
    assert metadata.exifMetadata.isoSpeedRatings == 1600
    assert metadata.exifMetadata.dateTimeOriginal == '2012:09:06 07:48:25'
    assert metadata.exifMetadata.focalLength.numerator == 700
    assert metadata.exifMetadata.focalLength.denominator == 10

    assert isinstance(metadata.semanticMasks, UnorderdMapSemanticMasks)


@pytest.mark.parametrize('image_type, ref_numpy_info, ref_image_info', [
    ('raw', (np.dtype('uint16'), (180, 240), 2), (PixelType.BAYER_RGGB, 16, ImageLayout.PLANAR)),
    ('bmp', (np.dtype('uint8'), (275, 301, 3), 3), (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
    ('jpg', (np.dtype('uint8'), (68, 100, 3), 3), (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
    ('png', (np.dtype('uint8'), (60, 180, 3), 3), (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
    ('png_16bit', (np.dtype('uint16'), (180, 240), 2), (PixelType.GRAYSCALE, 16, ImageLayout.PLANAR)),
    ('tif', (np.dtype('uint8'), (68, 100, 3), 3), (PixelType.RGB, 8, ImageLayout.INTERLEAVED)),
    ('tif_16bit', (np.dtype('uint16'), (180, 240), 2), (PixelType.BAYER_RGGB, 16, ImageLayout.PLANAR)),
    ('cfa', (np.dtype('uint16'), (180, 240), 2), (PixelType.BAYER_RGGB, 16, ImageLayout.PLANAR)),
    ('rawmipi10', (np.dtype('uint16'), (180, 240), 2), (PixelType.BAYER_GRBG, 10, ImageLayout.PLANAR)),
    ('rawmipi12', (np.dtype('uint16'), (300, 400), 2), (PixelType.BAYER_GBRG, 12, ImageLayout.PLANAR)),
    ('dng', (np.dtype('uint16'), (2314, 3474), 2), (PixelType.BAYER_RGGB, 12, ImageLayout.PLANAR)),
    ('yuv', (np.dtype('uint8'), (102, 100), 2), (PixelType.YUV, 0, ImageLayout.YUV_420)),
    ('nv12', (np.dtype('uint8'), (102, 100), 2), (PixelType.YUV, 0, ImageLayout.NV12)),
    ('canon', (np.dtype('uint16'), (3482, 5218), 2), (PixelType.BAYER_RGGB, 14, ImageLayout.PLANAR)),
    ('panasonic', (np.dtype('uint16'), (2250, 3984), 2), (PixelType.BAYER_BGGR, 12, ImageLayout.PLANAR)),
    ('sony', (np.dtype('uint16'), (3672, 5496), 2), (PixelType.BAYER_RGGB, 14, ImageLayout.PLANAR)),
    ('nikon', (np.dtype('uint16'), (4044, 6080), 2), (PixelType.BAYER_RGGB, 14, ImageLayout.PLANAR)),
    ('kodak', (np.dtype('uint8'), (976, 848), 2), (PixelType.BAYER_GRBG, 8, ImageLayout.PLANAR)),
    ('kodak_slr', (np.dtype('uint16'), (3012, 4516), 2), (PixelType.BAYER_GRBG, 12, ImageLayout.PLANAR)),
    ('leica', (np.dtype('uint16'), (2399, 4247), 2), (PixelType.BAYER_BGGR, 12, ImageLayout.PLANAR)),
    ('olympus', (np.dtype('uint16'), (2800, 3720), 2), (PixelType.BAYER_RGGB, 12, ImageLayout.PLANAR)),
    ('pentax', (np.dtype('uint16'), (2868, 4309), 2), (PixelType.BAYER_BGGR, 12, ImageLayout.PLANAR)),
    ('samsung', (np.dtype('uint16'), (3696, 5536), 2), (PixelType.BAYER_GRBG, 12, ImageLayout.PLANAR)),
])
def test_read_image(image_type, ref_numpy_info, ref_image_info):
    image, metadata = read_image(test_images_dir / test_data[image_type]['file'])
    assert isinstance(image, np.ndarray)
    assert (image.dtype, image.shape, image.ndim) == ref_numpy_info
    assert (metadata.fileInfo.pixelType, metadata.fileInfo.pixelPrecision,
            metadata.fileInfo.imageLayout) == ref_image_info

    ref_hash = test_data[image_type]['hash']
    hash = __hash_image(image)
    assert ref_hash == hash


@pytest.mark.parametrize('image_type, pixel_type, image_layout, pixel_precision, file_format, only_pixel_cmp', [
    ('raw', PixelType.BAYER_GBRG, ImageLayout.PLANAR, 0, FileFormat.PLAIN, False),
    ('bmp', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
    ('jpg', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
    ('png', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
    ('png_16bit', PixelType.GRAYSCALE, ImageLayout.PLANAR, 16, None, True),
    ('tif', PixelType.RGB, ImageLayout.INTERLEAVED, 0, None, True),
    ('tif_16bit', PixelType.BAYER_RGGB, ImageLayout.PLANAR, 16, None, True),
    ('cfa', PixelType.BAYER_RGGB, ImageLayout.PLANAR, 0, None, True),
    ('rawmipi12', PixelType.BAYER_GBRG, ImageLayout.PLANAR, 12, None, False),
    ('rawmipi10', PixelType.BAYER_RGGB, ImageLayout.PLANAR, 10, None, False),
    ('dng', PixelType.BAYER_RGGB, ImageLayout.PLANAR, 12, None, True),
    ('yuv', PixelType.YUV, ImageLayout.YUV_420, 0, FileFormat.PLAIN, False),
    ('nv12', PixelType.YUV, ImageLayout.NV12, 0, FileFormat.PLAIN, False),
])
def test_write_image(image_type, pixel_type, image_layout, pixel_precision, file_format, only_pixel_cmp):
    metadata = ImageMetadata()
    metadata.fileInfo.pixelType, metadata.fileInfo.imageLayout = pixel_type, image_layout
    metadata.fileInfo.pixelPrecision, metadata.fileInfo.fileFormat = pixel_precision, file_format
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
            np.array([[1.7485008239746094, -0.9061940312385559, 0.15769319236278534],
                      [0.017115920782089233, 1.318513035774231, -0.3356289267539978],
                      [0.03677308186888695, -0.3459629416465759 - 0.3356289267539978, 1.309189796447754]]))

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
    ('jpg',
     ('2008:05:30 15:56:01\x00', 1 / 160, 135, 71 / 10, 100, 'Canon\x00', 'Canon EOS 40D\x00', 1, 'GIMP 2.4.5\x00')),
    ('dng', ('2008:12:14 15:54:54', 1 / 800, 20, 71 / 10, 100, 'Canon', 'Canon EOS 350D DIGITAL', 1, None)),
    ('tif', ('2008:05:30 15:56:01', 1 / 160, 135, 71 / 10, 100, 'Canon', 'Canon EOS 40D', 1, 'GIMP 2.4.5')),
    ('canon', ('2012:09:06 07:48:25', 1 / 80, 70, 56 / 10, 1600, 'Canon', 'EOS-1D X', 1, None)),
    ('sony', ('2013:12:13 10:15:46', 1 / 29, 103 / 10, 18 / 10, 640, 'Sony', 'DSC-RX100', 1, None)),
    ('nikon', ('2008:12:01 14:52:13', 1 / 50, 70, 56 / 10, 100, 'Nikon', 'D3X', 6, None)),
    ('panasonic', ('2009:01:01 15:45:11', 1 / 40, 128 / 10, 80 / 10, 100, 'Panasonic', 'DMC-LX3', 1, None)),
    ('kodak', ('1997:04:23 07:58:32', 1 / 384, 370 / 10, 84 / 10, 160, 'Kodak', 'DC120', 1, None)),
    ('kodak_slr', ('2004:09:23 11:51:48', 1 / 350, 350 / 10, 95 / 10, 160, 'Kodak', 'DCS Pro SLR/n', 6, None)),
    ('leica', ('2007:07:08 12:57:48', 1 / 50, 63 / 10, 28 / 10, 400, 'Leica', 'D-LUX 3', 8, None)),
    ('olympus', ('2008:12:19 12:29:40', 1 / 320, 500 / 10, 20 / 10, 200, 'Olympus', 'E-3', 1, None)),
    ('pentax', ('2010:11:12 21:28:26', 1 / 5, 262 / 10, 40 / 10, 200, 'Pentax', 'K-x', 1, None)),
    ('samsung', ('2015:05:19 20:34:19', 1 / 59, 220 / 10, 56 / 10, 800, 'Samsung', 'NX300M', 1, None)),
])
def test_read_exif(image_type, ref_exif):
    image_path = test_images_dir / test_data[image_type]['file']

    if image_type in [
            'canon', 'sony', 'nikon', 'panasonic', 'kodak', 'kodak_slr', 'leica', 'olympus', 'pentax', 'samsung'
    ]:
        _, metadata = read_image(image_path)
        exif = metadata.exifMetadata
    else:
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
    assert abs(parsed_exif.exposureTime.asDouble() - __exif.exposureTime.asDouble()) < __epsilon
    assert abs(parsed_exif.focalLength.asDouble() - __exif.focalLength.asDouble()) < __epsilon
    assert abs(parsed_exif.fNumber.asDouble() - __exif.fNumber.asDouble()) < __epsilon
    assert (parsed_exif.make, parsed_exif.model) == (__exif.make, __exif.model)
    assert (parsed_exif.isoSpeedRatings, parsed_exif.orientation,
            parsed_exif.software) == (__exif.isoSpeedRatings, __exif.orientation, __exif.software)
