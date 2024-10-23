from cxx_image import ImageMetadata, ImageLayout, PixelType, PixelRepresentation

import numpy as np

__bayer_to_str = {
    PixelType.BAYER_RGGB: ('r', 'gr', 'gb', 'b'),
    PixelType.BAYER_BGGR: ('b', 'gb', 'gr', 'r'),
    PixelType.BAYER_GRBG: ('gr', 'r', 'b', 'gb'),
    PixelType.BAYER_GBRG: ('gb', 'b', 'r', 'gr')
}

def __separate_bayer_channels(bayer, pixel_type, pixel_presentation):

    r1 = bayer[::2].reshape((-1))
    r2 = bayer[1::2].reshape((-1))

    cfa = np.empty((4, bayer.size // 4), dtype=pixel_presentation)
    cfa[0] = r1[::2]
    cfa[1] = r1[1::2]
    cfa[2] = r2[::2]
    cfa[3] = r2[1::2]

    channels = {}
    for id, c in enumerate(__bayer_to_str[pixel_type]):
        channels[c] = cfa[id].reshape(bayer.shape[0] // 2, bayer.shape[1] // 2)
    return channels


def __separate_color_channels(image, metadata):
    channels = {}
    if metadata.fileInfo.pixelType == PixelType.RGBA:
        if metadata.fileInfo.imageLayout == ImageLayout.INTERLEAVED:
            channels['r'] = image[:, :, 0]
            channels['g'] = image[:, :, 1]
            channels['b'] = image[:, :, 2]
            channels['a'] = image[:, :, 3]
        elif metadata.fileInfo.imageLayout == ImageLayout.PLANAR:
            channels['r'] = image[0, :, :]
            channels['g'] = image[1, :, :]
            channels['b'] = image[2, :, :]
            channels['a'] = image[3, :, :]
        else:
            raise Exception('Unsupported color image layout')

    elif metadata.fileInfo.pixelType == PixelType.RGB:
        if metadata.fileInfo.imageLayout == ImageLayout.INTERLEAVED:
            channels['r'] = image[:, :, 0]
            channels['g'] = image[:, :, 1]
            channels['b'] = image[:, :, 2]
        elif metadata.fileInfo.imageLayout == ImageLayout.PLANAR:
            channels['r'] = image[0, :, :]
            channels['g'] = image[1, :, :]
            channels['b'] = image[2, :, :]
        else:
            raise Exception('Unsupported color image layout')

    return channels


def __separate_yuv_channels(image, metadata):

    channels = {}
    w = metadata.fileInfo.width
    h = metadata.fileInfo.height
    yuv = image.flatten()
    channels['y'] = yuv[:w * h].reshape(h, w)
    sampled_w = w // 2
    sampled_h = h // 2
    if metadata.fileInfo.imageLayout == ImageLayout.YUV_420:
        uv = yuv[w * h:w * (h + sampled_h)]
        channels['u'] = uv[:sampled_w * sampled_h].reshape(
            sampled_h, sampled_w)
        channels['v'] = uv[sampled_w * sampled_h:w * sampled_h].reshape(
            sampled_h, sampled_w)
    elif metadata.fileInfo.imageLayout == ImageLayout.NV12:
        uv = yuv[w * h:w * (h + h // 2)]
        channels['u'] = uv[::2].reshape(sampled_h, sampled_w)
        channels['v'] = uv[1::2].reshape(sampled_h, sampled_w)
    else:
        raise Exception('Unsupported yuv image layout!')

    return channels


def __merge_bayer_channels(channels, pixel_presentation, metadata):
    assert len(channels.keys()) == 4, 'bayer must have 4 channels: {0}'.format(
        channels.keys())
    assert all(
        k in channels.keys() for k in ['r', 'gr', 'gb', 'b']
    ), 'bayer channels must have r, gr, gb, b, current channels: {0}'.format(
        channels.keys())
    assert metadata.fileInfo.width and metadata.fileInfo.height, 'must have image width and height in fileInfo to merge channels'
    pixel_type = metadata.fileInfo.pixelType
    width, height = metadata.fileInfo.width, metadata.fileInfo.height

    bayer = np.empty((height, width), pixel_presentation)
    bayer[0::2, 0::2] = channels[__bayer_to_str[pixel_type][0]]  # top left
    bayer[0::2, 1::2] = channels[__bayer_to_str[pixel_type][1]]  # top right
    bayer[1::2, 0::2] = channels[__bayer_to_str[pixel_type][2]]  # bottom left
    bayer[1::2, 1::2] = channels[__bayer_to_str[pixel_type][3]]  # bottom right
    return bayer


def __merge_color_channels(channels, pixel_presentation, metadata):
    assert metadata.fileInfo.width and metadata.fileInfo.height, 'must have image width and height in fileInfo to merge channels'
    width, height = metadata.fileInfo.width, metadata.fileInfo.height
    if metadata.fileInfo.pixelType == PixelType.RGBA:
        assert len(
            channels.keys()) == 4, 'RGBA must have 4 channels: {0}'.format(
                channels.keys())
        assert all(
            k in channels.keys() for k in ['r', 'g', 'b', 'a']
        ), 'RGBA channels must have r, g, b, a, current channels: {0}'.format(
            channels.keys())
        if metadata.fileInfo.imageLayout == ImageLayout.INTERLEAVED:
            image = np.empty((height, width, 4), pixel_presentation)
            image[:, :, 0] = channels['r']
            image[:, :, 1] = channels['g']
            image[:,  :, 2] = channels['b']
            image[:, :, 3] = channels['a']
            return image
        elif metadata.fileInfo.imageLayout == ImageLayout.PLANAR:
            image = np.empty((4, height, width), pixel_presentation)
            image[0,  :, :] = channels['r']
            image[1,  :, :] = channels['g']
            image[2,  :, :] = channels['b']
            image[3,  :, :] = channels['a']
            return image
        else:
            raise Exception('Unsupported color image layout')
    elif metadata.fileInfo.pixelType == PixelType.RGB:
        assert len(
            channels.keys()) == 3, 'RGB must have 3 channels: {0}'.format(
                channels.keys())
        assert all(
            k in channels.keys() for k in ['r', 'g', 'b']
        ), 'RGB channels must have r, g, b, current channels: {0}'.format(
            channels.keys())
        if metadata.fileInfo.imageLayout == ImageLayout.INTERLEAVED:
            image = np.empty((height, width, 3), pixel_presentation)
            image[:, :, 0] = channels['r']
            image[:, :, 1] = channels['g']
            image[:, :, 2] = channels['b']
            return image
        elif metadata.fileInfo.imageLayout == ImageLayout.PLANAR:
            image = np.empty((3, height, width), pixel_presentation)
            image[0, :, :] = channels['r']
            image[1, :, :] = channels['g']
            image[2, :, :] = channels['b']
            return image
        else:
            raise Exception('Unsupported color image layout')
    else:
        raise Exception('Unsupported pixel type')


def __merge_yuv_channels(channels, pixel_presentation, metadata):
    assert len(channels.keys()) == 3, 'YUV must have 3 channels: {0}'.format(
        channels.keys())
    assert all(
        k in channels.keys() for k in ['y', 'u', 'v']
    ), 'YUV channels must have y, u, v, current channels: {0}'.format(
        channels.keys())

    assert metadata.fileInfo.width and metadata.fileInfo.height, 'must have image width and height in fileInfo to merge channels'
    w, h = metadata.fileInfo.width, metadata.fileInfo.height
    sampled_w = w // 2
    sampled_h = h // 2
    image = np.empty(((h + sampled_h) * w), dtype=pixel_presentation)
    if metadata.fileInfo.imageLayout == ImageLayout.YUV_420:
        image[:w * h] = channels['y'].reshape(-1)
        image[w * h:w * h +
              (sampled_w * sampled_h)] = channels['u'].reshape(-1)
        image[w * h + (sampled_w * sampled_h):] = channels['v'].reshape(-1)
        return image.reshape(h + sampled_h, w)
    elif metadata.fileInfo.imageLayout == ImageLayout.NV12:
        image[:w * h] = channels['y'].reshape(-1)
        uv = np.empty(sampled_w * sampled_h * 2, dtype=pixel_presentation)
        uv[::2] = channels['u'].reshape(-1)
        uv[1::2] = channels['v'].reshape(-1)
        image[w * h:] = uv
        return image.reshape(h + sampled_h, w)
    else:
        raise Exception('Unsupported yuv image layout!')


def split_image_channels(image: np.array, metadata: ImageMetadata) -> dict:
    """Split the image to different channels.

    Parameters
    ----------
    image : np.array
        image as numpy array
    metadata : ImageMetadata
        image metadata information including image width, height, pixel type and layout.

    Returns
    -------
    dict
        returned a dictionary which contains the different channels as keys.
        the value is the numpy array.
    """
    assert metadata, "metadata is necessary to split channels"

    # parse image width and height
    (width, height) = (None, None)
    if metadata.fileInfo.width and metadata.fileInfo.height:
        width, height = metadata.fileInfo.width, metadata.fileInfo.height
    elif metadata.exifMetadata.imageWidth and metadata.exifMetadata.imageHeight:
        width, height = metadata.exifMetadata.imageWidth, metadata.exifMetadata.imageHeight
    else:
        raise Exception('width and height are necessary to split channels')

    pixel_presentation = None
    if metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT8:
        pixel_presentation = np.uint8
    elif metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT16:
        pixel_presentation = np.uint16
    elif metadata.fileInfo.pixelRepresentation == PixelRepresentation.FLOAT:
        pixel_presentation = np.float
    else:
        raise Exception('Unsupported pixel presentation!')

    # parse pixel type:
    assert metadata.fileInfo.pixelType, "pixelType is necessary to split channels"
    if metadata.fileInfo.pixelType in (PixelType.BAYER_RGGB,
                                       PixelType.BAYER_BGGR,
                                       PixelType.BAYER_GRBG,
                                       PixelType.BAYER_GBRG):
        assert width % 2 == 0 and height % 2 == 0, "Bayer width and height must be power of 2"
        return __separate_bayer_channels(image, metadata.fileInfo.pixelType,
                                         pixel_presentation)
    elif metadata.fileInfo.pixelType in (PixelType.RGB, PixelType.RGBA):
        return __separate_color_channels(image, metadata)
    elif metadata.fileInfo.pixelType == PixelType.YUV:
        assert width % 2 == 0 and height % 2 == 0, "YUV width and height must be power of 2"
        return __separate_yuv_channels(image, metadata)
    else:
        raise Exception('Unsupported pixel type!')


def merge_image_channels(channels: dict, metadata: ImageMetadata) -> np.array:
    """Merge different channels to image numpy array as Imagelayout in ImageMetadata.

    Parameters
    ----------
    channels : dict
        dictionary which contains the different channels as keys.
        the value is the numpy array
    metadata : ImageMetadata
        image metadata information including image width, height, pixel type and layout.

    Returns
    -------
    dict
        numpy array.
    """
    assert metadata, "metadata is necessary to merge channels"

    # parse image width and height
    (width, height) = (None, None)
    if metadata.fileInfo.width and metadata.fileInfo.height:
        width, height = metadata.fileInfo.width, metadata.fileInfo.height
    elif metadata.exifMetadata.imageWidth and metadata.exifMetadata.imageHeight:
        width, height = metadata.exifMetadata.imageWidth, metadata.exifMetadata.imageHeight
    else:
        raise Exception('width and height are necessary to merge channels')

    pixel_presentation = None
    if metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT8:
        pixel_presentation = np.uint8
    elif metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT16:
        pixel_presentation = np.uint16
    elif metadata.fileInfo.pixelRepresentation == PixelRepresentation.FLOAT:
        pixel_presentation = np.float
    else:
        raise Exception('Unsupported pixel presentation: {0}'.format(
            metadata.fileInfo.pixelRepresentation))

    # parse pixel type:
    assert metadata.fileInfo.pixelType, "pixelType is necessary to merge channels"
    if metadata.fileInfo.pixelType in (PixelType.BAYER_RGGB,
                                       PixelType.BAYER_BGGR,
                                       PixelType.BAYER_GRBG,
                                       PixelType.BAYER_GBRG):
        assert width % 2 == 0 and height % 2 == 0, "bayer image's width and height must be power of 2"
        return __merge_bayer_channels(channels, pixel_presentation, metadata)
    elif metadata.fileInfo.pixelType in (PixelType.RGB, PixelType.RGBA):
        return __merge_color_channels(channels, pixel_presentation, metadata)
    elif metadata.fileInfo.pixelType == PixelType.YUV:
        return __merge_yuv_channels(channels, pixel_presentation, metadata)
    else:
        raise Exception('Unsupported pixel type!')
