from pathlib import Path

import pytest

test_images_dir = Path(__file__).parent.parent / "images"

@pytest.fixture
def raw_file():
    return test_images_dir / 'bayer_12bits.dng'

@pytest.fixture
def jpg_file():
    return test_images_dir / 'rgb_8bit.jpg'