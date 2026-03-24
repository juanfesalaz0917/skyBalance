import json

# Flight class — represents a single flight in the SkyBalance system.
# Stores all flight data and computes derived fields (finalPrice, rentability).
class Flight:
    
    # Constructor — initializes all fields with safe default values.
    def __init__(self):
        
        self.code = ""
        self.origin = ""
        self.destination = ""
        self.departureTime = ""
        self.basePrice = 0.0
        self.finalPrice = 0.0
        self.passengers = 0
        self.priority = 1
        self.promotion = False
        self.alert = False
        #AVL tree metadata - updated by TreeService after each operation
        self.height = 1
        self.balanceFactor = 0
        self.depth = 0
        self.nodoCritico = False
        self.rentability = 0.0
        
    # Getters and setters
        
    def get_code(self):
        return self.code
    
    def set_code(self, code):
        self.code = code
    
    def get_origin(self):
        return self.origin
    
    def set_origin(self, origin):
        self.origin = origin
    
    def get_destination(self):
        return self.destination
    
    def set_destination(self, destination):
        self.destination = destination
    
    def get_departure_time(self):
        return self.departureTime
    
    def set_departure_time(self, departure_time):
        self.departureTime = departure_time
    
    def get_base_price(self):
        return self.basePrice
    
    def set_base_price(self, base_price):
        self.basePrice = base_price
    
    def get_final_price(self):
        return self.finalPrice
    
    def set_final_price(self, final_price):
        self.finalPrice = final_price
    
    def get_passengers(self):
        return self.passengers
    
    def set_passengers(self, passengers):
        self.passengers = passengers
    
    def get_priority(self):
        return self.priority
    
    def set_priority(self, priority):
        self.priority = priority
    
    def get_promotion(self):
        return self.promotion
    
    def set_promotion(self, promotion):
        self.promotion = promotion
    
    def get_alert(self):
        return self.alert
    
    def set_alert(self, alert):
        self.alert = alert
        
    def get_depth(self):
        return self.depth
    
    def set_depth(self, depth):
        self.depth = depth
        
    def get_height(self):
        return self.height
    
    def set_height(self, height):
        self.height = height
    
    def get_balance_factor(self):
        return self.balanceFactor
    
    def set_balance_factor(self, balanceFactor):
        self.balanceFactor = balanceFactor
        
    def get_nodo_critico(self):
        return self.nodoCritico
        
    def set_nodo_critico(self, nodoCritico):
        self.nodoCritico = nodoCritico
    
    # Business logic methods
    
    def computeFinalPrice(self, criticalDepth):
        """
        Applies a 25% surcharge when the node is deeper than criticalDepth.
        Called by TreeService after every insert, delete or depth change.
        """
        if self.depth > criticalDepth:
            self.nodoCritico = True
            self.finalPrice = round(self.basePrice * 1.25, 2)
        else:
            self.nodoCritico = False
            self.finalPrice = round(self.basePrice, 2)
            
    def computeRentability(self):
        """
        rentability = passengers x finalPrice
                      - 50  (if promotion is active)
                      + 100 (if nodoCritico is active)
        Lower score = candidate for elimination.
        """
        score = self.passengers * self.finalPrice
        if self.promotion:
            score -= 50.0
        if self.nodoCritico:
            score += 100.0
        self.rentability = round(score, 2)
        return self.rentability
    
    # Comparison operators — needed so AVL can compare nodes by code
    def __lt__(self, other):
        return self.code < other.code
 
    def __gt__(self, other):
        return self.code > other.code
 
    def __eq__(self, other):
        if isinstance(other, Flight):
            return self.code == other.code
        return False
 
    def __le__(self, other):
        return self.code <= other.code
 
    def __ge__(self, other):
        return self.code >= other.code
    
    # Serialization
    
    @classmethod
    def fromDict(cls, data: dict) -> "Flight":
        """
        Creates a Flight from a raw dict.
        Accepts both Spanish keys (from JSON files) and English keys.
        """
        f = cls()
        # Support both JSON formats (Spanish keys from project JSONs)
        f.code          = str(data.get("codigo",       data.get("code",          "")))
        f.origin        = str(data.get("origen",       data.get("origin",        "")))
        f.destination   = str(data.get("destino",      data.get("destination",   "")))
        f.departureTime = str(data.get("horaSalida",   data.get("departureTime", "")))
        f.basePrice     = float(data.get("precioBase", data.get("basePrice",     0.0)))
        f.finalPrice    = float(data.get("precioFinal",data.get("finalPrice",    f.basePrice)))
        f.passengers    = int(data.get("pasajeros",    data.get("passengers",    0)))
        f.priority      = int(data.get("prioridad",    data.get("priority",      1)))
        f.promotion     = bool(data.get("promocion",   data.get("promotion",     False)))
        f.alert         = bool(data.get("alerta",      data.get("alert",         False)))
        f.height        = int(data.get("altura",       1))
        f.balanceFactor = int(data.get("factorEquilibrio", 0))
        f.depth         = int(data.get("profundidad",  0))
        f.nodoCritico   = bool(data.get("nodoCritico", False))
        f.rentability   = float(data.get("rentabilidad", 0.0))
        return f
     
    def toDict(self) -> dict:
        """
        Serializes the flight to a dict using the Spanish keys
        expected by the project JSON format (Section 1.3).
        """
        return {
            "codigo":           self.code,
            "origen":           self.origin,
            "destino":          self.destination,
            "horaSalida":       self.departureTime,
            "precioBase":       self.basePrice,
            "precioFinal":      self.finalPrice,
            "pasajeros":        self.passengers,
            "prioridad":        self.priority,
            "promocion":        self.promotion,
            "alerta":           self.alert,
            "rentabilidad":     self.rentability,
            "altura":           self.height,
            "factorEquilibrio": self.balanceFactor,
            "nodoCritico":      self.nodoCritico,
            "profundidad":      self.depth,
        }
            
    def toJSON(self) -> str:
        return json.dumps(self.toDict(), ensure_ascii=False, indent=2)
    
    def toString(self) -> str:
        return (
            f"code: {self.code}\n"
            f"origin: {self.origin}\n"
            f"destination: {self.destination}\n"
            f"departureTime: {self.departureTime}\n"
            f"basePrice: {self.basePrice}\n"
            f"finalPrice: {self.finalPrice}\n"
            f"passengers: {self.passengers}\n"
            f"priority: {self.priority}\n"
            f"promotion: {self.promotion}\n"
            f"alert: {self.alert}\n"           
            f"nodoCritico: {self.nodoCritico}\n"
            f"rentability: {self.rentability}"
        )
        