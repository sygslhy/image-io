import numpy as np
import pytest

from cxx_image_io import (ImageLayout, ImageMetadata, PixelRepresentation,
                          PixelType, merge_image_channels,
                          split_image_channels)

pytestmark = pytest.mark.unittest

# ----------------------------------------------------------------------
# split_image_channels
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "pixel_type,pixel_repr,layout,dtype,shape, res_shape",
    [
        # --- RGB ----------------------------------------------------------------
        (PixelType.RGB, PixelRepresentation.UINT8, ImageLayout.INTERLEAVED, np.uint8, (2, 2, 3), (2, 2)),
        (PixelType.RGB, PixelRepresentation.UINT16, ImageLayout.INTERLEAVED, np.uint16, (2, 2, 3), (2, 2)),
        (PixelType.RGB, PixelRepresentation.FLOAT, ImageLayout.INTERLEAVED, np.float32, (2, 2, 3), (2, 2)),

        # --- RGBA ---------------------------------------------------------------
        (PixelType.RGBA, PixelRepresentation.UINT8, ImageLayout.INTERLEAVED, np.uint8, (2, 2, 4), (2, 2)),
        (PixelType.RGBA, PixelRepresentation.FLOAT, ImageLayout.INTERLEAVED, np.float32, (2, 2, 4), (2, 2)),

        # --- Bayer --------------------------------------------------------------
        (PixelType.BAYER_RGGB, PixelRepresentation.UINT8, ImageLayout.PLANAR, np.uint8, (4, 4), (2, 2)),
        (PixelType.BAYER_RGGB, PixelRepresentation.FLOAT, ImageLayout.PLANAR, np.float32, (4, 4), (2, 2))
    ])
def test_split_image_channels(pixel_type, pixel_repr, layout, dtype, shape, res_shape):
    # Given: a simple 2x2 (or minimal) image with specified pixel type and representation
    img = np.ones(shape, dtype=dtype)

    metadata = ImageMetadata()
    metadata.fileInfo.width = shape[1]
    metadata.fileInfo.height = shape[0]
    metadata.fileInfo.pixelType = pixel_type
    metadata.fileInfo.pixelRepresentation = pixel_repr
    metadata.fileInfo.imageLayout = layout

    # When: splitting channels
    channels = split_image_channels(img, metadata)

    # Then: channels should exist and have correct dtype
    assert isinstance(channels, dict)
    for ch_name, ch in channels.items():
        assert isinstance(ch, np.ndarray)
        assert ch.dtype == dtype
        assert ch.shape == res_shape


# ----------------------------------------------------------------------
# merge_image_channels
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "pixel_type,pixel_repr,layout,dtype,shape, res_shape",
    [
        # --- RGB INTERLEAVED: H x W x 3 ---
        (PixelType.RGB, PixelRepresentation.UINT8, ImageLayout.INTERLEAVED, np.uint8, (2, 2), (2, 2, 3)),
        (PixelType.RGB, PixelRepresentation.UINT16, ImageLayout.INTERLEAVED, np.uint16, (2, 2), (2, 2, 3)),
        (PixelType.RGB, PixelRepresentation.FLOAT, ImageLayout.INTERLEAVED, np.float32, (2, 2), (2, 2, 3)),

        # --- RGBA INTERLEAVED: H x W x 4 ---
        (PixelType.RGBA, PixelRepresentation.UINT8, ImageLayout.INTERLEAVED, np.uint8, (2, 2), (2, 2, 4)),
        (PixelType.RGBA, PixelRepresentation.FLOAT, ImageLayout.INTERLEAVED, np.float32, (2, 2), (2, 2, 4)),

        # --- Bayer PLANAR: H x W (single plane raw pattern) ---
        (PixelType.BAYER_RGGB, PixelRepresentation.UINT8, ImageLayout.PLANAR, np.uint8, (4, 4), (8, 8)),
        (PixelType.BAYER_RGGB, PixelRepresentation.FLOAT, ImageLayout.PLANAR, np.float32, (4, 4), (8, 8)),
    ])
def test_merge_image_channels(pixel_type, pixel_repr, layout, dtype, shape, res_shape):
    # Given: separate channels for a minimal 2x2 image
    width, height = shape
    if pixel_type in (PixelType.RGB, PixelType.RGBA):
        channels = {
            'r': np.ones((height, width), dtype=dtype),
            'g': np.ones((height, width), dtype=dtype),
            'b': np.ones((height, width), dtype=dtype),
        }
        if pixel_type == PixelType.RGBA:
            channels['a'] = np.ones((height, width), dtype=dtype)
    elif pixel_type == PixelType.BAYER_RGGB:  # Bayer
        channels = {
            'r': np.ones((height, width), dtype=dtype),
            'gr': np.ones((height, width), dtype=dtype),
            'gb': np.ones((height, width), dtype=dtype),
            'b': np.ones((height, width), dtype=dtype)
        }
        width, height = 2 * width, 2 * height

    metadata = ImageMetadata()
    metadata.fileInfo.width = width
    metadata.fileInfo.height = height
    metadata.fileInfo.pixelType = pixel_type
    metadata.fileInfo.pixelRepresentation = pixel_repr
    metadata.fileInfo.imageLayout = layout

    # When: merging channels back to image
    merged = merge_image_channels(channels, metadata)

    # Then: merged image should have correct dtype and shape
    assert isinstance(merged, np.ndarray)
    assert merged.dtype == dtype
    assert merged.shape == res_shape


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
    "pixel_type,image_layout,img_shape, err_msg",
    [
        (PixelType.RGBA, ImageLayout(18), (2, 2, 4), 'Unsupported color image layout'),  # RGBA with unsupported layout
        (PixelType.RGB, ImageLayout(17), (2, 2, 3), 'Unsupported color image layout'),  # RGB with unsupported layout
        (PixelType.CUSTOM, ImageLayout(1),
         (2, 2, 3), 'Unsupported color pixel type')  # unsupported Pixel with supported layout
    ])
def test_split_color_unsupported_layout(pixel_type, image_layout, img_shape, err_msg):
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
    # Then it raises Exception with specific message
    with pytest.raises(Exception, match=err_msg):
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
    img_shape = (2, 2, 4)
    img = np.zeros(img_shape, dtype=np.uint8)

    # When / Then: call merge_image_channels and expect exception ---
    with pytest.raises(Exception, match="Unsupported pixel type!"):
        split_image_channels(img, metadata)


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


@pytest.mark.parametrize("pixel_type, required_keys, err_msg",
                         [(PixelType.RGB, ['r', 'g', 'b'], 'Unsupported color image layout'),
                          (PixelType.RGBA, ['r', 'g', 'b', 'a'], 'Unsupported color image layout'),
                          (PixelType.CUSTOM, ['r', 'g', 'b'], 'Unsupported pixel type')])
def test_merge_color_channels_unsupported_layout(pixel_type, required_keys, err_msg):
    # Given: RGB image but metadata contains invalid imageLayout
    metadata = ImageMetadata()
    metadata.fileInfo.width = 2
    metadata.fileInfo.height = 2
    metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8
    metadata.fileInfo.pixelType = pixel_type
    metadata.fileInfo.imageLayout = ImageLayout(999)

    # And Given: valid RGB channels
    channels = {k: np.zeros((2, 2), dtype=np.uint8) for k in required_keys}

    # When / Then: calling merge_image_channels should raise unsupported exception
    with pytest.raises(Exception, match=err_msg):
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
