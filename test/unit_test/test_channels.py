import numpy as np
import pytest

from cxx_image_io import (ImageLayout, ImageMetadata, PixelRepresentation,
                          PixelType, merge_image_channels,
                          split_image_channels)

pytestmark = pytest.mark.unittest

# ----------------------------------------------------------------------
# split_image_channels - KO cases
# ----------------------------------------------------------------------


def test_split_no_metadata():
    # Given: a valid numpy image but no metadata
    image = np.zeros((2, 2), dtype=np.uint8)

    # When / Then: calling split should fail because metadata is None
    with pytest.raises(AssertionError):
        split_image_channels(image, None)


def test_split_image_not_numpy():
    # Given: invalid image input (not a numpy array)
    # When / Then: split must raise an error
    with pytest.raises(AssertionError):
        split_image_channels("not array", ImageMetadata())


def test_split_no_width_height():
    # Given: metadata with no width/height information
    metadata = ImageMetadata()
    img = np.zeros((2, 2), dtype=np.uint8)

    # When / Then: split must fail because dimensions are missing
    with pytest.raises(Exception, match="width and height"):
        split_image_channels(img, metadata)


def test_split_unsupported_pixel_representation():
    # Given: invalid pixelRepresentation value inside metadata
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelType = PixelType.RGB
    metadata.fileInfo.pixelRepresentation = PixelRepresentation(999)  # unsupported type

    img = np.zeros((2, 2, 3))

    # When / Then: split must reject unsupported pixelRepresentation
    with pytest.raises(Exception, match="Unsupported pixel presentation"):
        split_image_channels(img, metadata)


def test_split_no_pixel_type():
    # Given: metadata with width/height but missing pixelType
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

    img = np.zeros((2, 2), dtype=np.uint8)

    # When / Then: split must enforce pixelType presence
    with pytest.raises(AssertionError, match="pixelType is necessary"):
        split_image_channels(img, metadata)


def test_split_bayer_width_not_even():
    # Given: Bayer image but width is odd (invalid)
    metadata = ImageMetadata()
    metadata.fileInfo.width = 3
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType.BAYER_RGGB

    img = np.zeros((2, 3), dtype=np.uint8)

    # When / Then: split must fail because Bayer requires even dimensions
    with pytest.raises(AssertionError, match="Bayer width and height must be power of 2"):
        split_image_channels(img, metadata)


@pytest.mark.parametrize(
    "pixel_type,image_layout,img_shape",
    [
        (PixelType.RGBA, ImageLayout(18), (2, 2, 4)),  # RGBA with unsupported layout
        (PixelType.RGB, ImageLayout(17), (2, 2, 3)),  # RGB with unsupported layout
    ])
def test_split_color_unsupported_layout(pixel_type, image_layout, img_shape):
    # Given a metadata object with RGB or RGBA pixel type
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = pixel_type

    # And Given an unsupported imageLayout in metadata
    metadata.fileInfo.imageLayout = image_layout

    # And Given: dummy image
    img = np.zeros(img_shape, dtype=np.uint8)

    # When split_image_channels() is called
    # Then it raises Exception('Unsupported color image layout')
    with pytest.raises(Exception, match="Unsupported color image layout"):
        split_image_channels(img, metadata)


def test_split_image_channels_unsupported_pixel_type():
    # Given: metadata with unsupported pixelType
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType(19)
    metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED

    # And Given: valid RGB channels
    channels = {
        'r': np.zeros((4, 4), dtype=np.uint8),
        'g': np.zeros((4, 4), dtype=np.uint8),
        'b': np.zeros((4, 4), dtype=np.uint8)
    }

    # When / Then: call merge_image_channels and expect exception ---
    with pytest.raises(Exception, match="Unsupported pixel type!"):
        merge_image_channels(channels, metadata)


def test_split_yuv_wrong_layout():
    # Given: YUV image but metadata contains an unsupported YUV layout
    metadata = ImageMetadata()
    metadata.fileInfo.width = 4
    metadata.fileInfo.height = 4
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType.YUV
    metadata.fileInfo.imageLayout = ImageLayout(5)  # Unsupport layout

    img = np.zeros((6, 4), dtype=np.uint8)

    # When / Then: split must fail because YUV layout is unsupported
    with pytest.raises(Exception, match="Unsupported yuv image layout"):
        split_image_channels(img, metadata)


def test_split_yuv_height_not_even():
    # Given: YUV 420 image with odd height (invalid)
    metadata = ImageMetadata()
    metadata.fileInfo.width = 4
    metadata.fileInfo.height = 3  # odd
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType.YUV
    metadata.fileInfo.imageLayout = ImageLayout.YUV_420

    img = np.zeros((5, 4), dtype=np.uint8)

    # When / Then: split must reject YUV 420 with odd height
    with pytest.raises(AssertionError, match="YUV width and height must be power of 2"):
        split_image_channels(img, metadata)


