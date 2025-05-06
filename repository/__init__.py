"""
pydiscovery.repository package – abstractions over element storage.
"""

from pydiscovery.repository.code_element_repository import CodeElementRepository
from pydiscovery.repository.in_memory_repository import InMemoryCodeElementRepository

__all__ = [
    "CodeElementRepository",
    "InMemoryCodeElementRepository",
]
