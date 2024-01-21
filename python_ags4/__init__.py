from importlib.metadata import metadata

_DISTRIBUTION_METADATA = metadata("python-ags4")
__version__ = _DISTRIBUTION_METADATA["Version"]
