from unittest.mock import MagicMock

import numpy as np
import pytest

from cxx_image_io import (ImageLayout, LibRawParameters, Matrix3, Metadata,
                          PixelRepresentation, PixelType)
from cxx_image_io.utils.io_cxx_libraw import (_bayer_pattern_to_pixel_type,
                                              _fill_calibration_data,
                                              _fill_exif_metadata,
                                              _fill_file_info,
                                              _parse_pixelType)

pytestmark = pytest.mark.unittest


# -----------------------------
# Test filters < 1000 → NotImplementedError
# -----------------------------
@pytest.mark.unittest
def test_parse_pixelType_filters_too_small():
    # Given: a libRaw object with filters < 1000
    libRaw = MagicMock()
    libRaw.imgdata.idata.filters = 999

    # When & Then: calling _parse_pixelType should raise NotImplementedError
    with pytest.raises(NotImplementedError):
        _parse_pixelType(libRaw)


# -----------------------------
# Test invalid 4x4 pattern → ValueError
# -----------------------------
@pytest.mark.unittest
def test_parse_pixelType_invalid_pattern(monkeypatch):
    # Given: a libRaw object with filters >= 1000
    libRaw = MagicMock()
    libRaw.imgdata.idata.filters = 1000

    # And: a 4x4 Bayer pattern with inconsistent sub-blocks
    pattern_4x4 = np.array(
        [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 1, 0],  # inconsistency here
            [1, 0, 0, 1]
        ],
        dtype=np.uint8)

    # Patch _raw_color to return values from the mock pattern
    # When: _parse_pixelType is called
    monkeypatch.setattr("cxx_image_io.utils.io_cxx_libraw._raw_color", lambda libRaw, y, x: pattern_4x4[y, x])

    # Then: it should raise ValueError due to inconsistent 4x4 sub-blocks
    with pytest.raises(ValueError):
        _parse_pixelType(libRaw)


# -----------------------------
# Test successful 2x2 CFA pattern extraction
# -----------------------------
@pytest.mark.unittest
def test_parse_pixelType_success(monkeypatch):
    # Given: a libRaw object with filters >= 1000
    libRaw = MagicMock()
    libRaw.imgdata.idata.filters = 1000

    # And: a consistent 4x4 Bayer pattern
    pattern_4x4 = np.array([[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]], dtype=np.uint8)

    # Patch _raw_color to return values from the consistent pattern
    # When: _parse_pixelType is called
    monkeypatch.setattr("cxx_image_io.utils.io_cxx_libraw._raw_color", lambda libRaw, y, x: pattern_4x4[y, x])

    top_left = _parse_pixelType(libRaw)

    # Then: it should return the correct 2x2 top-left CFA pattern
    expected = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    np.testing.assert_array_equal(top_left, expected)


# -----------------------------
# Convert a 2x2 RGGB Bayer matrix into PixelType.BAYER_RGGB
# -----------------------------
@pytest.mark.unittest
def test_bayer_pattern_to_pixel_type_rggb():
    # Given: A 2x2 Bayer pattern representing RGGB
    pattern = np.array([[0, 1], [3, 2]])

    # When: I call _bayer_pattern_to_pixel_type with this pattern
    result = _bayer_pattern_to_pixel_type(pattern)

    # --- Then: The function should return PixelType.BAYER_RGGB ----------------
    assert result == PixelType.BAYER_RGGB


# -----------------------------
# Convert a 2x2 BGGR Bayer matrix into PixelType.BAYER_BGGR
# -----------------------------
@pytest.mark.unittest
def test_bayer_pattern_to_pixel_type_bggr():
    # Given: the BGGR pattern[[2, 3],[1, 0]] representing BGGR
    pattern = np.array([[2, 3], [1, 0]])
    # When: I pass the pattern to _bayer_pattern_to_pixel_type
    result = _bayer_pattern_to_pixel_type(pattern)
    # Then: the returned value should be PixelType.BAYER_BGGR
    assert result == PixelType.BAYER_BGGR


