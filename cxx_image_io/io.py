import logging
import sys
from pathlib import Path

import numpy as np
from cxx_image import (ExifMetadata, ImageDouble, ImageFloat, ImageInt,
                       ImageLayout, ImageMetadata, ImageUint8, ImageUint16,
                       Matrix3, PixelRepresentation, PixelType, io, parser)
from cxx_libraw import LibRaw, LibRaw_errors

__numpy_array_image_convert_vector = {
    np.dtype('uint16'): ImageUint16,
    np.dtype('uint8'): ImageUint8,
    np.dtype('float'): ImageFloat,
    np.dtype('double'): ImageDouble,
    np.dtype('int'): ImageInt
}


class UnSupportedFileException(Exception):
    """Custom Exception for the case libraw cannot open unsupported file type.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class LibRawParameters():
    def __init__(self, raw_width, raw_height, width, height, top_margin, left_margin):
        self.rawWidth = raw_width
        self.rawHeight = raw_height
        self.rawWidthVisible = width
        self.rawHeightVisible = height
        self.topMargin = top_margin
        self.leftMargin = left_margin

    def __repr__(self):
        return str(self.__dict__)


class Metadata(ImageMetadata):
    def __init__(self, LibRawParameters):
        super().__init__()
        self.libRawParameters = LibRawParameters

    def serialize(self):
        metadata_dict = super().serialize()
        metadata_dict['LibRawParams'] = self.libRawParameters.__dict__
        return metadata_dict

    def __repr__(self):
        all_dict = self.serialize()
        return str(all_dict)


def __raw_color(libRaw, y, x):
    top_margin = libRaw.imgdata.sizes.top_margin
    left_margin = libRaw.imgdata.sizes.left_margin
    return libRaw.COLOR(y - top_margin, x - left_margin)


def __bayer_pattern_to_pixel_type(pattern):
    patterns = {
        PixelType.BAYER_RGGB: np.array([[0, 1], [3, 2]]),
        PixelType.BAYER_BGGR: np.array([[2, 3], [1, 0]]),
        PixelType.BAYER_GBRG: np.array([[3, 2], [0, 1]]),
        PixelType.BAYER_GRBG: np.array([[1, 0], [2, 3]]),
    }
    for key, value in patterns.items():
        if np.array_equal(pattern, value):
            return key
    raise ValueError("Invalid Bayer pattern")


def libraw_flip_to_exif_orientation(flip):
    conv_dict = {0: 1, 3: 3, 5: 6, 6: 8}
    return conv_dict[flip]


def __parse_pixelType(libRaw):
    if libRaw.imgdata.idata.filters < 1000:
        if libRaw.imgdata.idata.filters == 0:
            # black and white
            n = 1
        elif libRaw.p.imgdata.idata.filters == 1:
            #  Leaf Catchlight with 16x16 bayer matrix
            n = 16
        elif libRaw.p.imgdata.idata.filters == 9:
            # Fuji X-Trans (6x6 matrix)
            n = 6
        else:
            raise NotImplementedError('filters: {}'.format(libRaw.imgdata.idata.filters))
    else:
        n = 4
    pattern = np.empty((n, n), dtype=np.uint8)
    for y in range(n):
        for x in range(n):
            pattern[y, x] = __raw_color(libRaw, y, x)
    if n == 4:
        if np.all(pattern[:2, :2] == pattern[:2, 2:]) and np.all(pattern[:2, :2] == pattern[2:, 2:]) and np.all(
                pattern[:2, :2] == pattern[2:, :2]):
            pattern = pattern[:2, :2]
    return pattern


def __convert_LibRawdata_to_ImageMetadata(libRaw):
    assert isinstance(libRaw, LibRaw), "libRaw must be LibRaw type."

    libRawParameters = LibRawParameters(libRaw.imgdata.rawdata.sizes.raw_width,
                                            libRaw.imgdata.rawdata.sizes.raw_height,
                                            libRaw.imgdata.rawdata.sizes.width, libRaw.imgdata.rawdata.sizes.height,
                                            libRaw.imgdata.rawdata.sizes.top_margin,
                                            libRaw.imgdata.rawdata.sizes.left_margin)
    metadata = Metadata(libRawParameters)

    metadata.fileInfo.width = libRaw.imgdata.rawdata.sizes.raw_width
    metadata.fileInfo.height = libRaw.imgdata.rawdata.sizes.raw_height
    if libRaw.imgdata.color.raw_bps > 8:
        metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT16
    else:
        metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelPrecision = libRaw.imgdata.color.raw_bps
    metadata.fileInfo.imageLayout = ImageLayout.PLANAR

    raw_pattern = __parse_pixelType(libRaw)
    if raw_pattern.shape == (2, 2) and libRaw.imgdata.idata.cdesc == 'RGBG':
        metadata.fileInfo.pixelType = __bayer_pattern_to_pixel_type(raw_pattern)
    else:
        metadata.fileInfo.pixelType = PixelType.CUSTOM

    metadata.calibrationData.blackLevel = libRaw.imgdata.color.black
    metadata.calibrationData.whiteLevel = libRaw.imgdata.color.maximum
    if libRaw.imgdata.color.cam_mul[1] > 0 and libRaw.imgdata.color.cam_mul[0] > 0 and libRaw.imgdata.color.cam_mul[
            2] > 0:
        metadata.cameraControls.whiteBalance = ImageMetadata.WhiteBalance()
        metadata.cameraControls.whiteBalance.gainR = libRaw.imgdata.color.cam_mul[0] / libRaw.imgdata.color.cam_mul[1]
        metadata.cameraControls.whiteBalance.gainB = libRaw.imgdata.color.cam_mul[2] / libRaw.imgdata.color.cam_mul[1]
    if libRaw.imgdata.color.dng_levels.baseline_exposure and libRaw.imgdata.color.dng_levels.baseline_exposure >= 0:
        metadata.shootingParams.ispGain = 2**libRaw.imgdata.color.dng_levels.baseline_exposure

    rgb_cam = np.array(libRaw.imgdata.color.rgb_cam[:, :3])
    if not np.all(rgb_cam == 0):
        metadata.calibrationData.colorMatrix = Matrix3(rgb_cam)

    metadata.exifMetadata.imageWidth = libRaw.imgdata.rawdata.sizes.width
    metadata.exifMetadata.imageHeight = libRaw.imgdata.rawdata.sizes.height
    if libRaw.imgdata.rawdata.sizes.flip is not None:
        metadata.exifMetadata.orientation = libraw_flip_to_exif_orientation(libRaw.imgdata.rawdata.sizes.flip)

    if libRaw.imgdata.other.iso_speed and libRaw.imgdata.other.iso_speed > 0:
        metadata.exifMetadata.isoSpeedRatings = int(libRaw.imgdata.other.iso_speed)
    if libRaw.imgdata.other.shutter:
        fshutter = round(libRaw.imgdata.other.shutter, 8)
        if fshutter > 0:
            metadata.exifMetadata.exposureTime = ExifMetadata.Rational(1, int(1 / fshutter))
    if libRaw.imgdata.other.aperture:
        metadata.exifMetadata.fNumber = ExifMetadata.Rational(round(libRaw.imgdata.other.aperture * 10), 10)
    if libRaw.imgdata.other.focal_len:
        metadata.exifMetadata.focalLength = ExifMetadata.Rational(int(libRaw.imgdata.other.focal_len * 10), 10)
    if libRaw.imgdata.idata.make:
        metadata.exifMetadata.make = libRaw.imgdata.idata.make
    if libRaw.imgdata.idata.model:
        metadata.exifMetadata.model = libRaw.imgdata.idata.model
    if libRaw.imgdata.other.timestamp:
        metadata.exifMetadata.dateTimeOriginal = libRaw.imgdata.other.timestamp
    if libRaw.imgdata.other.desc:
        metadata.exifMetadata.imageDescription = libRaw.imgdata.other.desc
    return metadata


# internal function to print image essentiel infos for debugging
def __print_image_metadata_info(metadata):
    if metadata and metadata.fileInfo:
        print('Image Type:', metadata.fileInfo.pixelType)
        print('Pixel Precision:', metadata.fileInfo.pixelPrecision)
        print('Image Layout:', metadata.fileInfo.imageLayout)
        print('Pixel Representation:', metadata.fileInfo.pixelRepresentation)


# fill the image critical information to metadata that could be used otherwhere.
def __fill_medatata(image, metadata):
    assert metadata is not None
    metadata.fileInfo.pixelType = image.pixelType()
    metadata.fileInfo.pixelPrecision = image.pixelPrecision()
    metadata.fileInfo.imageLayout = image.imageLayout()
    metadata.fileInfo.width = image.width()
    metadata.fileInfo.height = image.height()
    return metadata


def read_image_cxx(image_path: Path, metadata_path: Path = None) -> (np.array, ImageMetadata):
    """Read different types of image files and return a numpy array,
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    image_path : Path
        path to image file
    metadata_path : Path, optional
        path to sidecar file for raw file case, the API will find automatically .json next to raw file, by default None,

    Returns
    -------
    np.array
        returned image in numpy array format
        metadata

    """
    assert isinstance(image_path, Path), "Image path must be pathlib.Path type."
    assert image_path.exists(), "Image file {0} not found".format(str(image_path))
    if metadata_path:
        assert isinstance(metadata_path, Path), "Metadata path must be pathlib.Path type."
        assert metadata_path.exists(), "Metadata file {0} not found".format(str(metadata_path))
        metadata_path = str(metadata_path)

    try:
        metadata = parser.readMetadata(str(image_path), metadata_path)
        image_reader = io.makeReader(str(image_path), metadata)
        # Currently don't find a good way to supported completely the std::optional by binding C++ function.
        # So create explicitily an ImageMetadata object when metadata is None.
        metadata = ImageMetadata() if metadata is None else metadata
        metadata = image_reader.readMetadata(metadata)
        if image_reader.pixelRepresentation() == PixelRepresentation.UINT8:
            image = image_reader.read8u()
        elif image_reader.pixelRepresentation() == PixelRepresentation.UINT16:
            image = image_reader.read16u()
        elif image_reader.pixelRepresentation() == PixelRepresentation.FLOAT:
            image = image_reader.readf()
        else:
            raise Exception('Unsupported image type!')
        metadata.fileInfo.pixelRepresentation = image_reader.pixelRepresentation()
        metadata = __fill_medatata(image, metadata)
        return np.array(image, copy=False), metadata
    except Exception as e:
        logging.error('Exception occurred in reading image from file {0}: {1}'.format(image_path, e))
        __print_image_metadata_info(metadata)
        sys.exit("Exception caught in reading image, check the error log.")


def read_image_libraw(image_path: Path) -> (np.array, ImageMetadata):
    """Read different types of raw files and return a numpy array,
       Supported image types: all the support file type by libraw

    Parameters
    ----------
    image_path : Path
        path to image file

    Returns
    -------
    np.array
        returned image in numpy array format

    """
    iProcessor = LibRaw()
    ret_open = iProcessor.open_file(str(image_path))
    iProcessor.unpack()
    if ret_open == LibRaw_errors.LIBRAW_FILE_UNSUPPORTED:
        raise UnSupportedFileException('Unsupported libRaw file type.')
    raw_with_margin = np.array(iProcessor.imgdata.rawdata, copy=False)
    top_margin, left_margin = iProcessor.imgdata.rawdata.sizes.top_margin, iProcessor.imgdata.rawdata.sizes.left_margin
    # width, height = iProcessor.imgdata.rawdata.sizes.width, iProcessor.imgdata.rawdata.sizes.height
    width, height = iProcessor.imgdata.rawdata.sizes.raw_width, iProcessor.imgdata.rawdata.sizes.raw_height
    raw_image = raw_with_margin[top_margin:top_margin + height, left_margin:left_margin + width]

    metadata = __convert_LibRawdata_to_ImageMetadata(iProcessor)
    return raw_with_margin, metadata


def read_image(image_path: Path, metadata_path: Path = None) -> (np.array, ImageMetadata):
    """Generic API to read different types of image files and return a numpy array,

    Parameters
    ----------
    image_path : Path
        path to image file
    metadata_path : Path, optional
        path to sidecar file for raw file case, the API will find automatically .json next to raw file, by default None,

    Returns
    -------
    np.array
        returned image in numpy array format
        metadata
    """
    if image_path.suffix.lower() in [
            '.yuv', '.nv12', '.bmp', '.jpg', '.jpeg', '.png', '.cfa', '.dng', '.tif', '.tiff'
    ]:
        image, metadata = read_image_cxx(image_path, metadata_path)
        return image, metadata

    try:
        image, metadata = read_image_libraw(image_path)
    except UnSupportedFileException as e:
        logging.warning('Unsupport file type for libraw, try with cxx_image to read image: {}'.format(e))
        # try with read_image_cxx to see if it can open this image file.
        image, metadata = read_image_cxx(image_path, metadata_path)
    return image, metadata


def read_exif(image_path: Path) -> ExifMetadata:
    """Read the exif data from image

    Parameters
    ----------
    image_path : Path
        path to image file

    Returns
    -------
    ExifMetadata
        returned exif data
    """
    assert isinstance(image_path, Path), "Image path must be pathlib.Path type."
    assert image_path.exists(), "Image file {0} not found".format(str(image_path))
    try:
        # By binding parser.readMetadata C++ code, we need to privode explicitely None as metadata path
        # In the case of tif, jpg or dng, we don't need sidecar.
        metadata = parser.readMetadata(str(image_path), None)
        image_reader = io.makeReader(str(image_path), metadata)
        return image_reader.readExif()
    except Exception as e:
        logging.error('Exception occurred in reading exif from file {0}: {1}'.format(image_path, e))
        __print_image_metadata_info(metadata)
        sys.exit("Exception caught in reading exif, check the error log.")


def write_image(output_path: Path, image_array: np.array, write_options: io.ImageWriter.Options):
    """Write a numpy array to different types of image file
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    output_path : Path
        path to image file
    image_array : np.array
        numpy array image to write
    write_options : io.ImageWriter.Options
        write options for writing parameters like, image buffer info, jpegQualiy, tiff compression type
        and exif metadata infos. by default None
    """
    assert isinstance(output_path, Path), "Image path must be pathlib.Path type."
    assert isinstance(image_array, np.ndarray), "image must be numpy array."
    try:
        # Currently don't find a good way to supported completely the std::optional by binding C++ function.
        # So create explicitily an ImageWriter.Options object when write_options is None.
        options = io.ImageWriter.Options() if write_options is None else write_options

        # Before writing the numpy array to image file, it is necessary to convert numpy array to C++ image object.
        # However, only numpy array need to know image types-map from np.dtype to Image<T>,
        # so we need firstly __numpy_array_image_convert_vector here
        # In addition, numpy array can't provide enough information to create C++ image object from itself.
        # We still need to get the information from metadata.fileInfo in write_options.
        image = __numpy_array_image_convert_vector[image_array.dtype](image_array, options.metadata.fileInfo.pixelType,
                                                                      options.metadata.fileInfo.imageLayout,
                                                                      options.metadata.fileInfo.pixelPrecision)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image_writer = io.makeWriter(str(output_path), options)
        image_writer.write(image)
    except Exception as e:
        logging.error('Exception occurred in writing image to file {0}: {1}'.format(output_path, e))
        __print_image_metadata_info(options.metadata)
        sys.exit("Exception caught in writing image, check the error log.")


def write_exif(image_path: Path, exif: ExifMetadata = None):
    """Write the exif data from image

    Parameters
    ----------
    image_path : Path
        path to image file
    exif : ExifMetadata
        exif data to write
    """
    assert isinstance(image_path, Path), "Image path must be pathlib.Path type."
    try:
        image_writer = io.makeWriter(str(image_path), io.ImageWriter.Options())
        image_writer.writeExif(exif)
    except Exception as e:
        logging.error('Exception occurred in writing exif to file {0}: {1}'.format(image_path, e))
        sys.exit("Exception caught in writing exif, check the error log.")
