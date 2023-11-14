from setuptools import setup, Extension, find_packages

setup(
    name = 'image io',
    version = '0.0.1',
    description = 'Python module with binding cxx image code',
    url = None,
    author = 'Yuan SUN',
    author_email = 'sunyuan860510@gmail.com',
    packages = find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_dir={'image-io': 'image_io'},
    package_data={'image_io': ['*.pyd']},
    install_requires = ['numpy'],
    python_requires = '>=3.8',
    license='MIT',
    zip_safe=False,
)