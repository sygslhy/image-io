# CXX Image IO

CXX Image IO is a Python project which provides the image IO interfaces, binding with the C++ library: https://github.com/emmcb/cxx-image,
These IO interfaces are designed to read and write images in many file formats in generic way and to interact nicely with numpy array.

| Image format  | Read | Write | EXIF | Pixel precision        | Pixel type           | File extension                   |
|---------------|------|-------|------|------------------------|----------------------|----------------------------------|
| BMP           | x    | x     |      | 8 bits                 | Grayscale, RGB, RGBA | .bmp                             |
| CFA           | x    | x     |      | 16 bits                | Bayer                | .cfa                             |
| DNG           | x    |       | x    | 16 bits, float         | Bayer, RGB           | .dng                             |
| JPEG          | x    | x     | x    | 8 bits                 | Grayscale, RGB       | .jpg, .jpeg                      |
| MIPIRAW       | x    | x     |      | 10 bits, 12 bits       | Bayer                | .RAWMIPI, .RAWMIPI10, .RAWMIPI12 |
| PLAIN         | x    | x     |      | *                      | Bayer                | .plain16,  *                     |
| PNG           | x    | x     |      | 8 bits, 16 bits        | Grayscale, RGB, RGBA | .png                             |
| TIFF          | x    | x     | x    | 8 bits, 16 bits, float | Bayer, RGB           | .tif, .tiff                      |

# Getting Started

## Prerequisites

This projet currently supports only Python 3.11 and 3.12 on Windows system. we are working for supporting Python on Linux nextly.

The user need to install python 3.11 or 3.12,

Then install the `numpy>=1.26` by `pip`

```sh
pip install numpy==1.26
```

## Installation

The python package `cxx_image_io` is to be installed by `pip`

```sh
pip install cxx_image_io
```

# Usage example

## Image reading

`read_image` is able to read a image file and return a numpy array and ImageMetadata object.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import read_image
from cxx_image_io import ImageMetadata
import numpy as np

image, metadata = read_image('/path/to/image.jpg')
assert isinstance(image, np.ndarray)

print('Type:', image.dtype)
print('Shape:', image.shape)
~~~~~~~~~~~~~~~

image is a numpy array which is suitable for the image processing afterwards.

The result could be like this:
~~~~~~~~~~~~~~~{.sh}
Type: uint8
Shape: (551, 603, 3)
~~~~~~~~~~~~~~~

ImageMetadata is the information about the image, including the pixel type, pixel precision and image layout, which define fundamentally how the pixels arranged in buffer.

~~~~~~~~~~~~~~~{.python}
print('Type:', metadata.fileInfo.pixelType)
print('Precision:', metadata.fileInfo.pixelPrecision)
print('Layout:', metadata.fileInfo.imageLayout)
~~~~~~~~~~~~~~~

The result could be like this:
~~~~~~~~~~~~~~~{.sh}
Type: PixelType.RGB
Precision: 8
Layout: ImageLayout.INTERLEAVED
~~~~~~~~~~~~~~~

Some file formats need to know in advance some informations about the image.
For example, the PLAIN format is just a simple dump of a buffer into a file, thus it needs to know how to interpret the data.

~~~~~~~~~~~~~~~{.python}
image, metadata = read_image('/path/to/image.plain16')
~~~~~~~~~~~~~~~

In this case, user need to have an image sidecar JSON located next to the image file as the same name and path `'/path/to/image.json'`

~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "format": "plain",
        "height": 3072,
        "width": 4080
        "pixelPrecision": 16,
        "pixelType": "bayer_gbrg",
    }
}
~~~~~~~~~~~~~~~

After image reading, the information in JSON sidecar is parsed in ImageMetadata object.

The result could be like this:
~~~~~~~~~~~~~~~{.sh}
Type: PixelType.BAYER_GBRG
Precision: 16
Layout: ImageLayout.PLANAR
~~~~~~~~~~~~~~~

Image sidecar is not mandatory, for the other formats which have already image information in their header, like jpg, png, tif, cfa. we don't need to provide image metadata.


## Image writing

`write_image` is able to write a numpy array to image file.

To write the pure numpy array to different image file extensions.
User need to define the following fundamental parameters in ImageMetadata which is part of ImageWriter.Options.
In order to call the specific C++ image libraries with them.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import ImageMetadata, ImageWriter, FileFormat, PixelType, ImageLayout
from cxx_image_io import write_image
import numpy as np

metadata = ImageMetadata()
metadata.fileInfo.pixelType = PixelType.RGB
metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image('/path/to/image.jpg', image, write_options)
~~~~~~~~~~~~~~~

`write_image` can determine the image format by file extensions, but some formats don't not rely on a specific extension, for example the PLAIN format that allows to directly dump the image buffer to a file. In this case, the format can be specified through ImageWriter.Options.

~~~~~~~~~~~~~~~{.python}
write_options = ImageWriter.Options(metadata)
write_options.fileFormat = FileFormat.PLAIN

assert isinstance(image, np.ndarray)
write_image('/path/to/image.plain16', image, write_options)
~~~~~~~~~~~~~~~



## EXIF

Some image formats, like JPEG and TIFF, support EXIF reading and writing.

If supported, EXIF can be read by calling `read_exif` and be written by calling `write_exif`.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import read_exif, write_exif
exif = read_exif('/path/to/image.jpg')

print('model:', exif.model)
print('make:', exif.make)
print('exposureTime:', exif.exposureTime.asDouble())
print('focalLength:', exif.focalLength.asDouble())
print('exposureTime:', exif.exposureTime.asDouble())
print('focalLength:', exif.focalLength.asDouble())
print('fNumber:',exif.fNumber.asDouble())
print('isoSpeedRatings:',exif.isoSpeedRatings)

write_exif('path/to/new_image.jpg', exif)
~~~~~~~~~~~~~~~

EXIF metadata can be read and written along with an image by specifying them in the ImageMetadata. In this case, the EXIF wil be read and written when calling `read_image` and `write_image`.

~~~~~~~~~~~~~~~{.python}
image, metadata = read_image('/path/to/image.jpg')
metadata.exifMetadata.make = 'Custom'
write_options = ImageWriter.Options(metadata)
write_image('/path/to/image.jpg', image, write_options)
~~~~~~~~~~~~~~~

# License

This project is licensed under the MIT License - see the [LICENSE.md](./LICENSE.md)file for details