# -----------------------------
# Passing an invalid 2x2 matrix to the Bayer pattern converter
# -----------------------------
@pytest.mark.unittest
def test_bayer_pattern_to_pixel_type_invalid():
    # --- Given: A pattern that does not match any known Bayer layout ----------
    pattern = np.array([[9, 9], [9, 9]])

    # --- When: I call _bayer_pattern_to_pixel_type with this pattern ----------
    # --- Then: The function should raise a ValueError -------------------------
    with pytest.raises(ValueError):
        _bayer_pattern_to_pixel_type(pattern)


# Fake libraw-like structure for test
class FakeSizes:
    raw_width = 4000
    raw_height = 3000


class FakeColor:
    raw_bps = 14  # 14-bit raw => UINT16


class FakeIdata:
    cdesc = 'RGGB'  # ensures Bayer path


class FakeRawData:
    sizes = FakeSizes()


class FakeImgData:
    rawdata = FakeRawData()
    color = FakeColor()
    idata = FakeIdata()


class FakeLibRaw:
    imgdata = FakeImgData()


def test_fill_file_info_bayer_pattern():
    # Given: A LibRaw-like object containing 14-bit RGGB raw image
    class FakeSizes:
        raw_width = 4000
        raw_height = 3000
        width = 4000
        height = 3000
        top_margin = 0
        left_margin = 0

    class FakeColor:
        raw_bps = 14  # 14-bit raw => UINT16

    class FakeIdata:
        cdesc = 'RGGB'  # ensures Bayer path
        filters = 2000  # need to > 1000

    class FakeRawData:
        sizes = FakeSizes()

    class FakeImgData:
        rawdata = FakeRawData()
        color = FakeColor()
        idata = FakeIdata()
        sizes = FakeSizes()

    class FakeLibRaw:
        imgdata = FakeImgData()

        def COLOR(self, y, x):
            # RGGB 2x2 pattern:
            pattern = [[0, 1], [3, 2]]
            return pattern[y % 2][x % 2]

    libRaw = FakeLibRaw()
    libraw_params = LibRawParameters(libRaw.imgdata.rawdata.sizes.raw_width, libRaw.imgdata.rawdata.sizes.raw_height,
                                     libRaw.imgdata.rawdata.sizes.width, libRaw.imgdata.rawdata.sizes.height,
                                     libRaw.imgdata.rawdata.sizes.top_margin, libRaw.imgdata.rawdata.sizes.left_margin)
    metadata = Metadata(libraw_params)

    # When: I call _fill_file_info with this libRaw instance
    result = _fill_file_info(libRaw, metadata)

    # Then: The metadata.fileInfo fields should be populated correctly
    assert result.fileInfo.width == 4000
    assert result.fileInfo.height == 3000
    assert result.fileInfo.pixelRepresentation == PixelRepresentation.UINT16
    assert result.fileInfo.pixelPrecision == 14
    assert result.fileInfo.imageLayout == ImageLayout.PLANAR
    assert result.fileInfo.pixelType == PixelType.BAYER_RGGB


