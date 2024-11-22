import os
import platform
import re
import subprocess
import pathlib
from packaging import version

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
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = version.Version(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if str(cmake_version) < '3.11.0':
                raise RuntimeError("CMake >= 3.11.0 is required")

        for ext in self.extensions:
            if isinstance(ext, CMakeExtension):
                self.build_extension(ext)

    def build_extension(self, ext):

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]
        build_lib_path = os.path.join(ext.sourcedir,
                                       os.path.dirname(self.get_outputs()[0]))

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        cmake_cfg = ['cmake', '-B', self.build_temp, '-S', ext.sourcedir, '--install-prefix', build_lib_path]
        cmake_cfg += ['-G', 'Ninja']
        subprocess.check_call(cmake_cfg)
        subprocess.check_call(['cmake', '--build', self.build_temp] +
                              build_args)
        subprocess.check_call(['cmake', '--install', self.build_temp])


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    long_description = long_description,
    ext_modules=[
        # This CmakeExtension take care build the binding projet
        # by cmake to generate pyd file.
        CMakeExtension(name='cxx_image', sourcedir='.'),
        # This Extension take care only to save the source C++ code.
        Extension(name='cxx_image_io',
                  sources=[
                      'binding/BindingEntryPoint.cpp',
                      'binding/ExifMetadata.cpp',
                      'binding/Image.cpp',
                      'binding/ImageIO.cpp',
                      'binding/ImageMetadata.cpp',
                      'binding/Matrix.cpp',
                      'binding/MetadataParser.cpp',
                      'binding/CMakeLists.txt', 'CMakeLists.txt'
                  ]),
    ],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    package_data={
      '': ['*.dll', '*.dylib', '*.so'],
    },
    package_dir={'cxx-image-io': 'cxx_image_io'})
