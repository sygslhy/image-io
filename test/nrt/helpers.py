import hashlib
import math

import numpy as np

from cxx_image_io import ExifMetadata

EPSILON = 1e-5
PSNR_THRESHOLD = 40.0


def psnr(a, b):
    mse = np.mean((a - b)**2)
    if mse == 0:
        return float('inf')
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))


def get_file_hash(file_name):
    with open(file_name, 'rb') as f:
        content = f.read()
    return hashlib.sha256(content).hexdigest()


def get_image_hash(image_array):
    image_bytes = image_array.tobytes()
    return hashlib.sha256(image_bytes).hexdigest()


def setup_custom_exif():
    return ExifMetadata(make="Canon",
                        model="Canon EOS 350D DIGITAL",
                        isoSpeedRatings=100,
                        exposureTime=ExifMetadata.Rational(1, 800),
                        focalLength=ExifMetadata.Rational(20, 1),
                        fNumber=ExifMetadata.Rational(71, 10),
                        dateTimeOriginal="2008:12:14 15:54:54",
                        orientation=1,
                        software="change",
                        exposureBiasValue=ExifMetadata.SRational(0, 1))


def is_musl():
    import os
    import subprocess

    # 1. check musl dll link name
    if os.path.exists("/lib/ld-musl-x86_64.so.1"):
        return True

    # 2. check alpine
    if os.path.exists("/etc/alpine-release"):
        return True

    # 3.check ldd version
    try:
        out = subprocess.check_output(["ldd", "--version"], stderr=subprocess.STDOUT)
        if b"musl" in out:
            return True
    except Exception:
        pass

    return False
