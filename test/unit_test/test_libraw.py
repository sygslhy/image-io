from cxx_image_io import LibRawParameters, Metadata
from cxx_image_io import ImageMetadata, ImageLayout, PixelType, PixelRepresentation

import pytest

pytestmark = pytest.mark.unittest

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
    """
    Scenario: Creating LibRaw with invalid parameters should raise AssertionError

    Given an invalid libraw processor type
    When I attempt to create a LibRaw instance
    Then an AssertionError should be raised
    """
    with pytest.raises(AssertionError) as excinfo:
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
    # Given:
    params = LibRawParameters(raw_width=100, raw_height=200, width=50, height=100, top_margin=10, left_margin=5)

    metadata = Metadata(params)
    metadata.fileInfo.imageLayout = ImageLayout.PLANAR
    metadata.fileInfo.pixelType = PixelType.BAYER_GRBG
    metadata.fileInfo.pixelPrecision = 8
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.width = 848
    metadata.fileInfo.height = 976

    # When:
    result = repr(metadata)

    # Then:

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
