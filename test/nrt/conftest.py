from pathlib import Path

import pytest


@pytest.fixture
def test_images_dir():
    return Path(__file__).parent.parent / "images"


@pytest.fixture
def test_npy_dir():
    return Path(__file__).parent.parent / "npy"


@pytest.fixture
def test_outputs_dir():
    return Path(__file__).parent.parent / "_outputs"
