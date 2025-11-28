import pytest
import rawpy

pytestmark = pytest.mark.nrt


def test_rawpy_open(benchmark, raw_file):
    def load():
        with rawpy.imread(str(raw_file)) as raw:
            raw.raw_image

    benchmark(load)
