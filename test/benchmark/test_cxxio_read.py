import pytest

from cxx_image_io import read_image

pytestmark = pytest.mark.nrt


def test_cxxio_raw(benchmark, raw_file):
    benchmark(lambda: read_image(raw_file))
