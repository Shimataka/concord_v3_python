from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class LoadedClass(Generic[T]):
    name: str
    class_obj: type[T]
