from importlib.metadata import version

__version__ = version("pytac")
del version

__all__ = ["__version__"]
