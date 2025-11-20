import numpy as np
import pytest

from cxx_image_io import (FileFormat, ImageLayout, PixelRepresentation,
                          PixelType, RgbColorSpace, UnorderdMapSemanticMasks,
                          read_image)

from .data_cases import TEST_CASES
from .helpers import epsilon


def compare_fileinfo_values(fi, ref_fi):
    assert fi and ref_fi
    if fi.fileFormat:
        assert fi.fileFormat == ref_fi.fileFormat
    assert fi.imageLayout == ref_fi.imageLayout
    assert fi.pixelType == ref_fi.pixelType
    assert fi.pixelPrecision == ref_fi.pixelPrecision
    assert fi.pixelRepresentation == ref_fi.pixelRepresentation
    assert fi.width == ref_fi.width
    assert fi.height == ref_fi.height


def compare_shootingparams_values(sp, ref_sp):
    assert sp and ref_sp
    assert abs(sp.aperture - ref_sp.aperture) < epsilon
    assert abs(sp.exposureTime - ref_sp.exposureTime) < epsilon
    assert abs(sp.sensitivity - ref_sp.sensitivity) < epsilon
    assert abs(sp.totalGain - ref_sp.totalGain) < epsilon
    assert abs(sp.sensorGain - ref_sp.sensorGain) < epsilon
    assert abs(sp.ispGain - ref_sp.ispGain) < epsilon


def compare_calibration_values(calib, ref_calib):
    assert calib and ref_calib
    assert calib.blackLevel == ref_calib.blackLevel
    assert calib.whiteLevel == ref_calib.whiteLevel
    if calib.vignetting:
        assert np.allclose(np.array(calib.vignetting), np.array(ref_calib.vignetting), rtol=epsilon)
    if calib.colorMatrixTarget:
        assert calib.colorMatrixTarget == ref_calib.colorMatrixTarget
    if calib.colorMatrix:
        assert np.allclose(np.array(calib.colorMatrix), np.array(ref_calib.colorMatrix), rtol=epsilon)


def compare_cameracontrol_values(cc, ref_cc):
    assert cc and ref_cc
    assert abs(cc.whiteBalance.gainR - ref_cc.whiteBalance.gainR) < epsilon
    assert abs(cc.whiteBalance.gainB - ref_cc.whiteBalance.gainB) < epsilon
    if cc.colorShading:
        assert np.allclose(np.array(cc.colorShading.gainR), np.array(ref_cc.colorShading.gainR), rtol=epsilon)
        assert np.allclose(np.array(cc.colorShading.gainB), np.array(ref_cc.colorShading.gainB), rtol=epsilon)

    if cc.faceDetection:
        for (fd, ref_fd) in zip(cc.faceDetection, ref_cc.faceDetection):
            assert fd.x == ref_fd.x and fd.y == ref_fd.y
            assert fd.width == ref_fd.width and fd.height == ref_fd.height


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.file_info])
def test_parse_fileinfo(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None
    assert metadata.fileInfo is not None
    compare_fileinfo_values(metadata.fileInfo, case.file_info)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.shooting_params])
def test_parse_shootingparams(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None
    assert metadata.shootingParams is not None
    compare_shootingparams_values(metadata.shootingParams, case.shooting_params)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.calibration])
def test_parse_calibration(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None
    assert metadata.calibrationData is not None
    compare_calibration_values(metadata.calibrationData, case.calibration)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.cameracontrol])
def test_parse_cameracontrol(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None
    assert metadata.cameraControls is not None
    compare_cameracontrol_values(metadata.cameraControls, case.cameracontrol)
