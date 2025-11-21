import numpy as np
import pytest

from cxx_image_io import read_image

from .data_cases import TEST_CASES
from .helpers import EPSILON


def compare_fileinfo_values(fi, ref_fi):
    assert fi, 'FileInfo is None'
    assert ref_fi, 'Ref FileInfo is None'
    if fi.fileFormat:
        assert fi.fileFormat == ref_fi.fileFormat, 'FileFormat does not match'
    assert fi.imageLayout == ref_fi.imageLayout, 'ImageLayout does not match'
    assert fi.pixelType == ref_fi.pixelType, 'PixelType does not match'
    assert fi.pixelPrecision == ref_fi.pixelPrecision, 'PixelPrecision does not match'
    assert fi.pixelRepresentation == ref_fi.pixelRepresentation, 'PixelRepresentation does not match'
    assert fi.width == ref_fi.width, 'Image width does not match'
    assert fi.height == ref_fi.height, 'Image height does not match'


def compare_shootingparams_values(sp, ref_sp):
    assert sp, 'ShootingParams is None'
    assert ref_sp, 'Ref ShootingParams is None'
    assert abs(sp.aperture - ref_sp.aperture) < EPSILON, 'Aperture does not match'
    assert abs(sp.exposureTime - ref_sp.exposureTime) < EPSILON, 'ExposureTime does not match'
    assert abs(sp.sensitivity - ref_sp.sensitivity) < EPSILON, 'ISO Sensitivity does not match'
    assert abs(sp.totalGain - ref_sp.totalGain) < EPSILON, 'TotalGain does not match'
    assert abs(sp.sensorGain - ref_sp.sensorGain) < EPSILON, 'SensorGain does not match'
    assert abs(sp.ispGain - ref_sp.ispGain) < EPSILON, 'ISPGain does not match'


def compare_calibration_values(calib, ref_calib):
    assert calib, 'CalibrationData is None'
    assert ref_calib, 'Ref CalibrationData is None'
    assert calib.blackLevel == ref_calib.blackLevel, 'BlackLevel does not match'
    assert calib.whiteLevel == ref_calib.whiteLevel, 'WhiteLevel does not match'
    if calib.vignetting:
        assert np.allclose(np.array(calib.vignetting, dtype=np.float64),
                           np.array(ref_calib.vignetting, dtype=np.float64)), 'Vignetting does not match'
    if calib.colorMatrixTarget:
        assert calib.colorMatrixTarget == ref_calib.colorMatrixTarget
    if calib.colorMatrix:
        assert np.allclose(np.array(calib.colorMatrix, dtype=np.float64),
                           np.array(ref_calib.colorMatrix, dtype=np.float64)), 'ColorMatrix does not match'


def compare_cameracontrol_values(cc, ref_cc):
    assert cc, 'CameraControls is None'
    assert ref_cc, 'Ref CameraControls is None'
    assert abs(cc.whiteBalance.gainR - ref_cc.whiteBalance.gainR) < EPSILON, 'WhiteBalance gainR does not match'
    assert abs(cc.whiteBalance.gainB - ref_cc.whiteBalance.gainB) < EPSILON, 'WhiteBalance gainB does not match'
    if cc.colorShading:
        assert np.allclose(np.array(cc.colorShading.gainR, dtype=np.float64),
                           np.array(ref_cc.colorShading.gainR, dtype=np.float64)), 'ColorShading gainR does not match'
        assert np.allclose(np.array(cc.colorShading.gainB, dtype=np.float64),
                           np.array(ref_cc.colorShading.gainB, dtype=np.float64)), 'ColorShading gainB does not match'
    if cc.faceDetection:
        for (fd, ref_fd) in zip(cc.faceDetection, ref_cc.faceDetection):
            assert fd.x == ref_fd.x and fd.y == ref_fd.y, 'FaceDetection x,y does not match'
            assert fd.width == ref_fd.width and fd.height == ref_fd.height, 'FaceDetection width,height does not match'


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.file_info])
def test_parse_fileinfo(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None, 'Metadata is None'
    compare_fileinfo_values(metadata.fileInfo, case.file_info)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.shooting_params])
def test_parse_shootingparams(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None, 'Metadata is None'
    compare_shootingparams_values(metadata.shootingParams, case.shooting_params)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.calibration])
def test_parse_calibration(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None, 'Metadata is None'
    compare_calibration_values(metadata.calibrationData, case.calibration)


@pytest.mark.parametrize("case", [case for case in TEST_CASES if case.cameracontrol])
def test_parse_cameracontrol(test_images_dir, case):
    _, metadata = read_image(test_images_dir / case.file)
    assert metadata is not None, 'Metadata is None'
    compare_cameracontrol_values(metadata.cameraControls, case.cameracontrol)
