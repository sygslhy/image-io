import sys
from pathlib import Path
current_dir =  Path(__file__).parent.parent

image_io_lib_path = Path(current_dir, 'build', 'image_io', 'binding')  
sys.path.append(str(image_io_lib_path))
