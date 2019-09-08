import itertools


def partition(items, predicate=bool):
    el1, el2 = itertools.tee((predicate(item), item) for item in items)
    return (
        (item for pred, item in el2 if pred),
        (item for pred, item in el1 if not pred),
    )
