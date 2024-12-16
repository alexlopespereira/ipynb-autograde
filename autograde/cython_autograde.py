# from setuptools import setup
# from Cython.Build import cythonize
#
# setup(
#     ext_modules = cythonize("autograde.pyx")
# )

from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("autograde", ["autograde.pyx"])
]

setup(
    # ... (other setup arguments)
    ext_modules=cythonize(
        extensions,  # Replace with the name of your Cython file
        compiler_directives={'language_level': "3"},  # Set language level
    ),
)