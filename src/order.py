
class Order:
    """
    Represents an order object. Extracts relevant info from Event object

    Attributes:
        submission_time (datetime): time that an event is submitted
        order_reference_number (int): the order ID number
        buy_sell_indicator (int): indicates side of book (1 == bid, -1 == ask)
        price (float): price at submission
        shares (int): shares submitted
        attribution (str): submission entity (eg. broker or market maker) filled as NSDQ if None
    """
    def __init__(self, event):
        """ Initializes order object """
        self.submission_time = event.record.timestamp
        self.order_reference_number = event.record.order_reference_number
        self.buy_sell_indicator = event.record.buy_sell_indicator
        self.price = event.record.price
        self.shares = event.record.shares
        self.attribution = event.record.attribution

    def getOrderData(self):
        """
        Returns CURRENT STATE of order data. 
        e.g. If called following a partial execution, it will return the remaining shares for that order

        Args:
            None

        Returns:
            list [list]: containing ref number, price, num shares
        """
        return [self.order_reference_number, self.price, self.shares]
        
    def executeShares(self, executed_shares):
        """
        Verifys execution amount: check if the shares being executed are >= to remaining shares

        Args:
            executed_shares (int): num shares form event type E to be reduced from order total

        Returns:
            boolean (bool): True if >= 0, else False
        """
        if self.shares != 0:
            self.shares -= executed_shares
            if self.shares >= 0:
                return True
            else:
                return False
            
    def cancelShares(self, cancelled_shares):
        """
        Verifys cancellation amount: check if the shares being cancelled are >= to remaining shares

        Args:
            cancelled_shares (int): num shares form event type X to be reduced from order total

        Returns:
            boolean (bool): True if >= 0, else False
        """
        if self.shares != 0:
            self.shares -= cancelled_shares
            if self.shares >= 0:
                return True
            else:
                return False
            
