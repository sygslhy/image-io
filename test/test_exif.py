from .data_cases import TEST_CASES
from .helpers import EPSILON, setup_custom_exif

from cxx_image_io import read_exif, read_image, write_exif

import shutil
import pytest


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
    image_path = test_images_dir / case.file
    _, metadata = read_image(image_path)
    compare_exif_values(metadata.exifMetadata, case.exif)


@pytest.mark.parametrize('case', [case for case in TEST_CASES if case.name in ('jpg', 'dng', 'tif')])
def test_read_only_exif(test_images_dir, case):
    # Use read_exif API to test only EXIF reading .
    image_path = test_images_dir / case.file
    exif = read_exif(image_path)
    compare_exif_values(exif, case.exif)


@pytest.mark.parametrize('case', [case for case in TEST_CASES if case.name in ('jpg', 'tif')])
def test_write_exif(test_images_dir, test_outputs_dir, case):
    image_path = test_images_dir / case.file
    tmp_image_path = test_outputs_dir / case.file
    tmp_image_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(image_path, tmp_image_path)

    exif = setup_custom_exif()

    write_exif(tmp_image_path, exif)

    # read back from new stored image file
    parsed_exif = read_exif(tmp_image_path)

    # both exif data must be equal
    assert parsed_exif.dateTimeOriginal == exif.dateTimeOriginal
    assert abs(parsed_exif.exposureTime.asDouble() - exif.exposureTime.asDouble()) < EPSILON
    assert abs(parsed_exif.focalLength.asDouble() - exif.focalLength.asDouble()) < EPSILON
    assert abs(parsed_exif.fNumber.asDouble() - exif.fNumber.asDouble()) < EPSILON
    assert (parsed_exif.make, parsed_exif.model) == (exif.make, exif.model)
    assert (parsed_exif.isoSpeedRatings, parsed_exif.orientation,
            parsed_exif.software) == (exif.isoSpeedRatings, exif.orientation, exif.software)
