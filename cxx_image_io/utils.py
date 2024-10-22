from cxx_image import ImageMetadata, ImageLayout, PixelType, PixelRepresentation

import numpy as np

__bayer_to_str = {
    PixelType.BAYER_RGGB: ('r', 'gr', 'gb', 'b'),
    PixelType.BAYER_BGGR: ('b', 'gb', 'gr', 'r'),
    PixelType.BAYER_GRBG: ('gr', 'r', 'b', 'gb'),
    PixelType.BAYER_GBRG: ('gb', 'b', 'r', 'gr')
}

__color_to_str = {PixelType.RGB: 'rgb', PixelType.RGBA: 'rgba'}


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
        channels[c] = cfa[id].reshape(bayer.shape[1] // 2, bayer.shape[0] // 2)
    return channels


def __separate_color_channels(image, metadata):
    channels = {}
    if metadata.fileInfo.pixelType == PixelType.RGBA:
        if metdata.fileInfo.imageLayout == ImageLayout.INTERLEAVED:
            channels['r'] = image[:, :, :, 0]
            channels['g'] = image[:, :, :, 1]
            channels['b'] = image[:, :, :, 2]
            channels['a'] = image[:, :, :, 3]
        elif metadata.fileInfo.imageLayout == ImageLayout.PLANAR:
            channels['r'] = image[0, :, :, :]
            channels['g'] = image[1, :, :, :]
            channels['b'] = image[2, :, :, :]
            channels['a'] = image[3, :, :, :]
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
        uv = yuv[w * h:w * (h + h // 2)]
        channels['u'] = uv[:w * (h // 4)].reshape(
            sampled_h, sampled_w)
        channels['v'] = uv[w * (h // 4):w * sampled_h].reshape(
            sampled_h, sampled_w)
    elif metadata.fileInfo.imageLayout == ImageLayout.NV12:
        uv = yuv[w * h:w * (h + h // 2)]
        channels['u'] = uv[::2].reshape(sampled_h, sampled_w)
        channels['v'] = uv[1::2].reshape(sampled_h, sampled_w)
    else:
        raise Exception('Unsupported yuv image layout!')

    return channels


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
    assert metadata, "metadata is necessary to seperate channels"

    # parse image width and height
    (width, height) = (None, None)
    if metadata.fileInfo.width and metadata.fileInfo.height:
        width, height = metadata.fileInfo.width, metadata.fileInfo.height
    elif metadata.exifMetadata.imageWidth and metadata.exifMetadata.imageHeight:
        width, height = metadata.exifMetadata.imageWidth, metadata.exifMetadata.imageHeight
    else:
        raise Exception('width and height are necessary to seperate channels')

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
    assert metadata.fileInfo.pixelType, "pixelType is necessary to seperate channels"
    if metadata.fileInfo.pixelType in (PixelType.BAYER_RGGB,
                                       PixelType.BAYER_BGGR,
                                       PixelType.BAYER_GRBG,
                                       PixelType.BAYER_GBRG):
        assert width % 2 == 0 and height % 2 == 0, "width and height must be power of 2"
        return __separate_bayer_channels(image, metadata.fileInfo.pixelType,
                                         pixel_presentation)
    elif metadata.fileInfo.pixelType in (PixelType.RGB, PixelType.RGBA):
        return __separate_color_channels(image, metadata)
    elif metadata.fileInfo.pixelType == PixelType.YUV:
        return __separate_yuv_channels(image, metadata)
    else:
        raise Exception('Unsupported pixel type!')