def test_fill_file_info_custom_pixel_type():
    # Given: A LibRaw-like object containing 14-bit RGGB raw image
    class FakeSizes:
        raw_width = 4000
        raw_height = 3000
        width = 4000
        height = 3000
        top_margin = 0
        left_margin = 0

    class FakeColor:
        raw_bps = 12  # 12-bit raw

    class FakeIdata:
        cdesc = 'XXXX'  # Not a recognized Bayer cdesc
        filters = 2000  # need to > 1000

    class FakeRawData:
        sizes = FakeSizes()

    class FakeImgData:
        rawdata = FakeRawData()
        color = FakeColor()
        idata = FakeIdata()
        sizes = FakeSizes()

    class FakeLibRaw:
        imgdata = FakeImgData()

        def COLOR(self, y, x):
            # RGGB 2x2 pattern:
            pattern = [[0, 1], [3, 2]]
            return pattern[y % 2][x % 2]

    libRaw = FakeLibRaw()
    libraw_params = LibRawParameters(libRaw.imgdata.rawdata.sizes.raw_width, libRaw.imgdata.rawdata.sizes.raw_height,
                                     libRaw.imgdata.rawdata.sizes.width, libRaw.imgdata.rawdata.sizes.height,
                                     libRaw.imgdata.rawdata.sizes.top_margin, libRaw.imgdata.rawdata.sizes.left_margin)
    metadata = Metadata(libraw_params)

    # When: I call _fill_file_info with this object
    result = _fill_file_info(libRaw, metadata)

    # Then: pixelType should fall back to PixelType.CUSTOM
    assert result.fileInfo.pixelType == PixelType.CUSTOM


def test_fill_calibration_data():
    # Given: A LibRaw-like object with calibration values
    class FakeColor:
        black = 64
        maximum = 16383
        cam_mul = [2.0, 1.0, 1.5]  # R,G,B
        rgb_cam = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        dng_levels = type('dng', (), {'baseline_exposure': 1})()

    class FakeImgData:
        color = FakeColor()

    class FakeLibRaw:
        imgdata = FakeImgData()

    libRaw = FakeLibRaw()

    # And: Metadata requires LibRawParameters
    libraw_params = LibRawParameters(raw_width=4000,
                                     raw_height=3000,
                                     width=4000,
                                     height=3000,
                                     top_margin=0,
                                     left_margin=0)
    metadata = Metadata(libraw_params)

    # When: I call fill_calibration_data
    result = _fill_calibration_data(libRaw, metadata)

    # Then: calibrationData and cameraControls should be populated
    assert np.all(result.calibrationData.blackLevel == 64)
    assert result.calibrationData.whiteLevel == 16383
    assert result.cameraControls.whiteBalance.gainR == 2.0 / 1.0
    assert result.cameraControls.whiteBalance.gainB == 1.5 / 1.0
    assert result.shootingParams.ispGain == 2**1
    assert isinstance(result.calibrationData.colorMatrix, Matrix3)
    repr_str = repr(result.calibrationData.colorMatrix)
    assert repr_str == "[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]"


def test_fill_exif_metadata():
    # Given: A LibRaw-like object with EXIF info
    class FakeOther:
        iso_speed = 100
        shutter = 0.01  # 1/100 s
        aperture = 2.8
        focal_len = 35.0
        timestamp = '2025:11:28 12:00:00'
        desc = 'Test image'

    class FakeIdata:
        make = 'TestMake'
        model = 'TestModel'

    class FakeSizes:
        width = 4000
        height = 3000
        flip = None

    class FakeRawData:
        sizes = FakeSizes()

    class FakeImgData:
        rawdata = FakeRawData()
        other = FakeOther()
        idata = FakeIdata()

    class FakeLibRaw:
        imgdata = FakeImgData()

    libRaw = FakeLibRaw()

    # And: Metadata requires LibRawParameters
    libraw_params = LibRawParameters(raw_width=4000,
                                     raw_height=3000,
                                     width=4000,
                                     height=3000,
                                     top_margin=0,
                                     left_margin=0)
    metadata = Metadata(libraw_params)

    # When: I call fill_exif_metadata
    result = _fill_exif_metadata(libRaw, metadata)

    # Then: exifMetadata fields should be populated correctly
    assert result.exifMetadata.imageWidth == 4000
    assert result.exifMetadata.imageHeight == 3000
    assert result.exifMetadata.isoSpeedRatings == 100
    assert result.exifMetadata.exposureTime.numerator == 1
    assert result.exifMetadata.exposureTime.denominator == int(1 / 0.01)
    assert result.exifMetadata.fNumber.numerator == round(2.8 * 10)
    assert result.exifMetadata.fNumber.denominator == 10
    assert result.exifMetadata.focalLength.numerator == int(35.0 * 10)
    assert result.exifMetadata.focalLength.denominator == 10
    assert result.exifMetadata.make == 'TestMake'
    assert result.exifMetadata.model == 'TestModel'
    assert result.exifMetadata.dateTimeOriginal == '2025:11:28 12:00:00'
    assert result.exifMetadata.imageDescription == 'Test image'


