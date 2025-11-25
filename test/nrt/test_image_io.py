import platform
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from cxx_image_io import (ImageMetadata, ImageWriter, LibRaw_errors, Matrix3,
                          UnSupportedFileException, read_image,
                          read_image_libraw, write_image)

from .data_cases import TEST_CASES
from .helpers import (PSNR_THRESHOLD, get_file_hash, get_image_hash, is_musl,
                      psnr, setup_custom_exif)

pytestmark = pytest.mark.nrt


@pytest.mark.parametrize("case", [
    pytest.param(
        case,
        marks=pytest.mark.skip(
            reason="skip on musl x86_64, because musl x86_64 pixel mismatch for nikon and kodak_slr"),
    ) if (case.name in ("nikon", "kodak_slr") and is_musl() and platform.machine() == "x86_64") else case
    for case in TEST_CASES
])
def test_read_image(test_images_dir, case):
    # Given: an existing image file with known numpy representation and metadata
    image_path = test_images_dir / case.file

    # When: the image is read using read_image API
    image, metadata = read_image(image_path)

    # Then: the image should be a numpy array with expected dtype, shape and ndim
    assert isinstance(image, np.ndarray)
    assert (image.dtype, image.shape, image.ndim) == case.numpy_info

    # Then: metadata fileInfo should match expected pixel type, precision, and layout
    assert metadata.fileInfo.pixelType == case.file_info.pixelType
    assert metadata.fileInfo.pixelPrecision == case.file_info.pixelPrecision
    assert metadata.fileInfo.imageLayout == case.file_info.imageLayout

    # Then: the image hash should match the reference hash
    ref_hash = case.sha256
    hash = get_image_hash(image)
    assert ref_hash == hash


def test_read_image_with_non_existing_file(test_images_dir):
    # Given: a non-existing image file
    image_path = test_images_dir / 'non_existing_file.jpg'

    # When / Then: reading the image should raise AssertionError
    with pytest.raises(AssertionError, match="Image file .* not found"):
        read_image(image_path)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.name in ('raw')])
def test_read_image_with_non_existing_sidecar(test_images_dir, test_outputs_dir, case):
    # Given: a RAW image file copied to a temporary location without its sidecar metadata
    image_path = test_images_dir / case.file
    tmp_image_path = test_outputs_dir / case.file
    tmp_image_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(image_path, tmp_image_path)

    # When / Then: reading the image should raise SystemExit due to missing sidecar
    with pytest.raises(SystemExit, match="Exception caught in reading image, check the error log."):
        read_image(tmp_image_path)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.name in ('yuv')])
def test_read_image_with_non_existing_metadata(test_images_dir, case):
    # Given: a YUV image file and a non-existing metadata JSON file
    image_path = test_images_dir / case.file
    meta_path = test_images_dir / 'non_existing_file_metadata.json'

    # When / Then: reading the image with metadata should raise AssertionError
    with pytest.raises(AssertionError, match="Metadata file .* not found"):
        read_image(image_path, metadata_path=meta_path)


def test_read_image_libraw_unsupported_file():
    # Given: a LibRaw instance whose open_file returns a failure code
    with patch("cxx_image_io.utils.io_cxx_libraw.LibRaw") as MockLibRaw:
        mock_processor = MagicMock()
        mock_processor.open_file.return_value = LibRaw_errors.LIBRAW_FILE_UNSUPPORTED
        MockLibRaw.return_value = mock_processor

        image_path = Path("dummy.cr2")

        # When / Then: read_image_libraw should raise UnSupportedFileException
        with pytest.raises(UnSupportedFileException, match="Unsupported libRaw file type"):
            read_image_libraw(image_path)


WRITE_TEST_CASES_INDEX = ('raw', 'bmp', 'jpg', 'png', 'png_16bit', 'tif', 'tif_16bit', 'cfa', 'rawmipi12', 'rawmipi10',
                          'dng', 'yuv', 'nv12')


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.name in WRITE_TEST_CASES_INDEX])
def test_write_image(test_images_dir, test_outputs_dir, test_npy_dir, case):
    # Given: an image numpy array and its metadata prepared with EXIF and calibration data
    metadata = ImageMetadata()
    metadata.fileInfo.pixelType, metadata.fileInfo.imageLayout = case.file_info.pixelType, case.file_info.imageLayout
    metadata.fileInfo.pixelPrecision = case.file_info.pixelPrecision
    metadata.fileInfo.fileFormat = case.file_info.fileFormat
    metadata.exifMetadata = setup_custom_exif()

    metadata.cameraControls.whiteBalance = ImageMetadata.WhiteBalance(2.2502453327178955, 1.493620753288269)
    metadata.shootingParams.ispGain = 1.1892070770263672
    metadata.calibrationData.blackLevel = 258
    metadata.calibrationData.whiteLevel = 4095
    metadata.calibrationData.colorMatrix = Matrix3(
        [[1.7485008239746094, -0.9061940312385559, 0.15769319236278534],
         [0.017115920782089233, 1.318513035774231, -0.3356289267539978],
         [0.03677308186888695, -0.3459629416465759 - 0.3356289267539978, 1.309189796447754]])

    output_path = test_outputs_dir / case.file

    write_options = ImageWriter.Options(metadata)
    write_options.fileFormat = metadata.fileInfo.fileFormat

    # Set JPEG quality to max to reduce the compression loss.
    if case.name == 'jpg':
        write_options.jpegQuality = 100

    npy_path = test_npy_dir / case.npy
    image = np.load(npy_path)

    # When: the image is written using write_image
    write_image(output_path, image, write_options)

    # Then: for formats requiring pixel comparison, the output image should match the input image
    if case.only_pixel_cmp:
        # jpg, bmp and png header has different varaition due to different machine
        # so cannot compare the sha1, only compre the image content.
        out_image, metadata = read_image(output_path)
        if case.name == 'jpg':
            assert psnr(out_image, image) > PSNR_THRESHOLD, 'Image arrays are visualy different'
        else:
            assert np.array_equal(out_image, image), 'Image arrays are different'
        return

    # Then: for other formats, the file hash should match the reference file
    output_hash = get_file_hash(output_path)
    ref_path = test_images_dir / case.file
    ref_hash = get_file_hash(ref_path)
    assert output_hash == ref_hash, 'Different hash between output and ref.'


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.name in 'jpg'])
def test_write_image_empty_metadata(test_outputs_dir, test_npy_dir, case):
    # Given: a numpy array of a jpg image and empty metadata
    output_path = test_outputs_dir / 'non_existing_file.jpg'
    metadata = ImageMetadata()
    write_options = ImageWriter.Options(metadata)
    npy_path = test_npy_dir / case.npy
    image = np.load(npy_path)

    # When / Then: writing the image should raise SystemExit due to missing file context
    with pytest.raises(SystemExit, match="Exception caught in writing image, check the error log."):
        write_image(output_path, image, write_options)
