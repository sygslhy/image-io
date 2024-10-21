from cxx_image import ImageMetadata, PixelType, PixelRepresentation

import numpy as np


def __separate_bayer_channels(bayer, pixel_type, pixel_presentation):
    r1 = bayer[::2].reshape((-1))
    r2 = bayer[1::2].reshape((-1))

    channels = np.empty((4, bayer.size // 4), dtype=pixel_presentation)
    channels[0] = r1[::2]
    channels[1] = r1[1::2]
    channels[2] = r2[::2]
    channels[3] = r2[1::2]


def separate_image_channels(image: np.array, metadata: ImageMetadata) -> dict:
    """Seperate the image to different channels.

    Parameters
    ----------
    image : np.array
        image as numpy array
    metadata : ImageMetadata
        image metadata information including image width, height, pixel type and layout.

    Returns
    -------
    dict
        returned a dictionary which contains the different channels in the
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
        __separate_bayer_channels(image, )
    elif metadata.fileInfo.pixelType in (PixelType.RGB, PixelType.RGBA):
        pass
    elif metadata.fileInfo.pixelType in (PixelType.YUV):
        pass
    else:
        raise Exception('Unsupported pixel type!')
