try:
    from importlib.metadata import version, PackageNotFoundError
except (ModuleNotFoundError, ImportError):
    from importlib_metadata import version, PackageNotFoundError
try:
    __version__ = version("brep_to_h5m")
except PackageNotFoundError:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)

__all__ = ["__version__"]

from .core import *
