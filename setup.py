import os
import platform
import re
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
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.10.0':
                raise RuntimeError("CMake >= 3.10.0 is required on Windows")

        for ext in self.extensions:
            if isinstance(ext, CMakeExtension):
                self.build_extension(ext)

    def build_extension(self, ext):

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', '-B', self.build_temp, '-S', '.'])
        subprocess.check_call(['cmake', '--build', self.build_temp] +
                              build_args)
        subprocess.check_call(['cmake', '--install', self.build_temp])

        # WA, the build backend script search first the package and associated data,
        # then build the C++ codes, but before build C++ code there wasn't the .pyd file
        # which provide the binding interface.
        # So the solution is to copy explicitly the pyd file to build_lib folder,
        # so that the install_lib in build backend will take care of it.
        # copy D:\Work\image-io\cxx_image_io\cxx_image.cp312-win_amd64.pyd to
        # build\lib.win-amd64-cpython-312\cxx_image_io\cxx_image.cp312-win_amd64.pyd
        pyd_name = os.path.basename(self.get_outputs()[0])
        pyd_target_path = os.path.join(os.path.dirname(self.get_outputs()[0]),
                                       'cxx_image_io', pyd_name)
        pyd_origin_path = os.path.join(ext.sourcedir, 'cxx_image_io', pyd_name)
        self.copy_file(pyd_origin_path, pyd_target_path, level=self.verbose)


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="cxx-image-io",
    version="0.0.5",
    author="Yuan SUN",
    author_email="sunyuan860510@gmail.com",
    description="Python image IO module with binding cxx image code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sygslhy/image-io",
    project_urls={
        "Homepage": "https://github.com/sygslhy/image-io",
        "Issues": "https://github.com/sygslhy/image-io/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    ext_modules=[
        # This CmakeExtension take care build the binding projet
        # by cmake to generate pyd file.
        CMakeExtension(name='cxx_image', sourcedir='.'),
        # This Extension take care only to save the source C++ code.
        Extension(name='cxx_image_io',
                  sources=[
                      'cxx_image_io/binding/BindingEntryPoint.cpp',
                      'cxx_image_io/binding/Image.cpp',
                      'cxx_image_io/binding/ImageIO.cpp',
                      'cxx_image_io/binding/ImageMetadata.cpp',
                      'cxx_image_io/binding/Matrix.cpp',
                      'cxx_image_io/binding/MetadataParser.cpp',
                      'cxx_image_io/binding/CMakeLists.txt', 'CMakeLists.txt'
                  ]),
    ],
    python_requires='>=3.10, <=3.12',
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
    packages=find_packages(
        exclude=["*.test", "*.test.*", "test.*", "test", "setup.py"]),
    package_dir={'cxx-image-io': 'cxx_image_io'},
    package_data={'cxx_image_io': ['*.pyd']},
    install_requires=['numpy>=1.26'])
