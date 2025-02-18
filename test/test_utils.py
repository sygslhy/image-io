from pathlib import Path

import numpy as np
import pytest

from test import root_dir
from cxx_image_io import (ImageLayout, ImageMetadata, PixelRepresentation, PixelType)
from cxx_image_io import read_image, split_image_channels, merge_image_channels

bayer_array = np.array([[1, 2] * 10 + [3, 4] * 10] * 8, dtype=np.uint16).reshape(16, 20)
bayer_metadata = ImageMetadata()
bayer_metadata.fileInfo.width = 20
bayer_metadata.fileInfo.height = 16
bayer_metadata.fileInfo.pixelType = PixelType.BAYER_RGGB
bayer_metadata.fileInfo.imageLayout = ImageLayout.PLANAR
bayer_metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT16

rgb_array = np.array([
    [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]],
    [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]],
    [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]],
])

rgb_metadata = ImageMetadata()
rgb_metadata.fileInfo.width = 4
rgb_metadata.fileInfo.height = 3
rgb_metadata.fileInfo.pixelType = PixelType.RGB
rgb_metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED
rgb_metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

rgb_planar_array = np.array([[[1, 1, 1], [1, 1, 1]], [[2, 2, 2], [2, 2, 2]], [[3, 3, 3], [3, 3, 3]]])

rgb_planar_metadata = ImageMetadata()
rgb_planar_metadata.fileInfo.width = 3
rgb_planar_metadata.fileInfo.height = 2
rgb_planar_metadata.fileInfo.pixelType = PixelType.RGB
rgb_planar_metadata.fileInfo.imageLayout = ImageLayout.PLANAR
rgb_planar_metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

rgba_array = np.array([
    [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
    [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
    [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
])

rgba_metadata = ImageMetadata()
rgba_metadata.fileInfo.width = 4
rgba_metadata.fileInfo.height = 3
rgba_metadata.fileInfo.pixelType = PixelType.RGBA
rgba_metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED
rgba_metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

rgba_planar_array = np.array([[[1, 1, 1], [1, 1, 1]], [[2, 2, 2], [2, 2, 2]], [[3, 3, 3], [3, 3, 3]],
                              [[4, 4, 4], [4, 4, 4]]])

rgba_planar_metadata = ImageMetadata()
rgba_planar_metadata.fileInfo.width = 3
rgba_planar_metadata.fileInfo.height = 2
rgba_planar_metadata.fileInfo.pixelType = PixelType.RGBA
rgba_planar_metadata.fileInfo.imageLayout = ImageLayout.PLANAR
rgba_planar_metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

yuv_array = np.array([[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1],
                      [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3]])

yuv_metadata = ImageMetadata()
yuv_metadata.fileInfo.width = 6
yuv_metadata.fileInfo.height = 4
yuv_metadata.fileInfo.pixelType = PixelType.YUV
yuv_metadata.fileInfo.imageLayout = ImageLayout.YUV_420
yuv_metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

nv12_array = np.array([[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1],
                       [2, 3, 2, 3, 2, 3], [2, 3, 2, 3, 2, 3]])

nv12_metadata = ImageMetadata()
nv12_metadata.fileInfo.width = 6
nv12_metadata.fileInfo.height = 4
nv12_metadata.fileInfo.pixelType = PixelType.YUV
nv12_metadata.fileInfo.imageLayout = ImageLayout.NV12
nv12_metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8


@pytest.mark.parametrize('array, metadata, order, ref_values', [
    (bayer_array, bayer_metadata, (PixelType.BAYER_RGGB, 'r', 'gr', 'gb', 'b'), (1, 2, 3, 4)),
    (bayer_array, bayer_metadata, (PixelType.BAYER_GRBG, 'gr', 'r', 'b', 'gb'), (1, 2, 3, 4)),
    (bayer_array, bayer_metadata, (PixelType.BAYER_GBRG, 'gb', 'b', 'r', 'gr'), (1, 2, 3, 4)),
    (bayer_array, bayer_metadata, (PixelType.BAYER_BGGR, 'b', 'gb', 'gr', 'r'), (1, 2, 3, 4)),
    (rgb_array, rgb_metadata, (PixelType.RGB, 'r', 'g', 'b'), (1, 2, 3)),
    (rgb_planar_array, rgb_planar_metadata, (PixelType.RGB, 'r', 'g', 'b'), (1, 2, 3)),
    (rgba_array, rgba_metadata, (PixelType.RGBA, 'r', 'g', 'b', 'a'), (1, 2, 3, 4)),
    (rgba_planar_array, rgba_planar_metadata, (PixelType.RGBA, 'r', 'g', 'b', 'a'), (1, 2, 3, 4)),
    (yuv_array, yuv_metadata, (PixelType.YUV, 'y', 'u', 'v'), (
        1,
        2,
        3,
    )),
    (nv12_array, nv12_metadata, (PixelType.YUV, 'y', 'u', 'v'), (1, 2, 3)),
])
def test_split_and_merge_channels(array, metadata, order, ref_values):
    if order:
        metadata.fileInfo.pixelType = order[0]
    channels = split_image_channels(array, metadata)
    if metadata.fileInfo.pixelType in (PixelType.BAYER_RGGB, PixelType.BAYER_GRBG, PixelType.BAYER_GBRG,
                                       PixelType.BAYER_BGGR):
        w, h = metadata.fileInfo.width // 2, metadata.fileInfo.height // 2
        for c, v in zip(order[1:], ref_values):
            assert channels[c].shape == (h, w)
            assert np.all(channels[c] == v), 'in {0} bayer channels not all = {1}'.format(c, v)

        res = merge_image_channels(channels, metadata)
        assert np.array_equal(array, res), 'bayer numpy array is different after merge channels'

    elif metadata.fileInfo.pixelType in [PixelType.RGB, PixelType.RGBA]:
        w, h = metadata.fileInfo.width, metadata.fileInfo.height
        for c, v in zip(order[1:], ref_values):
            assert channels[c].shape == (h, w)
            assert np.all(channels[c] == v), 'in {0} color channels not all = {1}'.format(c, v)

        res = merge_image_channels(channels, metadata)
        assert np.array_equal(array, res), 'color numpy array is different after merge channels'

    elif metadata.fileInfo.pixelType == PixelType.YUV:
        w, h = metadata.fileInfo.width, metadata.fileInfo.height
        sampled_w, sampled_h = w // 2, h // 2
        assert channels['y'].shape == (h, w)
        assert channels['u'].shape == (sampled_h, sampled_w)
        assert channels['v'].shape == (sampled_h, sampled_w)
        for c, v in zip(order[1:], ref_values):
            assert np.all(channels[c] == v), 'in {0} yuv channels not all = {1}'.format(c, v)

        res = merge_image_channels(channels, metadata)
        assert np.array_equal(array, res), 'yuv numpy array is different after merge channels'


@pytest.mark.parametrize('image_path', [
    'rgb_8bit.jpg', 'rgb_8bit.png', 'raw_420.yuv', 'bayer_16bit.cfa', 'bayer_12bit.RAWMIPI12', 'bayer_10bit.RAWMIPI',
    'bayer_16bit.plain16', 'raw.nv12', 'bayer_12bit.dng', 'rgb_8bit.tif'
])
def test_split_and_merge_images(image_path):
    test_images_dir = Path(root_dir, 'images/')
    image, metadata = read_image(test_images_dir / image_path)
    channels = split_image_channels(image, metadata)
    image_post = merge_image_channels(channels, metadata)

    np.array_equal(image, image_post)
