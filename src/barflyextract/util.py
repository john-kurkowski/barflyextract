import itertools
from typing import Callable, Iterable, Tuple, TypeVar

T = TypeVar("T")


def partition(
    items: Iterable[T], predicate: Callable[[T], bool] = bool
) -> Tuple[Iterable[T], Iterable[T]]:
    el1, el2 = itertools.tee((predicate(item), item) for item in items)
    return (
        (item for pred, item in el2 if pred),
        (item for pred, item in el1 if not pred),
    )