def test_fill_exif_metadata_all_invalid_values():
    # Given: A LibRaw-like object where EXIF fields are None or 0
    class FakeOther:
        iso_speed = 0
        shutter = -1
        aperture = 0
        focal_len = 0
        timestamp = None
        desc = None

    class FakeIdata:
        make = None
        model = None

    class FakeSizes:
        width = 4000
        height = 3000
        flip = None

    class FakeRawData:
        sizes = FakeSizes()

    class FakeImgData:
        rawdata = FakeRawData()
        other = FakeOther()
        idata = FakeIdata()

    class FakeLibRaw:
        imgdata = FakeImgData()

    libRaw = FakeLibRaw()

    # And: Metadata requires LibRawParameters
    libraw_params = LibRawParameters(raw_width=4000,
                                     raw_height=3000,
                                     width=4000,
                                     height=3000,
                                     top_margin=0,
                                     left_margin=0)
    metadata = Metadata(libraw_params)

    # When: I call fill_exif_metadata
    result = _fill_exif_metadata(libRaw, metadata)

    # Then: exifMetadata fields should remain defaults / None, no exceptions
    assert result.exifMetadata.imageWidth == 4000
    assert result.exifMetadata.imageHeight == 3000

    # The conditional fields should not be set
    assert getattr(result.exifMetadata, 'orientation', None) is None
    assert getattr(result.exifMetadata, 'isoSpeedRatings', None) is None
    assert getattr(result.exifMetadata, 'exposureTime', None) is None
    assert getattr(result.exifMetadata, 'fNumber', None) is None
    assert getattr(result.exifMetadata, 'focalLength', None) is None
    assert result.exifMetadata.make is None
    assert result.exifMetadata.model is None
    assert result.exifMetadata.dateTimeOriginal is None
    assert result.exifMetadata.imageDescription is None


def test_fill_exif_metadata_some_none_elements():
    # Given: A LibRaw-like object with EXIF info
    class FakeOther:
        iso_speed = 100
        focal_len = 35.0
        timestamp = '2025:11:28 12:00:00'
        desc = 'Test image'
        shutter = None
        aperture = None
        # shutter and aperture are None

    class FakeIdata:
        make = 'TestMake'
        model = 'TestModel'

    class FakeSizes:
        width = 4000
        height = 3000
        flip = None

    class FakeRawData:
        sizes = FakeSizes()

    class FakeImgData:
        rawdata = FakeRawData()
        other = FakeOther()
        idata = FakeIdata()

    class FakeLibRaw:
        imgdata = FakeImgData()

    libRaw = FakeLibRaw()

    # And: Metadata requires LibRawParameters
    libraw_params = LibRawParameters(raw_width=4000,
                                     raw_height=3000,
                                     width=4000,
                                     height=3000,
                                     top_margin=0,
                                     left_margin=0)
    metadata = Metadata(libraw_params)

    # When: I call fill_exif_metadata
    result = _fill_exif_metadata(libRaw, metadata)

    # Then: exifMetadata fields should be populated correctly excpet Fnumber and exposureTime
    assert result.exifMetadata.imageWidth == 4000
    assert result.exifMetadata.imageHeight == 3000
    assert result.exifMetadata.isoSpeedRatings == 100
    assert result.exifMetadata.exposureTime is None
    assert result.exifMetadata.fNumber is None
    assert result.exifMetadata.focalLength.numerator == int(35.0 * 10)
    assert result.exifMetadata.focalLength.denominator == 10
    assert result.exifMetadata.make == 'TestMake'
    assert result.exifMetadata.model == 'TestModel'
    assert result.exifMetadata.dateTimeOriginal == '2025:11:28 12:00:00'
    assert result.exifMetadata.imageDescription == 'Test image'


