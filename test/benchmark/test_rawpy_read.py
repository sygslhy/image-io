# tests/benchmark/test_rawpy_read.py
from pathlib import Path
import rawpy

def test_rawpy_open(benchmark, raw_file):
    def load():
        with rawpy.imread(str(raw_file)) as raw:
            raw.raw_image
    benchmark(load)
