import hashlib

from cxx_image_io import ExifMetadata

epsilon = 1e-7


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
