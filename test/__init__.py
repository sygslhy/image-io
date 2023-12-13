import sys
from pathlib import Path

# Append directly the .pyd file in build directory to sys.path
# So we can run the test without installation package.
current_dir = Path(__file__).parent.parent
image_io_lib_path = Path(current_dir, 'build', 'cxx_image_io', 'binding')
sys.path.append(str(image_io_lib_path))
