import os
import pathlib
import re
import shutil
import subprocess
from distutils.version import LooseVersion

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))

        if cmake_version < LooseVersion('3.11.0'):
            raise RuntimeError("CMake >= 3.11.0 is required")

        for ext in self.extensions:
            if isinstance(ext, CMakeExtension):
                self.build_extension(ext)

    def build_extension(self, ext):
        build_args = ['-DCMAKE_BUILD_TYPE=Release']
        if os.name == 'nt':
            build_args += ['-G', 'Ninja']
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        cmake_cfg = ['cmake', '-B', self.build_temp, '-S', ext.sourcedir] + build_args
        subprocess.check_call(cmake_cfg)
        subprocess.check_call(['cmake', '--build', self.build_temp, '-j4'])
        subprocess.check_call(['cmake', '--install', self.build_temp])

        # WA, the build backend script search first the package and associated data,
        # then build the C++ codes, but before build C++ code there wasn't the .pyd file
        # which provide the binding interface.
        # So the solution is to copy explicitly the pyd file to build_lib folder,
        # so that the install_lib in build backend will take care of it.
        # copy D:\Work\image-io\cxx_image_io\cxx_image.cp312-win_amd64.pyd to
        # build\lib.win-amd64-cpython-312\cxx_image_io\cxx_image.cp312-win_amd64.pyd
        build_lib_path = os.path.join(ext.sourcedir, os.path.dirname(self.get_outputs()[0]))
        all_files = []
        source_dir = pathlib.Path(ext.sourcedir, 'cxx_image_io')
        for ext in ['*.so.*', '*.so', '*.dll', '*.pyd', '*dylib']:
            all_files.extend(source_dir.glob(ext))

        print('found files to install', all_files)
        for ori_path in all_files:
            filename = ori_path.name
            pathlib.Path(build_lib_path).mkdir(parents=True, exist_ok=True)
            target_path = os.path.join(build_lib_path, 'cxx_image_io', filename)
            shutil.copy(ori_path, target_path, follow_symlinks=True)


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    long_description=long_description,
    ext_modules=[
        # This CmakeExtension take care build the binding projet
        # by cmake to generate pyd file.
        CMakeExtension(name='cxx_image', sourcedir='.'),
        # This Extension take care only to save the source C++ code.
        Extension(name='cxx_image_io',
                  sources=[
                      'binding/cxx_image/BindingEntryPoint.cpp', 'binding/cxx_image/ExifMetadata.cpp',
                      'binding/cxx_image/Image.cpp', 'binding/cxx_image/ImageIO.cpp',
                      'binding/cxx_image/ImageMetadata.cpp', 'binding/cxx_image/Matrix.cpp',
                      'binding/cxx_image/MetadataParser.cpp', 'binding/cxx_image/CMakeLists.txt',
                      'binding/CMakeLists.txt', 'CMakeLists.txt', 'binding/cxx_libraw/BindingEntryPoint.cpp',
                      'binding/cxx_libraw/RawTypes.cpp', 'binding/cxx_libraw/Metadata.cpp',
                      'binding/cxx_libraw/CMakeLists.txt'
                  ]),
    ],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    package_data={
        '': ['*.dll', '*.dylib', '*.so', '*.so*'],
    },
    package_dir={'cxx-image-io': 'cxx_image_io'})
