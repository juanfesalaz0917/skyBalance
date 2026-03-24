#Clase que permite instanciar Nodos para alimentar un árbol.
class Node:
  # El constructor permite la asignación de un valor
  # También inicia tanto el padre como los hijos en None
  def __init__(self, value):
    self.value = value
    self.parent = None
    self.leftChild = None
    self.rightChild = None
    
  def getValue(self):
    return self.value
 
  def setValue(self, value):
    self.value = value

  # Método que permite asignar un padre al nodo
  # recibe la referencia al nodo padre que va a ser asignado
  def setParent(self, parentNode):
    self.parent = parentNode

  # Método que permite obtener la referencia al padre del nodo
  def getParent(self):
    return self.parent

  # Método que permite asignar un hijo izquierdo al nodo
  # se recibe la referencia al hijo que se va a asignar
  def setLeftChild(self, leftChildNode):
    self.leftChild = leftChildNode

  # Método para obtener la referencia al hijo izquiero del nodo
  def getLeftChild(self):
    return self.leftChild

  # Método que permite asignar un hijo derecho al nodo
  # se recibe la referencia al hijo que se va a asignar
  def setRightChild(self, rightChildNode):
    self.rightChild = rightChildNode

  # Método para obtener la referencia al hijo derecho del nodo
  def getRightChild(self):
    return self.rightChild
  
  #Helpers 
  
  # Método para determinar si el nodo es una hoja (no tiene hijos)
  def isLeaf(self) -> bool:
    return self.leftChild is None and self.rightChild is None
 
  # Método para determinar si el nodo es la raíz (no tiene padre)
  def __repr__(self):
    code = self.value.get_code() if self.value is not None else "None"
    return f"Node(code={code})"