@pytest.mark.parametrize(
    "raw_width, raw_height, width, height, top_margin, left_margin, expected_msg",
    [
        # --- 1. raw w h non positive int ---
        (0, 100, 50, 50, 0, 0, "raw_width must be a positive int"),
        (100, -1, 50, 50, 0, 0, "raw_height must be a positive int"),

        # --- 2. raw visible w h non positive int ---
        (100, 100, 0, 50, 0, 0, "width must be a positive int"),
        (100, 100, 50, -3, 0, 0, "height must be a positive int"),

        # --- 3. margin negative ---
        (100, 100, 50, 50, -1, 0, "top_margin must be a non-negative int"),
        (100, 100, 50, 50, 0, -10, "left_margin must be a non-negative int"),

        # --- 4. visible size > raw size ---
        (100, 100, 200, 50, 0, 0, "visible width must not exceed raw width"),
        (100, 100, 50, 150, 0, 0, "visible height must not exceed raw height"),

        # --- 5. margin + visible size > raw size ---
        (100, 100, 80, 80, 30, 0, "top_margin + height exceeds raw height"),  # 30+80=110 > 100
        (100, 100, 80, 80, 0, 25, "left_margin + width exceeds raw width"),  # 25+80=105 > 100
    ])
def test_libraw_parameters(raw_width, raw_height, width, height, top_margin, left_margin, expected_msg):
    # Given an invalid libraw processor type
    with pytest.raises(AssertionError) as excinfo:
        # When I attempt to create a LibRaw instance
        # Then an AssertionError should be raised
        LibRawParameters(raw_width, raw_height, width, height, top_margin, left_margin)
    assert expected_msg in str(excinfo.value)


def test_librawparameters():
    # Given: valid raw sensor parameters that satisfy all constraints
    #   - raw dimensions: 4000x3000
    #   - visible area:   2000x1500, fully inside the raw frame
    #   - margins:        top=100, left=50, not causing overflow
    params = LibRawParameters(raw_width=4000, raw_height=3000, width=2000, height=1500, top_margin=100, left_margin=50)

    # When: converting the object to string via __repr__
    result = repr(params)

    # Then: the representation should match the internal __dict__ state
    assert result == str({
        'rawWidth': 4000,
        'rawHeight': 3000,
        'rawWidthVisible': 2000,
        'rawHeightVisible': 1500,
        'topMargin': 100,
        'leftMargin': 50
    })


def test_metadata():
    # Given: A Metadata is instanciated with example fileInfo and LibRawParameters
    params = LibRawParameters(raw_width=100, raw_height=200, width=50, height=100, top_margin=10, left_margin=5)

    metadata = Metadata(params)
    metadata.fileInfo.imageLayout = ImageLayout.PLANAR
    metadata.fileInfo.pixelType = PixelType.BAYER_GRBG
    metadata.fileInfo.pixelPrecision = 8
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.width = 848
    metadata.fileInfo.height = 976

    # When: converting the object to string via __repr__
    result = repr(metadata)

    # Then: the string must be as a string of __dict__ state
    assert result == str({
        'fileInfo': {
            'width': 848,
            'height': 976,
            'pixelPrecision': 8,
            'imageLayout': 'planar',
            'pixelType': 'bayer_grbg',
            'pixelRepresentation': 'uint8'
        },
        'exifMetadata': {},
        'shootingParams': {},
        'cameraControls': {},
        'calibrationData': {},
        'semanticMasks': [],
        'LibRawParams': {
            'rawWidth': 100,
            'rawHeight': 200,
            'rawWidthVisible': 50,
            'rawHeightVisible': 100,
            'topMargin': 10,
            'leftMargin': 5
        }
    })
