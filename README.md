# CXX Image IO

CXX Image IO is a Python project which provides the image IO interfaces, binding with the C++ library: https://github.com/emmcb/cxx-image,
These IO interfaces are designed to read and write images in many file formats in generic way and to interact nicely with numpy array.

| Image format  | Read | Write  | EXIF | Pixel precision        | Pixel type           | File extension                   |
|---------------|------|--------|------|------------------------|----------------------|----------------------------------|
| BMP           | x    | x      |      | 8 bits                 | Grayscale, RGB, RGBA | .bmp                             |
| CFA           | x    | x      |      | 16 bits                | Bayer                | .cfa                             |
| DNG           | x    | x      | x    | 16 bits, float         | Bayer, RGB           | .dng                             |
| JPEG          | x    | x      | x    | 8 bits                 | Grayscale, RGB       | .jpg, .jpeg                      |
| MIPIRAW       | x    | x      |      | 10 bits, 12 bits       | Bayer                | .RAWMIPI, .RAWMIPI10, .RAWMIPI12 |
| PLAIN         | x    | x      |      | *                      | *                    | .plain16, .nv12, *               |
| PNG           | x    | x      |      | 8 bits, 16 bits        | Grayscale, RGB, RGBA | .png                             |
| TIFF          | x    | x      | x    | 8 bits, 16 bits, float | Bayer, RGB           | .tif, .tiff                      |

# Getting Started

## Prerequisites

- numpy >= 2.1.0
- ninja >= 1.11.1

This projet currently supports Python from 3.10 to 3.13 on
- Windows: x86_64
- Linux: x86_64 and aarch64, glibc 2.28+
- MacOS: x86_64 and arm64, 11.0+

## Installation

The python package `cxx-image-io` is to be installed by `pip`

```sh
pip install cxx-image-io
```

# Usage example

## Image reading

`read_image` is able to read a image file and return a numpy array and ImageMetadata object.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import read_image
from cxx_image_io import ImageMetadata
import numpy as np
from pathlib import Path

image, metadata = read_image(Path('/path/to/image.jpg'))
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
print(metadata.fileInfo)
~~~~~~~~~~~~~~~

The result could be like this:
~~~~~~~~~~~~~~~{.sh}
{'pixelPrecision': 8, 'imageLayout': 'interleaved', 'pixelType': 'rgb'}
~~~~~~~~~~~~~~~

Some file formats need to know in advance some informations about the image.
For example, the PLAIN format is just a simple dump of a buffer into a file, thus it needs to know how to interpret the data.

~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.plain16'))
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

The result of `print(metadata.fileInfo)`could be like this:
~~~~~~~~~~~~~~~{.sh}
{'width': 4080, 'height': 3072, 'pixelPrecision': 16, 'imageLayout': 'planar', 'pixelType': 'bayer_gbrg'}
~~~~~~~~~~~~~~~

Image sidecar is not mandatory, for the other formats which have already image information in their header, like jpg, png, tif, cfa. we don't need to provide image metadata.

## Split and merge image channels
After calling `read_image`, `cxx-image-io` provides a public API `split_image_channels` which helps to split to different colors channels, so that user can do the different processes on them.  The function return type is a dictionary which contains the different color channel name as keys, and the value in numpy array of one single channel.

before calling `write_image`, `cxx-image-io` provides a public API `merge_image_channels` which helps to merge different colors channels to a numpy array buffer.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import read_image, split_image_channels, merge_image_channels, ImageLayout, ImageMetadata, PixelRepresentation, PixelType
import numpy as np
from pathlib import Path

rgb, metadata = read_image(Path('rgb_8bit.jpg'))

channels = split_image_channels(rgb, metadata)

# print(channels['r'])  # Red channel
# print(channels['g'])  # Green channel
# print(channels['b'])  # Blue channel

rgb_post = merge_image_channels(channels, metadata)

np.array_equal(rgb, rgb_post)

cfa, metadata = read_image(Path('bayer_16bit.plain16'))

channels = split_image_channels(cfa, metadata)

# print(channels['gr'])  # Bayer Gr pixels
# print(channels['r'])  # Bayer R pixels
# print(channels['b'])  # Bayer B pixels
# print(channels['gb'])  # Bayer Gb pixels

cfa_post = merge_image_channels(channels, metadata)

np.array_equal(cfa, cfa_post)

yuv, metadata = read_image(Path('raw.nv12'))

channels = split_image_channels(yuv, metadata)

# print(channels['y'])  # Y plane
# print(channels['u'])  # U plane
# print(channels['v'])  # V plane

yuv_post = merge_image_channels(channels, metadata)

np.array_equal(yuv, yuv_post)


~~~~~~~~~~~~~~~



## Image writing

`write_image` is able to write a numpy array to image file.

To write the pure numpy array to different image file extensions.
User need to define the following fundamental parameters in ImageMetadata which is part of ImageWriter.Options.
In order to call the specific C++ image libraries with them.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import ImageMetadata, ImageWriter, FileFormat, PixelType, ImageLayout
from cxx_image_io import write_image
import numpy as np
from pathlib import Path

metadata = ImageMetadata()
metadata.fileInfo.pixelType = PixelType.RGB
metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.jpg'), image, write_options)
~~~~~~~~~~~~~~~

`write_image` can determine the image format by file extensions, but some formats don't not rely on a specific extension, for example the PLAIN format that allows to directly dump the image buffer to a file. In this case, the format can be specified through ImageWriter.Options.

~~~~~~~~~~~~~~~{.python}
write_options = ImageWriter.Options(metadata)
write_options.fileFormat = FileFormat.PLAIN

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.plain16'), image, write_options)
~~~~~~~~~~~~~~~



## EXIF

Some image formats, like JPEG and TIFF, support EXIF reading and writing.

If supported, EXIF can be read by calling `read_exif` and be written by calling `write_exif`.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import read_exif, write_exif
from pathlib import Path

exif = read_exif(Path('/path/to/image.jpg'))

print(exif)

write_exif(Path('path/to/new_image.jpg'), exif)
~~~~~~~~~~~~~~~

`print(exif)` will give the following output like:
~~~~~~~~~~~~~~~{.sh}
{'make': 'Canon', 'model': 'Canon EOS 40D', 'orientation': 1, 'software': 'GIMP 2.4.5', 'exposureTime': [1, 160], 'fNumber': [71, 10], 'isoSpeedRatings': 100, 'dateTimeOriginal': '2008:05:30 15:56:01', 'exposureBiasValue': [0, 1], 'focalLength': [135, 1]}
~~~~~~~~~~~~~~~
user can use `help(exif)` to see the definition of Exif metdata.

EXIF metadata can be read and written along with an image by specifying them in the ImageMetadata. In this case, the EXIF wil be read and written when calling `read_image` and `write_image`.

~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.jpg'))
metadata.exifMetadata.make = 'Custom'
write_options = ImageWriter.Options(metadata)
write_image(Path('/path/to/image.jpg'), image, write_options)
~~~~~~~~~~~~~~~

# License

This project is licensed under the MIT License - see the [LICENSE.md](./LICENSE.md) file for details
