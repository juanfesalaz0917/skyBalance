import copy

# HistoryStack — LIFO stack that stores tree snapshots for undo 
# How it works:
#   1. Before every mutating operation (insert, delete, cancel, update),
#      TreeService calls push() with a deep copy of the current tree root.
#   2. When the user clicks Undo (Ctrl+Z), TreeService calls pop() to get
#      the previous state and restores it as the tree root.

class HistoryStack:
 
    def __init__(self, maxSize: int = 50):
        # Internal list used as a stack (last element = top)
        self._stack = []
        # Maximum number of snapshots to keep in memory.
        # Oldest snapshots are dropped when the limit is reached.
        self.maxSize = maxSize 
        
    # Core operations
    def push(self, rootNode) -> None:
        """
        Save a deep copy of the current tree root onto the stack.
        Call this BEFORE every mutating operation so it can be undone.
        """
        if len(self._stack) >= self.maxSize:
            # Drop oldest snapshot to keep memory under control
            self._stack.pop(0)
        self._stack.append(copy.deepcopy(rootNode))
        
    def pop(self):
        """
        Remove and return the most recent snapshot.
        Returns None if the stack is empty (nothing to undo).
        """
        if not self.isEmpty():
            return self._stack.pop()
        return None
 
    def peek(self):
        """
        Return the most recent snapshot without removing it.
        Returns None if the stack is empty.
        """
        if not self.isEmpty():
            return self._stack[-1]
        return None
    
    # Utility method
    # Used by TreeService to check if undo is possible (stack not empty) and to display undo availability in the UI.
    def isEmpty(self) -> bool:
        return len(self._stack) == 0
    
    # For testing and debugging: get current stack size (number of snapshots stored).
    def size(self) -> int:
        return len(self._stack)
    
    # For testing and debugging: clear all snapshots from the stack.
    def clear(self) -> None:
        """Remove all snapshots. Used on full reset."""
        self._stack = []