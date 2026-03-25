"""Node model used by the tree implementations."""


class Node:
    """Tree node that stores a value plus parent and child references."""

    def __init__(self, value):
        """Initialize a node with empty links."""
        self.value = value
        self.parent = None
        self.left_child = None
        self.right_child = None

    def get_value(self):
        """Return the stored value."""
        return self.value

    def set_value(self, value):
        """Replace the stored value."""
        self.value = value

    def set_parent(self, parent_node):
        """Set the parent reference for the node."""
        self.parent = parent_node

    def get_parent(self):
        """Return the parent node or None."""
        return self.parent

    def set_left_child(self, left_child_node):
        """Set the left child reference."""
        self.left_child = left_child_node

    def get_left_child(self):
        """Return the left child or None."""
        return self.left_child

    def set_right_child(self, right_child_node):
        """Set the right child reference."""
        self.right_child = right_child_node

    def get_right_child(self):
        """Return the right child or None."""
        return self.right_child

    def is_leaf(self) -> bool:
        """Return True when the node has no children."""
        return self.left_child is None and self.right_child is None

    def __repr__(self):
        """Return a compact debug representation of the node."""
        code = self.value.get_code() if self.value is not None else "None"
        return f"Node(code={code})"