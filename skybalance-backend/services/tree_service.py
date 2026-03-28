"""Tree service — main orchestrator for all SkyBalance tree operations."""

from collections import deque

from core.avl_tree import AVL
from core.bts_tree import BST
from core.node import Node
from core.history_stack import HistoryStack
from models.Flight import Flight
from services.flight_service import FlightService


class TreeService:
    """
    Central service that owns the live AVL tree, the BST (INSERCION mode),
    the undo stack, the insertion queue, and named version snapshots.

    Every method that mutates the tree calls __save_history() first so the
    operation can always be undone with undo().

    Sections covered:
        1.1 — load_json
        1.2 — insert_flight, update_flight, delete_flight, cancel_flight, undo
        1.3 — export_json
        2   — save_version, restore_version, list_versions, delete_version
        3   — enqueue, process_one_from_queue, process_full_queue, list_queue
        4   — get_metrics
        5   — enable_stress_mode, global_rebalance
        6   — set_critical_depth
        7   — audit_avl
        8   — eliminate_least_profitable
    """

    def __init__(self):
        """Initialize the service with empty trees and empty state containers."""
        self.avl            = AVL()
        self.bst            = BST()
        self.history        = HistoryStack(maxSize=50)
        self._queue         = deque()   # Section 3 — pending insertions
        self._versions      = {}        # Section 2 — { name: serialized root dict }
        self._load_mode     = None      # "TOPOLOGIA" | "INSERCION" | None
        self._critical_depth = 999      # Section 6 — price surcharge threshold

    # ================================================================
    # Section 1.1 — Load JSON
    # ================================================================

    def load_json(self, raw_bytes: bytes, critical_depth: int = 999) -> dict:
        """
        Load a JSON file and populate the AVL (and BST in INSERCION mode).
        Resets all current state before loading.
        Returns the serialized trees and their properties.
        """
        self.__full_reset()
        self._critical_depth = critical_depth

        result = FlightService.load_from_json(raw_bytes, self.avl, self.bst)
        self._load_mode = result["mode"]

        # Apply pricing rules with the configured critical depth
        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)

        return result

    # ================================================================
    # Section 1.2 — Node CRUD
    # ================================================================

    def insert_flight(self, flight_data: dict) -> dict:
        """
        Insert a new flight into the AVL tree.
        Saves an undo snapshot before mutating.
        Returns the updated tree and its properties.
        """
        self.__save_history()

        flight = Flight.fromDict(flight_data)
        node   = Node(flight)
        self.avl.insert(node)

        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return self.__tree_response()

    def update_flight(self, code: str, updates: dict) -> dict:
        """
        Update fields of an existing flight in place.
        Does not change the tree structure.
        Returns the updated tree or an error dict.
        """
        # Build a temporary flight just to use as search key
        key    = Flight.fromDict({"codigo": code})
        node   = self.avl.search(key)

        if node is None:
            return {"error": f"Vuelo {code} no encontrado."}

        self.__save_history()
        flight = node.get_value()

        # Map of accepted update field names to their setter methods
        field_map = {
            "origen":      flight.set_origin,
            "origin":      flight.set_origin,
            "destino":     flight.set_destination,
            "destination": flight.set_destination,
            "horaSalida":  flight.set_departure_time,
            "departureTime": flight.set_departure_time,
            "precioBase":  flight.set_base_price,
            "basePrice":   flight.set_base_price,
            "pasajeros":   flight.set_passengers,
            "passengers":  flight.set_passengers,
            "prioridad":   flight.set_priority,
            "priority":    flight.set_priority,
            "promocion":   flight.set_promotion,
            "promotion":   flight.set_promotion,
            "alerta":      flight.set_alert,
            "alert":       flight.set_alert,
        }

        for field, value in updates.items():
            if field in field_map:
                field_map[field](value)

        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return self.__tree_response()

    def delete_flight(self, code: str) -> dict:
        """
        Delete a single node from the AVL tree.
        Does NOT remove descendants — use cancel_flight for that.
        Returns the updated tree or an error dict.
        """
        key  = Flight.fromDict({"codigo": code})
        node = self.avl.search(key)

        if node is None:
            return {"error": f"Vuelo {code} no encontrado."}

        self.__save_history()
        self.avl.delete(key)

        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return self.__tree_response()

    def cancel_flight(self, code: str) -> dict:
        """
        Cancel a flight — removes the node AND all its descendants (Section 1.2).
        Different from delete: the entire subtree is dropped.
        Returns how many nodes were removed and the updated tree.
        """
        key  = Flight.fromDict({"codigo": code})
        node = self.avl.search(key)

        if node is None:
            return {"error": f"Vuelo {code} no encontrado."}

        self.__save_history()
        removed = self.avl.cancel(key)
        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return {"nodesRemoved": removed, **self.__tree_response()}

    def search_flight(self, code: str) -> dict:
        """Search for a single flight by code. Returns its data or an error dict."""
        key  = Flight.fromDict({"codigo": code})
        node = self.avl.search(key)

        if node is None:
            return {"error": f"Vuelo {code} no encontrado."}

        return node.get_value().toDict()

    # ================================================================
    # Section 1.2 — Undo (Ctrl+Z)
    # ================================================================

    def undo(self) -> dict:
        """
        Restore the tree to its state before the last mutating operation.
        Returns the restored tree or an error if the stack is empty.
        """
        previous_root = self.history.pop()

        if previous_root is None:
            return {"error": "No hay acciones para deshacer."}

        self.avl.root = previous_root
        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return self.__tree_response()

    # ================================================================
    # Section 1.3 — Export JSON
    # ================================================================

    def export_json(self) -> bytes:
        """Export the current AVL tree to a topology JSON (bytes for download)."""
        return FlightService.export_to_json(self.avl)

    # ================================================================
    # Section 2 — Named versions
    # ================================================================

    def save_version(self, name: str) -> dict:
        """Save a named snapshot of the current tree."""
        self._versions[name] = FlightService.serialize_tree(self.avl.get_root())
        return {"saved": name, "versions": list(self._versions.keys())}

    def restore_version(self, name: str) -> dict:
        """
        Restore the tree from a named snapshot.
        Saves a history entry so the restore itself can be undone.
        """
        if name not in self._versions:
            return {"error": f"Versión '{name}' no existe."}

        self.__save_history()
        snapshot = self._versions[name]

        if snapshot:
            self.avl.root = FlightService.build_from_topology(snapshot, parent=None, depth=0)
        else:
            self.avl.root = None

        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return {"restored": name, **self.__tree_response()}

    def list_versions(self) -> list:
        """Return the names of all saved versions."""
        return list(self._versions.keys())

    def delete_version(self, name: str) -> dict:
        """Delete a saved version by name."""
        if name not in self._versions:
            return {"error": f"Versión '{name}' no existe."}
        del self._versions[name]
        return {"deleted": name, "versions": list(self._versions.keys())}

    # ================================================================
    # Section 3 — Insertion queue (concurrency simulation)
    # ================================================================

    def enqueue(self, flight_data: dict) -> dict:
        """
        Add a flight to the pending insertion queue.
        Does NOT insert it yet — just schedules it for later processing.
        """
        self._queue.append(flight_data)
        return {
            "queued":  len(self._queue),
            "pending": list(self._queue),
        }

    def process_one_from_queue(self) -> dict:
        """
        Insert the next flight from the queue into the AVL tree.
        Shows the tree state after each individual insertion.
        Returns an error if the queue is empty.
        """
        if not self._queue:
            return {"error": "La cola está vacía."}

        flight_data = self._queue.popleft()
        result      = self.insert_flight(flight_data)
        return {
            "inserted":  flight_data,
            "remaining": len(self._queue),
            **result,
        }

    def process_full_queue(self) -> dict:
        """Drain the entire queue inserting all pending flights at once."""
        inserted_codes = []
        while self._queue:
            flight_data = self._queue.popleft()
            self.insert_flight(flight_data)
            inserted_codes.append(flight_data.get("codigo", ""))
        return {"insertedCodes": inserted_codes, **self.__tree_response()}

    def list_queue(self) -> dict:
        """Return the current pending insertions in the queue."""
        return {"size": len(self._queue), "pending": list(self._queue)}

    def remove_from_queue(self, code: str) -> dict:
        """Remove a specific flight from the queue without inserting it."""
        for i, flight_data in enumerate(self._queue):
            if str(flight_data.get("codigo", "")) == code:
                del self._queue[i]
                return {"removed": code, "remaining": len(self._queue)}
        return {"error": f"Vuelo {code} no está en la cola."}

    # ================================================================
    # Section 4 — Analytics / metrics
    # ================================================================

    def get_metrics(self) -> dict:
        """
        Return all real-time tree metrics in a single call.
        Includes height, node count, leaf count, rotation stats,
        mass cancellation count, stress mode status, and all traversals.
        """
        root = self.avl.get_root()
        has_root = root is not None

        return {
            "height":            self.avl.calculate_height(root) + 1 if has_root else 0,
            "totalNodes":        self.avl.count_nodes(),
            "leafCount":         self.avl.count_leaves(),
            "rotations":         self.avl.get_rotation_stats(),
            "massCancellations": self.avl.mass_cancellations,
            "stressMode":        self.avl.stress_mode,
            "criticalDepth":     self._critical_depth,
            # All traversal orders as lists of flight dicts
            "bfs":     [f.toDict() for f in self.avl.get_breadth_first_list()] if has_root else [],
            "dfs":     [f.toDict() for f in self.avl.get_pre_order_list()]     if has_root else [],
            "inorder": [f.toDict() for f in self.avl.get_in_order_list()]      if has_root else [],
        }

    # ================================================================
    # Section 5 — Stress mode / deferred rebalancing
    # ================================================================

    def enable_stress_mode(self) -> dict:
        """
        Enable stress mode — all mutations bypass automatic rebalancing.
        The tree can degrade visually to show the impact of imbalance.
        """
        self.avl.enable_stress_mode()
        return {"stressMode": True}

    def global_rebalance(self) -> dict:
        """
        Exit stress mode and rebalance the entire tree.
        Rebuilds from an in-order walk to guarantee AVL property.
        Returns rotation statistics produced during the repair.
        """
        self.__save_history()
        rotation_stats = self.avl.global_rebalance()
        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return {
            "stressMode":       False,
            "rotationsApplied": rotation_stats,
            **self.__tree_response(),
        }

    # ================================================================
    # Section 6 — Critical depth penalty
    # ================================================================

    def set_critical_depth(self, depth: int) -> dict:
        """
        Update the critical depth threshold.
        Immediately recalculates finalPrice and rentability for every node.
        Nodes deeper than threshold get a 25% price surcharge.
        """
        self._critical_depth = depth
        FlightService.recalculate_prices(self.avl.get_root(), self._critical_depth)
        return {"criticalDepth": depth, **self.__tree_response()}

    # ================================================================
    # Section 7 — AVL audit (only in stress mode)
    # ================================================================

    def audit_avl(self) -> dict:
        """
        Verify the AVL property across the entire tree.
        Only available in stress mode — the tree may have been degraded.
        Returns a report listing every node with balance factor outside {-1,0,1}.
        """
        if not self.avl.stress_mode:
            return {"error": "La auditoría solo está disponible en modo estrés."}
        return self.avl.audit_avl()

    # ================================================================
    # Section 8 — Least profitable elimination
    # ================================================================

    def eliminate_least_profitable(self) -> dict:
        """
        Find and cancel the flight with the lowest rentability score.

        Tie-break rules:
          1. Lowest rentability wins.
          2. If tied, the deepest node wins (farthest from root).
          3. If still tied, the node with the largest code wins.

        Cancels the entire subtree of the chosen node.
        """
        if self.avl.get_root() is None:
            return {"error": "El árbol está vacío."}

        target = self.__find_least_profitable()
        if target is None:
            return {"error": "No se encontró un nodo candidato."}

        code   = target.get_value().get_code()
        result = self.cancel_flight(code)

        return {
            "cancelledCode": code,
            "rentability":   target.get_value().get_rentability(),
            **result,
        }

    def __find_least_profitable(self):
        """
        Walk the entire tree and return the node with the lowest rentability.
        Tie-break: deepest first, then largest code.
        """
        candidates = []
        self.__collect_rentability(self.avl.get_root(), candidates)

        if not candidates:
            return None

        # Tie-break rules:
        # 1) Lower rentability
        # 2) Greater depth
        # 3) Greater code (lexicographically)
        best = candidates[0]
        for candidate in candidates[1:]:
            if candidate[0] < best[0]:
                best = candidate
                continue

            if candidate[0] > best[0]:
                continue

            if candidate[1] > best[1]:
                best = candidate
                continue

            if candidate[1] < best[1]:
                continue

            if candidate[2] > best[2]:
                best = candidate

        return best[3]

    def __collect_rentability(self, node, result: list):
        """Recursively collect (rentability, depth, code, node) tuples."""
        if node is None:
            return
        flight = node.get_value()
        result.append((
            flight.get_rentability(),
            flight.get_depth(),
            flight.get_code(),
            node,
        ))
        self.__collect_rentability(node.get_left_child(), result)
        self.__collect_rentability(node.get_right_child(), result)

    # ================================================================
    # Private helpers
    # ================================================================

    def __save_history(self):
        """Push a deep copy of the current AVL root onto the undo stack."""
        self.history.push(self.avl.get_root())

    def __tree_response(self) -> dict:
        """Standard response containing the serialized AVL tree and its properties."""
        return {
            "tree":       FlightService.serialize_tree(self.avl.get_root()),
            "properties": FlightService.tree_properties(self.avl),
        }

    def __full_reset(self):
        """Reset all state — called before loading a new JSON file."""
        self.avl             = AVL()
        self.bst             = BST()
        self.history.clear()
        self._queue.clear()
        self._versions.clear()
        self._load_mode      = None
        self._critical_depth = 999