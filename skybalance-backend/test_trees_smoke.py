"""Smoke tests for BST and AVL tree behavior."""

from core.avl_tree import AVL
from core.bts_tree import BST
from core.node import Node


def build_nodes(values):
    """Build Node instances from a sequence of values."""
    return [Node(value) for value in values]


def run_bst_checks():
    """Run insertion, search, deletion and height checks for BST."""
    bst = BST()
    for node in build_nodes([10, 5, 15, 3, 7, 12, 18]):
        bst.insert(node)

    assert bst.breadth_first_search() == [10, 5, 15, 3, 7, 12, 18]
    assert bst.search(7).get_value() == 7

    bst.delete(3)
    assert bst.breadth_first_search() == [10, 5, 15, 7, 12, 18]

    bst.delete(5)
    assert bst.breadth_first_search() == [10, 7, 15, 12, 18]

    bst.delete(15)
    assert bst.breadth_first_search() == [10, 7, 12, 18]

    return {
        "breadth_first_search": bst.breadth_first_search(),
        "height": bst.calculate_height(bst.get_root()),
    }


def run_avl_checks():
    """Run insertion, rotation and deletion checks for AVL."""
    avl = AVL()
    for node in build_nodes([30, 10, 20]):
        avl.insert(node)

    assert avl.get_root().get_value() == 20
    assert avl.breadth_first_search() == [20, 10, 30]
    assert avl.rotation_count["LR"] == 1

    avl.insert(Node(40))
    avl.delete(10)

    assert avl.get_root().get_value() == 30
    assert avl.breadth_first_search() == [30, 20, 40]

    return {
        "breadth_first_search": avl.breadth_first_search(),
        "height": avl.calculate_height(avl.get_root()),
        "rotation_count": avl.rotation_count,
    }


def main():
    """Execute smoke tests and print a compact summary."""
    result = {
        "bst": run_bst_checks(),
        "avl": run_avl_checks(),
    }
    print(result)


if __name__ == "__main__":
    main()