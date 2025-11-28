import sys
from unittest import mock

import pytest

from cxx_image_io import LIB_EXT, preload_libs

pytestmark = pytest.mark.unittest


def test_preload_libs_success(tmp_path):
    lib_name = "testlib"
    platform = sys.platform
    ext = None

    # Given: platform has a known extension in LIB_EXT
    for key, value in LIB_EXT.items():
        if platform.startswith(key):
            ext = value
            break
    assert ext is not None, f"No extension defined for platform {platform}"

    # Given: a temporary "DLL" file exists
    lib_file = tmp_path / f"{lib_name}{ext}"
    lib_file.write_text("fake dll content")

    # When: preload_libs is called with this library
    with mock.patch("ctypes.CDLL") as mock_cdll:
        preload_libs(str(tmp_path), [lib_name])

        # Then: ctypes.CDLL should be called once with correct path
        mock_cdll.assert_called_once_with(str(lib_file))


def test_preload_libs_file_not_exist(tmp_path):
    # Given: a library file that does not exist in the directory
    lib_name = "nonexistent"
    # When & Then: preload_libs should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        preload_libs(str(tmp_path), [lib_name])


def test_preload_libs_unsupported_platform(monkeypatch):
    # Given: an unknown / unsupported platform
    monkeypatch.setattr(sys, "platform", "unknown_os")

    # When & Then: preload_libs should raise RuntimeError
    with pytest.raises(RuntimeError, match="Unsupported platform"):
        preload_libs("/some/dir", ["dummy"])