# ----------------------------------------------------------------------
# merge_image_channels - KO cases
# ----------------------------------------------------------------------


def test_merge_no_metadata():
    # Given: merging channels but metadata is None
    # When / Then: merge must fail
    with pytest.raises(AssertionError):
        merge_image_channels({}, None)


def test_merge_no_width_height():
    # Given: metadata without width/height
    metadata = ImageMetadata()
    metadata.fileInfo.pixelType = PixelType.RGB
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

    # When / Then: merge must reject missing dimensions
    with pytest.raises(Exception, match="width and height"):
        merge_image_channels({}, metadata)


def test_merge_unsupported_pixel_representation():
    # Given: invalid pixelRepresentation
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelType = PixelType.RGB
    metadata.fileInfo.pixelRepresentation = PixelRepresentation(9)  # Unsupport pixel Representation

    # When / Then: merge must fail for unsupported representation
    with pytest.raises(Exception, match="Unsupported pixel presentation"):
        merge_image_channels({}, metadata)


def test_merge_no_pixel_type():
    # Given: missing pixelType in metadata
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

    # When / Then: merge must enforce pixelType presence
    with pytest.raises(AssertionError, match="pixelType is necessary"):
        merge_image_channels({}, metadata)


def test_merge_bayer_invalid_size():
    # Given: Bayer image with odd width (invalid)
    metadata = ImageMetadata()
    metadata.fileInfo.width = 3
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType.BAYER_RGGB

    # When / Then: merge must reject incorrect Bayer dimensions
    with pytest.raises(AssertionError, match="bayer image's width and height must be power of 2"):
        merge_image_channels({}, metadata)


def test_merge_rgb_missing_channels():
    # Given: RGB image but channels dict is missing 'b'
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType.RGB
    metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED

    channels = {"r": np.zeros((2, 2)), "g": np.zeros((2, 2))}

    # When / Then: merge must require r/g/b channels
    with pytest.raises(AssertionError, match="RGB must have 3 channels"):
        merge_image_channels(channels, metadata)


@pytest.mark.parametrize("pixel_type, required_keys", [
    (PixelType.RGB, ['r', 'g', 'b']),
    (PixelType.RGBA, ['r', 'g', 'b', 'a']),
])
def test_merge_color_channels_unsupported_layout(pixel_type, required_keys):
    # Given: RGB image but metadata contains invalid imageLayout
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = pixel_type
    metadata.fileInfo.imageLayout = ImageLayout(999)

    # And Given: valid RGB channels
    channels = {k: np.zeros((2, 2), dtype=np.uint8) for k in required_keys}

    # When / Then: calling merge_image_channels should raise unsupported layout exception
    with pytest.raises(Exception, match="Unsupported color image layout"):
        merge_image_channels(channels, metadata)


def test_merge_yuv_missing_channels():
    # Given: YUV 420 image missing 'v' channel
    metadata = ImageMetadata()
    metadata.fileInfo.width = 4
    metadata.fileInfo.height = 4
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType.YUV
    metadata.fileInfo.imageLayout = ImageLayout.YUV_420

    channels = {"y": np.zeros((4, 4)), "u": np.zeros((2, 2))}

    # When / Then: merge must enforce presence of all YUV channels
    with pytest.raises(AssertionError, match="YUV must have 3 channels"):
        merge_image_channels(channels, metadata)


def test_merge_yuv_unsupported_layout():
    # Given: YUV image but metadata contains unsupported layout
    metadata = ImageMetadata()
    metadata.fileInfo.width = 4
    metadata.fileInfo.height = 4
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType.YUV
    metadata.fileInfo.imageLayout = ImageLayout(999)  # unsupported layout

    channels = {
        "y": np.zeros((4, 4)),
        "u": np.zeros((2, 2)),
        "v": np.zeros((2, 2)),
    }

    # When / Then: merge must fail due to unsupported YUV layout
    with pytest.raises(Exception, match="Unsupported yuv image layout"):
        merge_image_channels(channels, metadata)


def test_merge_image_channels_unsupported_pixel_type():
    # Given: metadata with unsupported pixelType
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = PixelType(19)
    metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED

    # And Given: valid RGB channels
    channels = {
        'r': np.zeros((4, 4), dtype=np.uint8),
        'g': np.zeros((4, 4), dtype=np.uint8),
        'b': np.zeros((4, 4), dtype=np.uint8)
    }

    # When / Then: call merge_image_channels and expect exception ---
    with pytest.raises(Exception, match="Unsupported pixel type!"):
        merge_image_channels(channels, metadata)
