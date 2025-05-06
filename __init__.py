"""
pydiscovery – lightweight, dependency‑free Python code‑base discovery toolkit.
"""

from importlib import metadata as _metadata

__version__ = _metadata.version(__name__) if _metadata.packages_distributions().get(__name__) else "0.0.0"

__all__ = [
    "launcher",
    "analyzer",
    "repository",
    "model",
    "util",
    "__version__",
]
