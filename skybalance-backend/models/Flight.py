import json
class Flight:
    def __init__(self):
        self.code : str
        self.origin : str
        self.destination :str
        self.departureTime : str 
        self.basePrice : float
        self.finalPrice : float
        self.passengers : int
        self.priority:int
        self.promotion : bool
        self.alert : bool
        
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
    
    def toJSON(self):
        data={
        "code":self.get_code(),
        "origin":self.get_origin(),
        "destination":self.get_destination(),
        "departureTime":self.get_departure_time(),
        "basePrice":self.get_base_price(),
        "finalPrice":self.get_final_price(),
        "passengers":self.get_passengers(),
        "priority":self.get_priority(),
        "promotion":self.get_promotion(),
        "alert":self.alert()
        }
        return json.dump(data)
    def toString(self):
        data=(f"code: {self.get_code()} \n"
              f"origin: {self.get_origin()} \n"
              f"destination: {self.get_destination()} \n"
              f"departureTime: {self.get_departure_time()} \n"
              f"basePrice: {self.get_base_price()} \n"
              f"finalPrice: {self.get_final_price()} \n"
              f"passengers: {self.get_passengers()} \n"
              f"priority: {self.get_priority()} \n"
              f"promotion: {self.get_promotion()} \n"
              f"alert: {self.get_alert()}")
        return data