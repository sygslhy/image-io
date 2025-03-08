# CXX Image IO

![PyPI - Version](https://img.shields.io/pypi/v/cxx-image-io)
![Supported Python versions](https://img.shields.io/pypi/pyversions/cxx-image-io.svg?style=flat-square)
![Supported OS](https://img.shields.io/badge/OS-Linux_%7C_Windows_%7C_macOS-blue)
![Supported Archi](https://img.shields.io/badge/Architecture-x86__64_%7C_ARM__64-green)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/sygslhy/image-io/blob/main/LICENSE.md)
![Wheel OS](https://img.shields.io/badge/wheels-Linux_%7C_Windows_%7C_macOS-green)
[![CI](https://github.com/sygslhy/image-io/actions/workflows/wheels.yml/badge.svg)](https://github.com/sygslhy/image-io/actions/workflows/wheels.yml)
[![Weekly](https://github.com/sygslhy/image-io/actions/workflows/schedule.yml/badge.svg)](https://github.com/sygslhy/image-io/actions/workflows/schedule.yml)


# What's new since  `v1.1.1`

Since version `v1.1.1`, `cxx-image-io` supports reading Bayer RAW images from reflex cameras into numpy.array, while also parsing some EXIF information. It is integrated with the C++ library .

The RAW image formats of the following camera manufacturers are supported, user can open these camera raw files by `read_image`, get image as `numpy.array` format:

| Camera manufacturer | Image format |
|---------------------|--------------|
| Canon               | CR2          |
| Nikon               | NEF          |
| Sony                | ARW          |
| Panasonic           | RW2          |
| Kodak               | DCR          |
| Samsung             | SRW          |
| Olympus             | ORF          |
| Leica               | RAW          |
| Pentax              | PEF          |

# Introduction

CXX Image IO is a Python project which provides the image IO interfaces, binding with the C++ library: https://github.com/emmcb/cxx-image.
These IO interfaces are designed to read and write images in many file formats in generic way and to interact nicely with numpy array.

| Image format  | Read | Write  | EXIF | Pixel precision        | Pixel type           | File extension                   |  Sidecar needed  |
|---------------|------|--------|------|------------------------|----------------------|----------------------------------|------------------|
| BMP           | x    | x      |      | 8 bits                 | Grayscale, RGB, RGBA | .bmp                             |                  |
| CFA           | x    | x      |      | 16 bits                | Bayer                | .cfa                             |                  |
| DNG           | x    | x      | x    | 16 bits, float         | Bayer, RGB           | .dng                             |                  |
| JPEG          | x    | x      | x    | 8 bits                 | Grayscale, RGB       | .jpg, .jpeg                      |                  |
| MIPI RAW      | x    | x      |      | 10 bits, 12 bits       | Bayer                | .RAWMIPI, .RAWMIPI10, .RAWMIPI12 | x                |
| PLAIN RAW     | x    | x      |      | *                      | *                    | .raw .plain16, .nv12, .yuv, *    | x                |
| PNG           | x    | x      |      | 8 bits, 16 bits        | Grayscale, RGB, RGBA | .png                             |                  |
| TIFF          | x    | x      | x    | 8 bits, 16 bits, float | Bayer, RGB           | .tif, .tiff                      |                  |



# Getting Started

## Prerequisites

This projet currently supports Python from `3.9` to `3.13` on
- Windows: `x86_64`
- Linux: `x86_64` and `aarch64`, glibc `v2.28+`, musl libc `v1.2+`
- MacOS: `x86_64` and `arm64`, `v11.0+`

## Installation

The python package `cxx-image-io` is to be installed by `pip`

```sh
pip install cxx-image-io
```

# Usage

## Image reading basic example

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

The print result could be like this:
~~~~~~~~~~~~~~~{.sh}
Type: uint8
Shape: (551, 603, 3)
~~~~~~~~~~~~~~~

`ImageMetadata` is the information about the image, the component `fileInfo` including the pixel type, pixel precision and image layout, which define fundamentally how the pixels arranged in buffer.


~~~~~~~~~~~~~~~{.python}
print(metadata.fileInfo)
~~~~~~~~~~~~~~~

The print result could be like this:
~~~~~~~~~~~~~~~{.sh}
{'pixelPrecision': 8, 'imageLayout': 'interleaved', 'pixelType': 'rgb'}
~~~~~~~~~~~~~~~

`metadata.fileInfo` shows: `image` is a 3-dimensional numpy array, where rgb 3 channels interleaved, in each channel, pixel depth is 8 bits.

`ImageMetadata` has more components than `fileInfo`, it also includes `ExifMetadata`, `help(ImageMetadata)` will show the details.


### Read Camera manufacturer RAW image example:

reading camera manufacturer raw image is the same method as we read from .jpg or .tif, just call `read_image`.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import read_image
from cxx_image_io import ImageMetadata
import numpy as np
from pathlib import Path

image, metadata = read_image(Path('test/images/RAW_CANON_EOS_1DX.CR2'))
assert isinstance(image, np.ndarray)

print('Type:', image.dtype)
print('Shape:', image.shape)

print(metadata)
~~~~~~~~~~~~~~~


The print result will be like:
~~~~~~~~~~~~~~{.sh}
Type: uint16
Shape: (3584, 5344)
{
   "fileInfo":{
      "width":5344,
      "height":3584,
      "pixelPrecision":14,
      "imageLayout":"planar",
      "pixelType":"bayer_rggb",
      "pixelRepresentation":"uint16"
   },
   "exifMetadata":{
      "imageWidth":5218,
      "imageHeight":3482,
      "make":"Canon",
      "model":"EOS-1D X",
      "orientation":1,
      "exposureTime":[
         1,
         80
      ],
      "fNumber":[
         56,
         10
      ],
      "isoSpeedRatings":1600,
      "dateTimeOriginal":"2012:09:06 07:48:25",
      "focalLength":[
         700,
         10
      ]
   },
   "shootingParams":{

   },
   "cameraControls":{
      "whiteBalance":[
         1.75390625,
         1.4775390625
      ]
   },
   "calibrationData":{
      "blackLevel":2048,
      "whiteLevel":15438,
      "colorMatrix":[
         [
            1.9404515027999878,
            -1.1166307926177979,
            0.17617927491664886
         ],
         [
            -0.21374493837356567,
            1.6440128087997437,
            -0.430267870426178
         ],
         [
            0.021280933171510696,
            -0.5217925906181335,
            1.500511646270752
         ]
      ]
   },
   "semanticMasks":[

   ],
   "LibRawParams":{
      "rawWitdh":5344,
      "rawHeight":3584,
      "rawWidthVisible":5218,
      "rawWidthVisible":3482,
      "topMargin":100,
      "leftMargin":126
   }
}
~~~~~~~~~~~~~~~

Note that `camera manufacturer RAW image metadata` has an additional Parameters: `LibRawParams`, it contains the coordinates of the original RAW sizes, including the top and left margins, as well as the actual visible area's width and height in the original RAW.

According to these inforamtions, user can corp the visable zone on the RAW image numpy array.

## Image reading with sidecar JSON

Some file formats need to know in advance some informations about the image.
For example, the PLAIN RAW format is just a simple dump of a buffer into a file, thus it needs to know how to interpret the data.

Bayer Plain Raw 16 bits
~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.plain16'))
print('Type:', image.dtype)
print('Shape:', image.shape)
print(metadata.fileInfo)
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


After image reading, the information in JSON sidecar is parsed in `ImageMetadata` object.

The print result of will be like this:
~~~~~~~~~~~~~~~{.sh}
Type: uint16
Shape: (3072, 4080)
~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~{.sh}
{'width': 4080, 'height': 3072, 'pixelPrecision': 16, 'imageLayout': 'planar', 'pixelType': 'bayer_gbrg'}
~~~~~~~~~~~~~~~

`metadata.fileInfo` shows that `image` is a 2-dimensional numpy array, where pixel is Bayer type, planar layout (not interleaved), pixel depth is 16 bits.

`metadata.fileInfo` has more attributes to describe the file info, like `widthAlignment`, `heightAlignment`, please use `help(metadata.fileInfo)` to see the details.

Image sidecar is not mandatory, for the other formats which have already image information in their header, like jpg, png, tif, cfa. we don't need to provide image metadata.

### Other image reading with sidecar examples

<details>
  <summary>
  Click to unfold other image format sidecar examples
  </summary>

#### Packed RAW MIPI 12 bits:
python code
~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.RAWMIPI12'))
~~~~~~~~~~~~~~~

sidecar json
~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "fileFormat": "raw12",
        "height": 3000,
        "width": 4000,
        "pixelPrecision": 12,
        "pixelType": "bayer_gbrg"
    }
}
~~~~~~~~~~~~~~~

#### Packed RAW MIPI 10 bits:
python code
~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.RAWMIPI'))
~~~~~~~~~~~~~~~

sidecar json
~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "height": 3000,
        "width": 4000,
        "format": "raw10",
        "pixelPrecision": 10,
        "pixelType": "bayer_grbg"
    }
}
~~~~~~~~~~~~~~~

#### YUV 420 buffer 8 bits:
python code
~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.yuv'))
~~~~~~~~~~~~~~~

sidecar json
~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "format": "plain",
        "height": 300,
        "width": 400,
        "imageLayout": "yuv_420"
    }
}
~~~~~~~~~~~~~~~

#### NV12 buffer 8 bits:
python code
~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.nv12'))
~~~~~~~~~~~~~~~

sidecar json
~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "format": "plain",
        "height": 300,
        "width": 400,
        "imageLayout": "nv12"
    }
}
~~~~~~~~~~~~~~~


</details>


## Split and merge image channels
After calling `read_image`, `cxx-image-io` provides a public API `split_image_channels` which helps to split to different colors channels, so that user can do the different processes on them.  The function return type is a dictionary which contains the different color channel name as keys, and the value in numpy array of one single channel.

before calling `write_image`, `cxx-image-io` provides a public API `merge_image_channels` which helps to merge different colors channels to a numpy array buffer.

~~~~~~~~~~~~~~~{.python}
from cxx_image_io import read_image, split_image_channels, merge_image_channels, ImageLayout, ImageMetadata, PixelRepresentation, PixelType
import numpy as np
from pathlib import Path

rgb, metadata = read_image(Path('rgb_8bit.jpg'))

channels = split_image_channels(rgb, metadata)

# print(channels['r'])  # Red channel in numpy array
# print(channels['g'])  # Green channel in numpy array
# print(channels['b'])  # Blue channel in numpy array

rgb_post = merge_image_channels(channels, metadata)

np.array_equal(rgb, rgb_post)

cfa, metadata = read_image(Path('bayer_16bit.plain16'))

channels = split_image_channels(cfa, metadata)

# print(channels['gr'])  # Bayer Gr pixels in numpy array
# print(channels['r'])  # Bayer R pixels in numpy array
# print(channels['b'])  # Bayer B pixels in numpy array
# print(channels['gb'])  # Bayer Gb pixels in numpy array

cfa_post = merge_image_channels(channels, metadata)

np.array_equal(cfa, cfa_post)

yuv, metadata = read_image(Path('raw.nv12'))

channels = split_image_channels(yuv, metadata)

# print(channels['y'])  # Y plane in numpy array
# print(channels['u'])  # U plane in numpy array
# print(channels['v'])  # V plane in numpy array

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
metadata = ImageMetadata()
metadata.fileInfo.pixelType = PixelType.BAYER_GBRG
metadata.fileInfo.imageLayout = ImageLayout.PLANAR

write_options = ImageWriter.Options(metadata)
write_options.fileFormat = FileFormat.PLAIN

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.plain16'), image, write_options)
~~~~~~~~~~~~~~~


### Other image writing examples
<details>
  <summary>
  Click to unfold other image writing examples
  </summary>

#### Packed RAW MIPI 12 bits:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.BAYER_GBRG  # adapt with User's RAW Bayer pattern.
metadata.fileInfo.imageLayout = ImageLayout.PLANAR
metadata.fileInfo.pixelPrecision = 12

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.RAWMIPI12'), image, write_options)
~~~~~~~~~~~~~~~


#### Packed RAW MIPI 10 bits:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.BAYER_GBRG # to adapt with User's RAW Bayer pattern.
metadata.fileInfo.imageLayout = ImageLayout.PLANAR
metadata.fileInfo.pixelPrecision = 10

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.RAWMIPI10'), image, write_options)
~~~~~~~~~~~~~~~


#### YUV 420 buffer 8 bits:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.YUV
metadata.fileInfo.imageLayout = ImageLayout.YUV_420

write_options = ImageWriter.Options(metadata)
write_options.fileFormat = FileFormat.PLAIN

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.yuv'), image, write_options)

~~~~~~~~~~~~~~~

#### NV12 buffer 8 bits:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.YUV
metadata.fileInfo.imageLayout = ImageLayout.NV12

write_options = ImageWriter.Options(metadata)
write_options.fileFormat = FileFormat.PLAIN

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.nv12'), image, write_options)
~~~~~~~~~~~~~~~

#### Bayer dng 12 bits:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.BAYER_RGGB  # adapt with User's RAW Bayer pattern.
metadata.fileInfo.imageLayout = ImageLayout.PLANAR
metadata.fileInfo.pixelPrecision = 12

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.dng'), image, write_options)
~~~~~~~~~~~~~~~

#### RGB 8 bits images (jpg, png, tif, bmp):
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.RGB
metadata.fileInfo.imageLayout = ImageLayout.INTERLEAVED

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.jpg'), image, write_options)
~~~~~~~~~~~~~~~

#### CFA 16 bits image:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.BAYER_RGGB  # adapt with User's RAW Bayer pattern.
metadata.fileInfo.imageLayout = ImageLayout.PLANAR
metadata.fileInfo.pixelPrecision = 16

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.cfa'), image, write_options)
~~~~~~~~~~~~~~~

#### Grayscale 16 bits png image:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.GRAYSCALE
metadata.fileInfo.imageLayout = ImageLayout.PLANAR
metadata.fileInfo.pixelPrecision = 16

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.png'), image, write_options)
~~~~~~~~~~~~~~~

#### Bayer 16 bits tif image:
~~~~~~~~~~~~~~~{.python}
metadata = ImageMetadata()

metadata.fileInfo.pixelType = PixelType.BAYER_RGGB  # adapt with User's RAW Bayer pattern.
metadata.fileInfo.imageLayout = ImageLayout.PLANAR
metadata.fileInfo.pixelPrecision = 16

write_options = ImageWriter.Options(metadata)

assert isinstance(image, np.ndarray)
write_image(Path('/path/to/image.tif'), image, write_options)
~~~~~~~~~~~~~~~


</details>


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
{
  'make': 'Canon',
  'model': 'Canon EOS 40D',
  'orientation': 1,
  'software': 'GIMP 2.4.5',
  'exposureTime': [1, 160],
  'fNumber': [71, 10],
  'isoSpeedRatings': 100,
  'dateTimeOriginal': '2008:05:30 15:56:01',
  'exposureBiasValue': [0, 1],
  'focalLength': [135, 1]
}
~~~~~~~~~~~~~~~
user can use `help(exif)` to see the definition of `ExifMetdata`.

EXIF metadata can be read and written along with an image by specifying them in the ImageMetadata. In this case, the EXIF wil be read and written when calling `read_image` and `write_image`.

~~~~~~~~~~~~~~~{.python}
image, metadata = read_image(Path('/path/to/image.jpg'))
metadata.exifMetadata.make = 'Custom'
write_options = ImageWriter.Options(metadata)
write_image(Path('/path/to/image.jpg'), image, write_options)
~~~~~~~~~~~~~~~

# Dependencies

This project has the dependencies of the following libraries by cmake FetchContent:

## Statically linked
- libjpeg: https://libjpeg.sourceforge.net/
- libpng: http://www.libpng.org/pub/png/libpng.html
- libtiff: https://libtiff.gitlab.io/libtiff/
- adobe dng sdk: https://helpx.adobe.com/camera-raw/digital-negative.html
- pybind11 (BSD-2): https://github.com/pybind/pybind11
- cxx-image (Apache 2.0): https://github.com/emmcb/cxx-image

## Dynamically linked
- libexif (LGPL v2.1): https://libexif.github.io/
- libraw  (LGPL v2.1 and CDDL): https://www.libraw.org/


# License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/sygslhy/image-io/blob/main/LICENSE.md) file for details.
