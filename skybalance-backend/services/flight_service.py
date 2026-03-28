"""Flight service — handles JSON loading and tree serialization for SkyBalance."""

import json

from models.Flight import Flight
from core.node import Node
from core.avl_tree import AVL
from core.bts_tree import BST


class FlightService:
    """
    Handles everything related to reading/writing flights from/to JSON
    and converting the live tree into a serializable structure.

    Two loading modes (Section 1.1):
        TOPOLOGIA  — tree is rebuilt exactly as described in the JSON
        INSERCION  — flights are inserted one by one into a fresh AVL and BST
    """

    # JSON loading (Section 1.1)

    @staticmethod
    def load_from_json(raw_bytes: bytes, avl: AVL, bst: BST) -> dict:
        """
        Parse raw JSON bytes and populate the trees.
        Returns a summary dict with the serialized trees and their properties.
        Raises ValueError if the JSON type is unknown.
        """
        data = json.loads(raw_bytes)
        mode = str(data.get("tipo", "TOPOLOGIA")).upper()

        if mode == "TOPOLOGIA":
            FlightService.__load_topology(data, avl)
            return {
                "mode":    "TOPOLOGIA",
                "avl":     FlightService.tree_properties(avl),
                "bst":     None,
                "avlTree": FlightService.serialize_tree(avl.get_root()),
                "bstTree": None,
            }

        if mode == "INSERCION":
            ordering = data.get("ordenamiento", "codigo")
            flights  = data.get("vuelos", [])
            # Sort by the specified key before inserting so both trees
            # receive flights in the same order
            flights  = sorted(flights, key=lambda f: str(f.get(ordering, "")))
            FlightService.__load_insercion(flights, avl, bst)
            return {
                "mode":    "INSERCION",
                "avl":     FlightService.tree_properties(avl),
                "bst":     FlightService.bst_properties(bst),
                "avlTree": FlightService.serialize_tree(avl.get_root()),
                "bstTree": FlightService.serialize_tree(bst.get_root()),
            }

        raise ValueError(f"Tipo de JSON desconocido: '{mode}'. Use 'TOPOLOGIA' o 'INSERCION'.")

    @staticmethod
    def __load_topology(data: dict, avl: AVL):
        """Reconstruct the AVL from a topology JSON respecting parent-child links."""
        avl.root = FlightService.build_from_topology(data, parent=None, depth=0)

    @staticmethod
    def build_from_topology(data: dict, parent, depth: int):
        """
        Recursively build Node objects from a topology dict.
        Preserves the exact structure described in the JSON.
        """
        if data is None:
            return None

        flight = Flight.fromDict(data)
        flight.set_depth(depth)

        node = Node(flight)
        node.set_parent(parent)

        node.set_left_child(
            FlightService.build_from_topology(data.get("izquierdo"), node, depth + 1)
        )
        node.set_right_child(
            FlightService.build_from_topology(data.get("derecho"), node, depth + 1)
        )
        return node

    @staticmethod
    def __load_insercion(flights: list, avl: AVL, bst: BST):
        """
        Insert each flight one by one into both AVL and BST.
        AVL rebalances automatically on each insertion.
        BST does not rebalance — used for visual comparison.
        """
        for flight_data in flights:
            # Create independent Flight objects for each tree
            avl_flight = Flight.fromDict(flight_data)
            bst_flight = Flight.fromDict(flight_data)

            avl.insert(Node(avl_flight))
            bst.insert(Node(bst_flight))

    # JSON export (Section 1.3)

    @staticmethod
    def export_to_json(avl: AVL) -> bytes:
        """
        Serialize the current AVL tree to a topology JSON file (bytes).
        Includes all required fields: hierarchy, heights, balance factors,
        prices, passengers, promotions, alerts, priorities, rentability.
        """
        data = FlightService.serialize_tree(avl.get_root())
        return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def serialize_tree(node) -> dict:
        """
        Recursively serialize a node and its entire subtree to a dict.
        Returns None for empty nodes (used for izquierdo/derecho fields).
        Each node's dict also carries the current height and balance factor.
        """
        if node is None:
            return None

        flight = node.get_value()
        data   = flight.toDict()

        # Attach real-time AVL structural metadata
        data["izquierdo"] = FlightService.serialize_tree(node.get_left_child())
        data["derecho"]   = FlightService.serialize_tree(node.get_right_child())

        return data

    # Tree property summaries 

    @staticmethod
    def tree_properties(avl: AVL) -> dict:
        """Return structural statistics for the AVL tree."""
        root = avl.get_root()
        return {
            "raiz":          root.get_value().get_code() if root else None,
            "profundidad":   avl.calculate_height(root) + 1 if root else 0,
            "cantidadHojas": avl.count_leaves(),
            "totalNodos":    avl.count_nodes(),
            "rotaciones":    avl.get_rotation_stats(),
        }

    @staticmethod
    def bst_properties(bst: BST) -> dict:
        """Return structural statistics for the BST tree."""
        root = bst.get_root()
        return {
            "raiz":          root.get_value().get_code() if root else None,
            "profundidad":   bst.calculate_height(root) + 1 if root else 0,
            "cantidadHojas": bst.count_leaves(),
            "totalNodos":    bst.count_nodes(),
        }

    # Price recalculation (Section 6)

    @staticmethod
    def recalculate_prices(node, critical_depth: int, depth: int = 0):
        """
        Walk the entire tree and recompute finalPrice and rentability
        for every node based on the current critical_depth threshold.

        Must be called after:
          - Any insert, delete or cancel operation (depth of nodes changes).
          - The user changes the critical depth value.
        """
        if node is None:
            return

        flight = node.get_value()
        flight.set_depth(depth)
        flight.computeFinalPrice(critical_depth)
        flight.computeRentability()

        FlightService.recalculate_prices(node.get_left_child(),  critical_depth, depth + 1)
        FlightService.recalculate_prices(node.get_right_child(), critical_depth, depth + 1)