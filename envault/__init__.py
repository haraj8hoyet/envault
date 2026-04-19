"""envault — securely store and sync environment variables."""

__version__ = "0.1.0"
__author__ = "envault contributors"
__license__ = "MIT"


def get_version() -> str:
    """Return the current version of envault.

    Returns:
        str: The version string in PEP 440 format.

    Example:
        >>> import envault
        >>> envault.get_version()
        '0.1.0'
    """
    return __version__
