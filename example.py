import ctypes

# Load DLL into memory.

hllDll = ctypes.WinDLL ("D:\\image-io\\cxx_image_io\\libexif.dll")

hllDll2 = ctypes.WinDLL ("D:\\image-io\\cxx_image_io\\cxx_image.cp313-win_amd64.pyd")

hllDll1 = ctypes.WinDLL ("D:\\image-io\\cxx_image_io\\libraw_r.dll")

hllDll3 = ctypes.WinDLL ("D:\\image-io\\cxx_image_io\\cxx_libraw.cp313-win_amd64.pyd")
