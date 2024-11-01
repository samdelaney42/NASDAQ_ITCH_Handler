
class Event:
    """
    super class of event objects - depending on event type, specific attributes are assigned at the subclass level

    Attributes:
        types (dict): contains each expected message type to build a specific event object
        type (str): message type
        record (TypeXYZ): reference to specific event object
    """
    def __init__(self, type, message):
        self.types = {"A":TypeA, "F":TypeF, "E":TypeE, "C":TypeC, "X":TypeX, "D":TypeD, "U":TypeU, "P":TypeP, "Q":TypeQ}
        self.type = type
        self.record = self.types[type](message)
    
class TypeA(Event):
    def __init__(self, data):
        """ Initializes Type A Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.order_reference_number: int = data[3]
        self.buy_sell_indicator: str = data[4] if type(data[4]) == str else data[4].decode('ascii')
        self.shares: int = data[5]
        self.stock: str = data[6] if type(data[6]) == str else data[6].decode('ascii').strip()
        self.price: int = data[7]
        self.attribution = "NSDQ"

class TypeF(Event):
    def __init__(self, data):
        """ Initializes Type F Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.order_reference_number: int = data[3]
        self.buy_sell_indicator: str = data[4] if type(data[4]) == str else data[4].decode('ascii')
        self.shares: int = data[5]
        self.stock: str = data[6] if type(data[6]) == str else data[6].decode('ascii').strip()
        self.price: int = data[7]
        self.attribution: str = data[8] if type(data[8]) == str else data[8].decode('ascii')

class TypeE(Event):
    def __init__(self, data):
        """ Initializes Type E Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.order_reference_number: int = data[3]
        self.executed_shares: int = data[4]
        self.match_number: int = data[5]

class TypeC(Event):
    def __init__(self, data):
        """ Initializes Type C Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.order_reference_number: int = data[3]
        self.executed_shares: int = data[4]
        self.match_number: int = data[5]
        self.printable: str = data[6].decode('ascii')
        self.execution_price: int = data[7]

class TypeX(Event):
    def __init__(self, data):
        """ Initializes Type X Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.order_reference_number: int = data[3]
        self.cancelled_shares: int = data[4]

class TypeD(Event):
    def __init__(self, data):
        """ Initializes Type D Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.order_reference_number: int = data[3]

class TypeU(Event):
    def __init__(self, data):
        """ Initializes Type U Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.original_order_reference_number: int = data[3]
        self.new_order_reference_number: int = data[4]
        self.shares: int = data[5] 
        self.price: int = data[6]

class TypeP(Event):
    def __init__(self, data):
        """ Initializes Type P Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.order_reference_number: int = data[3]
        self.buy_sell_indicator: str = data[4].decode('ascii')
        self.shares: int = data[5]
        self.stock: str = data[6].decode('ascii').strip()
        self.price: int = data[7]
        self.match_number: int = data[8]

class TypeQ(Event):
    def __init__(self, data):
        """ Initializes Type Q Event Object """
        self.stock_locate: int = data[0]
        self.tracking_number: int = data[1]
        self.timestamp: int = data[2]
        self.shares: int = data[3]
        self.stock: str = data[4].decode('ascii').strip()
        self.cross_price: int = data[5]
        self.match_number: int = data[6]
        self.cross_type: str = data[7].decode('ascii')