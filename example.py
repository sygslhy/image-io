import ctypes
import sys

# Load DLL into memory only on Windows.
if sys.platform == "win32":
    hllDll = ctypes.WinDLL("D:\\image-io\\cxx_image_io\\libexif.dll")
    hllDll1 = ctypes.WinDLL("D:\\image-io\\cxx_image_io\\libraw_r.dll")
    hllDll2 = ctypes.WinDLL("D:\\image-io\\cxx_image_io\\cxx_image.cp313-win_amd64.pyd")
    hllDll3 = ctypes.WinDLL("D:\\image-io\\cxx_image_io\\cxx_libraw.cp313-win_amd64.pyd")
else:
    # Load shared libraries on Linux.
    hllDll = ctypes.CDLL("/home/ysun/image-io/cxx_image_io/libexif.so")
    hllDll1 = ctypes.CDLL("/home/ysun/image-io/cxx_image_io/libraw_r.so")
    hllDll1 = ctypes.CDLL("/home/ysun/image-io/cxx_image_io/libloguru.so")
    hllDll2 = ctypes.CDLL("/home/ysun/image-io/cxx_image_io/cxx_image.cpython-312-x86_64-linux-gnu.so")
    hllDll3 = ctypes.CDLL("/home/ysun/image-io/cxx_image_io/cxx_libraw.cpython-312-x86_64-linux-gnu.so")
