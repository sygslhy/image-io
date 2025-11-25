# tests/benchmark/test_cxxio_read.py
from pathlib import Path
from cxx_image_io import read_image

def test_cxxio_raw(benchmark, raw_file):
    benchmark(lambda: read_image(raw_file))
