from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name='Gerador de Telas',
    ext_modules=cythonize("compute.pyx", annotate=True, language_level=3),
    include_dirs=[numpy.get_include()],
    zip_safe=False,
)
