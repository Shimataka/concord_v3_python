from dataclasses import dataclass
from typing import Generic, TypeVar

TypeOfAny = TypeVar("TypeOfAny")


@dataclass
class LoadedClass(Generic[TypeOfAny]):
    name: str
    class_type: TypeOfAny
