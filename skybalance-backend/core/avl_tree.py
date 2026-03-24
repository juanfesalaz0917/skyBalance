"""AVL tree implementation used by SkyBalance."""

from collections import deque


class AVL:
    """Self-balancing binary search tree ordered by flight code."""

    def __init__(self):
        """Initialize an empty AVL tree."""
        self.root = None
        self.stress_mode = False
        self.rotation_count = {"LL": 0, "RR": 0, "LR": 0, "RL": 0}
        self.mass_cancellations = 0

    def get_root(self):
        """Return the root node."""
        return self.root

    def insert(self, node):
        """Insert a node and rebalance when stress mode is disabled."""
        if self.root is None:
            self.root = node
            return

        self.__insert(self.root, node)

    def __insert(self, current_root, node):
        """Insert recursively from the given root."""
        if node.get_value() == current_root.get_value():
            raise ValueError(f"El valor {node.get_value()} ya existe en el árbol.")

        if node.get_value() > current_root.get_value():
            if current_root.get_right_child() is None:
                current_root.set_right_child(node)
                node.set_parent(current_root)
                self.__check_balance(node)
                return

            self.__insert(current_root.get_right_child(), node)
            return

        if current_root.get_left_child() is None:
            current_root.set_left_child(node)
            node.set_parent(current_root)
            self.__check_balance(node)
            return

        self.__insert(current_root.get_left_child(), node)

    def search(self, value):
        """Search a node by value and return the node or None."""
        if self.root is None:
            raise ValueError("El árbol está vacío.")

        return self.__search(self.root, value)

    def __search(self, current_root, value):
        """Search recursively from the given root."""
        if value == current_root.get_value():
            return current_root

        if value > current_root.get_value():
            if current_root.get_right_child() is None:
                return None

            return self.__search(current_root.get_right_child(), value)

        if current_root.get_left_child() is None:
            return None

        return self.__search(current_root.get_left_child(), value)

    def delete(self, value):
        """Delete a single node by value using predecessor-based deletion."""
        if self.root is None:
            print("El árbol está vacío.")
            return

        node = self.search(value)
        if node is None:
            print(f"El nodo con valor {value} no existe en el árbol")
            return

        self.__delete(node)

    def __delete(self, node):
        """Delete a node according to its deletion case."""
        deletion_case = self.__identify_deletion_case(node)
        match deletion_case:
            case 1:
                self.__delete_leaf_node(node)
            case 2:
                self.__delete_node_with_one_child(node)
            case 3:
                self.__delete_node_with_two_children(node)

    def __delete_node_with_two_children(self, node):
        """Delete a node with two children using its inorder predecessor."""
        predecessor = self.__get_predecessor(node)
        node.set_value(predecessor.get_value())

        predecessor_case = self.__identify_deletion_case(predecessor)
        if predecessor_case == 1:
            self.__delete_leaf_node(predecessor)
            return

        self.__delete_node_with_one_child(predecessor)

    def __get_predecessor(self, node):
        """Return the inorder predecessor of the given node."""
        current = node.get_left_child()
        while current.get_right_child() is not None:
            current = current.get_right_child()
        return current

    def __delete_node_with_one_child(self, node):
        """Delete a node that has exactly one child."""
        if node.get_left_child() is not None:
            child_node = node.get_left_child()
        else:
            child_node = node.get_right_child()

        parent_node = node.get_parent()

        if parent_node is None:
            self.root = child_node
            child_node.set_parent(None)
        else:
            if parent_node.get_left_child() == node:
                parent_node.set_left_child(child_node)
            else:
                parent_node.set_right_child(child_node)

            child_node.set_parent(parent_node)

        node.set_left_child(None)
        node.set_right_child(None)
        node.set_parent(None)

        if not self.stress_mode and parent_node is not None:
            self.__check_balance(parent_node)

    def __delete_leaf_node(self, node):
        """Delete a leaf node."""
        if node == self.root:
            self.root = None
            return

        parent_node = node.get_parent()
        if parent_node.get_left_child() == node:
            parent_node.set_left_child(None)
        else:
            parent_node.set_right_child(None)

        node.set_parent(None)

        if not self.stress_mode:
            self.__check_balance(parent_node)

    def __identify_deletion_case(self, node):
        """Identify whether a node is a leaf, has one child, or has two."""
        if node.get_left_child() is None and node.get_right_child() is None:
            return 1

        if node.get_left_child() is not None and node.get_right_child() is not None:
            return 3

        return 2

    def breadth_first_search(self):
        """Return a breadth-first traversal as a list of node values."""
        if self.root is None:
            raise ValueError("El árbol está vacío.")

        return self.__breadth_first_search(self.root)

    def __breadth_first_search(self, current_root):
        """Traverse the tree in breadth-first order from the given root."""
        queue = deque([current_root])
        result = []

        while queue:
            current_root = queue.popleft()
            result.append(current_root.get_value())

            if current_root.get_left_child() is not None:
                queue.append(current_root.get_left_child())
            if current_root.get_right_child() is not None:
                queue.append(current_root.get_right_child())

        return result

    def pre_order_traversal(self):
        """Print the tree in pre-order traversal."""
        if self.root is None:
            raise ValueError("El árbol está vacío.")

        self.__pre_order_traversal(self.root)

    def __pre_order_traversal(self, current_root):
        """Traverse the tree in pre-order from the given root."""
        print(current_root.get_value())
        if current_root.get_left_child() is not None:
            self.__pre_order_traversal(current_root.get_left_child())
        if current_root.get_right_child() is not None:
            self.__pre_order_traversal(current_root.get_right_child())

    def in_order_traversal(self):
        """Print the tree in in-order traversal."""
        if self.root is None:
            raise ValueError("El árbol está vacío.")

        self.__in_order_traversal(self.root)

    def __in_order_traversal(self, current_root):
        """Traverse the tree in in-order from the given root."""
        if current_root.get_left_child() is not None:
            self.__in_order_traversal(current_root.get_left_child())

        print(current_root.get_value())

        if current_root.get_right_child() is not None:
            self.__in_order_traversal(current_root.get_right_child())

    def post_order_traversal(self):
        """Print the tree in post-order traversal."""
        if self.root is None:
            raise ValueError("El árbol está vacío.")

        self.__post_order_traversal(self.root)

    def __post_order_traversal(self, current_root):
        """Traverse the tree in post-order from the given root."""
        if current_root.get_left_child() is not None:
            self.__post_order_traversal(current_root.get_left_child())

        if current_root.get_right_child() is not None:
            self.__post_order_traversal(current_root.get_right_child())

        print(current_root.get_value())

    def calculate_height(self, node):
        """Return the height of the given node."""
        if node is None:
            return -1

        return self.__calculate_height(node)

    def __calculate_height(self, current_root):
        """Calculate node height recursively."""
        if current_root is None:
            return -1

        left_height = self.__calculate_height(current_root.get_left_child())
        right_height = self.__calculate_height(current_root.get_right_child())
        return 1 + max(left_height, right_height)

    def get_balance_factor(self, node):
        """Return the AVL balance factor of a node."""
        left_child_height = self.calculate_height(node.get_left_child())
        right_child_height = self.calculate_height(node.get_right_child())
        return left_child_height - right_child_height

    def __check_balance(self, node):
        """Walk upward from a node and rebalance ancestors when needed."""
        if node is None:
            return

        balance_factor = self.get_balance_factor(node)
        if balance_factor > 1 or balance_factor < -1:
            self.__rebalance(node, balance_factor)

        self.__check_balance(node.get_parent())

    def __rebalance(self, node, balance_factor):
        """Apply the appropriate AVL rotation for the current imbalance."""
        rebalance_case = self.__identify_rebalance_case(node, balance_factor)
        match rebalance_case:
            case "LL":
                self.__balance_ll(node)
                self.rotation_count["LL"] += 1
            case "RR":
                self.__balance_rr(node)
                self.rotation_count["RR"] += 1
            case "LR":
                self.__balance_lr(node)
            case "RL":
                self.__balance_rl(node)

    def __balance_lr(self, top_node):
        """Apply a left-right double rotation."""
        middle_node = top_node.get_left_child()
        self.__balance_rr(middle_node)
        self.__balance_ll(top_node)
        self.rotation_count["LR"] += 1

    def __balance_rl(self, top_node):
        """Apply a right-left double rotation."""
        middle_node = top_node.get_right_child()
        self.__balance_ll(middle_node)
        self.__balance_rr(top_node)
        self.rotation_count["RL"] += 1

    def __balance_ll(self, top_node):
        """Rotate left-left around the given top node."""
        middle_node = top_node.get_left_child()
        top_node_parent = top_node.get_parent()
        right_child_of_middle = middle_node.get_right_child()

        middle_node.set_right_child(top_node)
        top_node.set_parent(middle_node)

        middle_node.set_parent(top_node_parent)
        if top_node_parent is None:
            self.root = middle_node
        elif top_node_parent.get_left_child() == top_node:
            top_node_parent.set_left_child(middle_node)
        else:
            top_node_parent.set_right_child(middle_node)

        top_node.set_left_child(right_child_of_middle)
        if right_child_of_middle is not None:
            right_child_of_middle.set_parent(top_node)

    def __balance_rr(self, top_node):
        """Rotate right-right around the given top node."""
        middle_node = top_node.get_right_child()
        top_node_parent = top_node.get_parent()
        left_child_of_middle = middle_node.get_left_child()

        middle_node.set_left_child(top_node)
        top_node.set_parent(middle_node)

        middle_node.set_parent(top_node_parent)
        if top_node_parent is None:
            self.root = middle_node
        elif top_node_parent.get_left_child() == top_node:
            top_node_parent.set_left_child(middle_node)
        else:
            top_node_parent.set_right_child(middle_node)

        top_node.set_right_child(left_child_of_middle)
        if left_child_of_middle is not None:
            left_child_of_middle.set_parent(top_node)

    def __identify_rebalance_case(self, node, balance_factor):
        """Identify which AVL rebalance case applies to a node."""
        if balance_factor > 0:
            child_balance_factor = self.get_balance_factor(node.get_left_child())
            if child_balance_factor > 0:
                return "LL"
            return "LR"

        child_balance_factor = self.get_balance_factor(node.get_right_child())
        if child_balance_factor > 0:
            return "RL"
        return "RR"

    def print_tree(self):
        """Print the tree structure in ASCII form."""
        if self.root is None:
            print("El árbol está vacío.")
            return

        self.__print_tree(self.root, "", True)

    def __print_tree(self, node=None, prefix="", is_left=True):
        """Recursively print a tree branch."""
        if node is None:
            return

        if node.get_right_child():
            new_prefix = prefix + ("│   " if is_left else "    ")
            self.__print_tree(node.get_right_child(), new_prefix, False)

        connector = "└── " if is_left else "┌── "
        print(prefix + connector + str(node.get_value()))

        if node.get_left_child():
            new_prefix = prefix + ("    " if is_left else "│   ")
            self.__print_tree(node.get_left_child(), new_prefix, True)
