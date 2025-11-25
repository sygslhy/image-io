import numpy as np
import pytest

from cxx_image_io import (ImageMetadata, PixelType, merge_image_channels,
                          read_image, split_image_channels)

from .data_cases import TEST_CASES, TEST_CHANNELS_CASES

pytestmark = pytest.mark.nrt


@pytest.mark.parametrize("case", TEST_CHANNELS_CASES)
def test_split_and_merge_channels(case):
    # Given: a numpy array representing an image and its metadata with pixel type and order
    array = case.array
    metadata = ImageMetadata()
    metadata.fileInfo = case.fileInfo
    order = case.order
    ref_values = case.ref_values

    if order:
        metadata.fileInfo.pixelType = order[0]

    # When: the image is split into channels using split_image_channels
    channels = split_image_channels(array, metadata)

    # Then: for Bayer images, each channel should have expected shape and values
    if metadata.fileInfo.pixelType in (PixelType.BAYER_RGGB, PixelType.BAYER_GRBG, PixelType.BAYER_GBRG,
                                       PixelType.BAYER_BGGR):
        w, h = metadata.fileInfo.width // 2, metadata.fileInfo.height // 2
        for c, v in zip(order[1:], ref_values):
            assert channels[c].shape == (h, w)
            assert np.all(channels[c] == v), 'in {0} bayer channels not all = {1}'.format(c, v)

        # When: channels are merged back
        res = merge_image_channels(channels, metadata)

        # Then: the merged array should be identical to the original
        assert np.array_equal(array, res), 'bayer numpy array is different after merge channels'

    # Then: for RGB/RGBA images, each channel should have expected shape and values
    elif metadata.fileInfo.pixelType in [PixelType.RGB, PixelType.RGBA]:
        w, h = metadata.fileInfo.width, metadata.fileInfo.height
        for c, v in zip(order[1:], ref_values):
            assert channels[c].shape == (h, w)
            assert np.all(channels[c] == v), 'in {0} color channels not all = {1}'.format(c, v)

        # When: channels are merged back
        res = merge_image_channels(channels, metadata)

        # Then: the merged array should be identical to the original
        assert np.array_equal(array, res), 'color numpy array is different after merge channels'

    # Then: for YUV images, each channel should have expected shape and values
    elif metadata.fileInfo.pixelType == PixelType.YUV:
        w, h = metadata.fileInfo.width, metadata.fileInfo.height
        sampled_w, sampled_h = w // 2, h // 2
        assert channels['y'].shape == (h, w)
        assert channels['u'].shape == (sampled_h, sampled_w)
        assert channels['v'].shape == (sampled_h, sampled_w)
        for c, v in zip(order[1:], ref_values):
            assert np.all(channels[c] == v), 'in {0} yuv channels not all = {1}'.format(c, v)

        # When: channels are merged back
        res = merge_image_channels(channels, metadata)

        # Then: the merged array should be identical to the original
        assert np.array_equal(array, res), 'yuv numpy array is different after merge channels'


SPLIT_TEST_CASES_INDEX = ['jpg', 'png', 'yuv', 'cfa', 'rawmipi12', 'rawmipi10', 'raw', 'nv12', 'dng', 'tif']


@pytest.mark.parametrize('case', [case for case in TEST_CASES if case.name in SPLIT_TEST_CASES_INDEX])
def test_split_and_merge_images(test_images_dir, case):
    image_path = test_images_dir / case.file
    image, metadata = read_image(image_path)
    channels = split_image_channels(image, metadata)
    image_post = merge_image_channels(channels, metadata)

    np.array_equal(image, image_post)
