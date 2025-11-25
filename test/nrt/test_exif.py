import shutil

import pytest

from cxx_image_io import read_exif, read_image, write_exif

from .data_cases import TEST_CASES
from .helpers import EPSILON, setup_custom_exif

pytestmark = pytest.mark.nrt


def compare_exif_values(exif, ref_exif):
    assert exif.dateTimeOriginal == ref_exif.dateTimeOriginal
    assert abs(exif.exposureTime.asDouble() - ref_exif.exposureTime.asDouble()) < EPSILON
    assert abs(exif.focalLength.asDouble() - ref_exif.focalLength.asDouble()) < EPSILON
    assert abs(exif.fNumber.asDouble() - ref_exif.fNumber.asDouble()) < EPSILON
    assert exif.isoSpeedRatings == ref_exif.isoSpeedRatings
    assert exif.make == ref_exif.make
    assert exif.model == ref_exif.model
    assert exif.orientation == ref_exif.orientation
    assert exif.software == ref_exif.software


@pytest.mark.parametrize('case', [case for case in TEST_CASES if case.exif])
def test_read_exif(test_images_dir, case):
    # Given an image file that contains EXIF metadata.
    image_path = test_images_dir / case.file

    # When the image is read using the read_image API.
    _, metadata = read_image(image_path)

    # Then the EXIF metadata should match the expected values.
    compare_exif_values(metadata.exifMetadata, case.exif)


@pytest.mark.parametrize('case', [case for case in TEST_CASES if case.name in ('jpg', 'dng', 'tif')])
def test_read_only_exif(test_images_dir, case):
    # Given an image file of a format that supports EXIF (jpg, dng, tif).
    image_path = test_images_dir / case.file

    # When the EXIF metadata is read using the read_exif API.
    exif = read_exif(image_path)

    # Then the returned EXIF metadata should match the expected values.
    compare_exif_values(exif, case.exif)


def test_read_only_exif_error_handling(test_images_dir):
    #  Given a non-existing image file.
    image_path = test_images_dir / 'non_existing_file.jpg'

    # When read_exif is called,
    # Then an AssertionError should be raised indicating the image file was not found.
    with pytest.raises(AssertionError, match="Image file .* not found"):
        read_exif(image_path)


@pytest.mark.parametrize('case', [case for case in TEST_CASES if case.name in ('bmp', 'png', 'raw')])
def test_read_only_with_no_exif_images(test_images_dir, case):
    # Given an image file of a format that does not support EXIF (bmp, png, raw).
    image_path = test_images_dir / case.file

    # When read_exif is called.
    exif = read_exif(image_path)

    # Then the returned EXIF metadata should be None.
    assert exif is None


@pytest.mark.parametrize('case', [case for case in TEST_CASES if case.name in ('jpg', 'tif')])
def test_write_exif(test_images_dir, test_outputs_dir, case):

    # Given an image file of a format that supports EXIF (jpg, tif).
    # And a custom EXIF metadata to write,
    image_path = test_images_dir / case.file
    tmp_image_path = test_outputs_dir / case.file
    tmp_image_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(image_path, tmp_image_path)
    exif = setup_custom_exif()

    # When the EXIF metadata is written to a copied image file.
    write_exif(tmp_image_path, exif)

    # Then reading the EXIF back from the new file should match the written metadata.
    parsed_exif = read_exif(tmp_image_path)
    assert parsed_exif.dateTimeOriginal == exif.dateTimeOriginal
    assert abs(parsed_exif.exposureTime.asDouble() - exif.exposureTime.asDouble()) < EPSILON
    assert abs(parsed_exif.focalLength.asDouble() - exif.focalLength.asDouble()) < EPSILON
    assert abs(parsed_exif.fNumber.asDouble() - exif.fNumber.asDouble()) < EPSILON
    assert (parsed_exif.make, parsed_exif.model) == (exif.make, exif.model)
    assert (parsed_exif.isoSpeedRatings, parsed_exif.orientation,
            parsed_exif.software) == (exif.isoSpeedRatings, exif.orientation, exif.software)


def test_write_exif_no_file(test_outputs_dir):
    # Given a non-existing image file And a custom EXIF metadata
    tmp_image_path = test_outputs_dir / 'non_existing_file.jpg'
    exif = setup_custom_exif()
    # When write_exif is called,
    # Then a SystemExit exception should be raised indicating a failure in writing EXIF.
    with pytest.raises(SystemExit, match="Exception caught in writing exif, check the error log."):
        write_exif(tmp_image_path, exif)
