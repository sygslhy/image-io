from pathlib import Path

import pytest

from cxx_image_io import (BaseImageReader, CxxImageReader, LibRaw_errors,
                          LibRawImageReader)

# ---------------------------------------------------------------------
# BaseImageReader tests
# ---------------------------------------------------------------------


def test_base_reader_can_read_not_implemented():
    # Given: a BaseImageReader class
    # When / Then: calling can_read on the class should raise NotImplementedError
    with pytest.raises(NotImplementedError, match="can_read must be implemented in subclasses"):
        BaseImageReader.can_read(None, Path("x.raw"))  # 第一个参数是 self，可以传 None


def test_base_reader_read_not_implemented():
    # Given: a BaseImageReader class
    # When / Then: calling read on the class should raise NotImplementedError
    with pytest.raises(NotImplementedError, match="read must be implemented in subclasses"):
        BaseImageReader.read(None, Path("x.raw"))


# ---------------------------------------------------------------------
# CxxImageReader tests
# ---------------------------------------------------------------------


def test_cxx_can_read_supported_ext():
    # Given: a CxxImageReader
    reader = CxxImageReader()

    # When / Then: supported extensions return True
    assert reader.can_read(Path("a.jpg"))
    assert reader.can_read(Path("b.PNG"))
    assert reader.can_read(Path("c.nv12"))

    # When / Then: unsupported extensions return False
    assert not reader.can_read(Path("x.txt"))


# ---------------------------------------------------------------------
# LibRawImageReader tests
# ---------------------------------------------------------------------


def test_libraw_can_read_by_extension():
    # Given: a LibRaw reader
    reader = LibRawImageReader()

    # When / Then: RAW extensions are recognized
    assert reader.can_read(Path("x.cr2"))
    assert reader.can_read(Path("y.ARW"))

    # When / Then: non-RAW extension is False
    assert not reader.can_read(Path("z.jpg"))


def test_libraw_try_open_fail(monkeypatch):
    # Given: LibRaw patched to return unsupported error
    class FakeLibRaw:
        def open_file(self, path):
            return LibRaw_errors.LIBRAW_FILE_UNSUPPORTED

    monkeypatch.setattr("cxx_image_io.LibRaw", FakeLibRaw)

    reader = LibRawImageReader()

    # When / Then: libraw rejects → can_read = False
    assert not reader.can_read(Path("file.bad"))
