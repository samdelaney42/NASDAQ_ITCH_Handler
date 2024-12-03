import pandas as pd
from datetime import datetime, timedelta

from book_tree import BookLimits
from order import Order
from event import Event

class OrderBook:
    """
    Order Book object - this saves the time series states of the orderbook
    it handles each incoming event and modifies the book accordingly

    Attributes:
        bid (BookLimit): BST of bids
        ask (BookLimit): BST of asks
        stock (str): stock name
        orders (dict): Dictionary of order objects keyed on order_reference_number
        open (event): ref to opening cross
        close (event): ref to closing cross
        sequence_number (int): increments with each event handeled
        book_snapshot (list): list of best bid/ask, time, event type, recorded after each handled event
        time_sales (list): list of printable executions
    """

    def __init__(self, stock, levels=1):
        """ Initializes the order book variables """
        # Hard code date for example purpose
        self.date = datetime.strptime("12302019", "%m%d%Y") 
        self.bid = BookLimits(side=1)
        self.ask = BookLimits(side=-1)
        self.stock = stock
        self.levels = levels
        self.orders = {}
        self.open = None
        self.close = None
        self.sequence_number = 0
        self.book_snapshot = []
        self.time_sales = []

    def handleEvent(self, event):
        """
        Primary handler to sort each incoming event. Matches incoming event type to dict of helpers

        Args:
            Event (Event): any incoming event
        
        Returns:
            None

        Raises:
            ValueError: event type doesnt exist
        """
        group_handlers = {"A" : self.addOrder,
                          "F" : self.addOrder,
                          "E" : self.modifyOrder,
                          "C" : self.modifyOrder,
                          "X" : self.modifyOrder,
                          "D" : self.modifyOrder,
                          "U" : self.modifyOrder,
                          "P" : self.tradeOrder,
                          "Q" : self.tradeOrder}

        # get the required handler given the event type
        handler = group_handlers.get(event.type)
        if handler:
            handler(event)
        else:
            raise ValueError("Event type {} does not exist".format(event.type))

        # increment the sequence number and save a snapshot of the book
        self.sequence_number += 1
        self.book_snapshot.append([self.bid.maxValueLimit(), self.ask.minValueLimit(), event.record.timestamp, event.type])

    def addOrder(self, event):
        """
        Adds a new order to the book

        Args:
            Event (event): new event to handle

        Returns:
            None
        """
        self._add(event)

    def _add(self, event):
        """
        Add order helper method. Creates the new order obj and save it to dict, then passes it to relevant side

        Args:
            Event (event): new event

        Returns:
            None
        """
        # create new order obj and add to dict
        new_order = Order(event)
        self.orders[new_order.order_reference_number] = new_order
        # pass to releveant side of book
        if new_order.buy_sell_indicator == "B":
            self.bid.addOrder(new_order)
        else:
            self.ask.addOrder(new_order)

    def modifyOrder(self, event):
        """
        Modifies an existing order in the book

        Args:
            Event (event): new event

        Returns:
            None

        Raises:
            ValueError: event type doesnt exist
        """
        # handler dict for each event type
        modify_handlers = {"E" : self._execute,
                           "C" : self._executeWithPrice,
                           "X" : self._cancel,
                           "D" : self._delete,
                           "U" : self._replace}
        
        # check event type exists and handle accordingly
        modify_handler = modify_handlers.get(event.type)
        if modify_handler:
            modify_handler(event)
        else:
            raise ValueError("Event type {} does not exist".format(event.type))

    def _execute(self, event, printable=True):
        """
        Execution helper method, handles event type E

        Args:
            event (Event): new event to handle
            printable (bool): handles if we can add to time and sales record 

        Returns:
            None

        Raises:
            ValueError: Order doesnt exist
        """
        # get executed shares from event
        executed_shares = event.record.executed_shares
        # pull the order from the dict
        order_to_execute = self.orders.get(event.record.order_reference_number)
        # if order exists, handle on relevant side of book
        if order_to_execute is not None:
            if order_to_execute.buy_sell_indicator == "B":
                self.bid.executeOrder(order_to_execute, executed_shares)
            else:
                self.ask.executeOrder(order_to_execute, executed_shares)
            # add to time and sales if printable
            if printable==True:
                if event.type == 'C':
                    self.time_sales.append([event.record.execution_price, executed_shares, order_to_execute.buy_sell_indicator, event.record.timestamp])
                else:
                    self.time_sales.append([order_to_execute.price, executed_shares, order_to_execute.buy_sell_indicator, event.record.timestamp])
        else:
            #self.logger.info("Order {} does not exist".format(event.order_reference_number))
            raise ValueError("Order {} does not exist".format(event.record.order_reference_number))

    def _executeWithPrice(self, event):
        """
        Execution with price helper method, handles event type C
        Here, it can either be printable or not so handle whether or not to record to time and sales
        then send back to regular execution handler above

        Args:
            event (Event): new event to handle

        Returns:
            None

        Raises:
            ValueError: Order doesnt exist
        """
        if event.record.printable == "Y":
            self._execute(event, printable=True) 
            ### add to time and sales
        else:
            self._execute(event, printable=False)
            ### don't add to time and sales

    def _cancel(self, event):
        """
        Cancellation helper method, handles event type X

        Args:
            event (Event): new event to handle

        Returns:
            None

        Raises:
            ValueError: Order doesnt exist
        """
        # get shares to cancel from event
        cancelled_shares = event.record.cancelled_shares
        # pull the order from the dict
        order_to_cancel = self.orders.get(event.record.order_reference_number)
        # if order exists, handle on relevant side of the book
        if order_to_cancel is not None:
            if order_to_cancel.buy_sell_indicator == "B":
                self.bid.cancelOrder(order_to_cancel, cancelled_shares)
            else:
                self.ask.cancelOrder(order_to_cancel, cancelled_shares)
        else:
            #self.logger.info("Order {} does not exist".format(event.order_reference_number))
            raise ValueError("Order {} does not exist".format(event.record.order_reference_number))

    def _delete(self, event):
        """
        Deletion helper method, handles event type D

        Args:
            event (Event): new event to handle

        Returns:
            None

        Raises:
            ValueError: Order doesnt exist
        """
        # pull order from the dict
        order_to_delete = self.orders.get(event.record.order_reference_number)
        # if order exists, handle on relevant side of the book
        if order_to_delete is not None:
            remaining_shares = order_to_delete.shares
            if order_to_delete.buy_sell_indicator == "B":
                self.bid.deleteOrder(order_to_delete, remaining_shares)
            else:
                self.ask.deleteOrder(order_to_delete, remaining_shares)
        else:
            #self.logger.info("Order {} does not exist".format(event.order_reference_number))
            raise ValueError("Order {} does not exist".format(event.record.order_reference_number))

    def _replace(self, event):
        """
        Replacement helper method, handles event type U
        Data for Type U can be interesting - sometimes all feilds are provided per the documentation
        other times, only original and new IDs are provided

        Args:
            event (Event): new event to handle

        Returns:
            None

        Raises:
            ValueError: Order doesnt exist
        """
        # pull existing order from dict
        order_to_repalce = self.orders.get(event.record.original_order_reference_number)
        if order_to_repalce is not None:
            # save the new order info
            # called potential becasue sometimes it can be NaN (or 0 as we fill in the event object)
            potential_new_price = order_to_repalce.price
            potential_new_shares = order_to_repalce.shares
            potential_new_buy_sell = order_to_repalce.buy_sell_indicator
            
            # check if new values actually exist in the event, fill with those
            # otherwise, fill with values from the original order
            if event.record.price == 0.0:
                temp_price = potential_new_price
            else:
                temp_price = event.record.price
            if event.record.shares == 0:
                temp_shares = potential_new_shares
            else:
                temp_shares = event.record.shares

            if order_to_repalce.attribution != "NSDQ":
                replacement_order_event = Event("F", [event.record.stock_locate,
                                                      event.record.tracking_number,
                                                      event.record.timestamp,
                                                      event.record.new_order_reference_number,
                                                      order_to_repalce.buy_sell_indicator,
                                                      temp_shares,
                                                      self.stock,
                                                      temp_price,
                                                      order_to_repalce.attribution,])
            else:
                replacement_order_event = Event("A", [event.record.stock_locate,
                                                      event.record.tracking_number,
                                                      event.record.timestamp,
                                                      event.record.new_order_reference_number,
                                                      order_to_repalce.buy_sell_indicator,
                                                      temp_shares,
                                                      self.stock,
                                                      temp_price])
            # add this new order
            self.addOrder(replacement_order_event)
            delete_original_order_event = Event("D", [event.record.stock_locate,
                                                      event.record.tracking_number,
                                                      event.record.timestamp,
                                                      order_to_repalce.order_reference_number])
            self._delete(delete_original_order_event)
        else:
            #self.logger.info("Order {} does not exist".format(event.order_reference_number))
            raise ValueError("Order {} does not exist".format(event.record.order_reference_number))

    def tradeOrder(self, event):
        """
        Handles non-displayable order types

        Args:
            event (Event): event to handle

        Returns:
            None
        """
        if event.type == "P":
            self.time_sales.append([event.record.price, event.record.shares, event.record.buy_sell_indicator, event.record.timestamp])
        else:
            if event.record.cross_type == 0.0:
                self.open = event
            else:
                self.close = event

############################## format methods
                
    def formatBook(self, start_from):
        """ converts book snapshots to clean DF of orderbook over time """
        bid = [x[0] for x in self.book_snapshot[start_from:]]
        ask = [x[1] for x in self.book_snapshot[start_from:]]
        time = [x[2] for x in self.book_snapshot[start_from:]]
        event = [x[3] for x in self.book_snapshot[start_from:]]

        bid_price = [x[0][0]/10_000 for x in bid]
        ask_price = [x[0][0]/10_000 for x in ask]

        bid_volume = [x[0][1] for x in bid]
        ask_volume = [x[0][1] for x in ask]

        bid_orders = [x[0][2] for x in bid]
        ask_orders = [x[0][2] for x in ask]

        decoded_time = self.getTime(time)

        formatted_book = pd.DataFrame({"Bid_1":bid_price, 
                                       "Ask_1":ask_price,
                                       "Bid_1_Vol":bid_volume, 
                                       "Ask_1_Vol":ask_volume,
                                       "Bid_1_Ord":bid_orders, 
                                       "Ask_1_Ord":ask_orders,
                                       "Time":decoded_time})
        
        return formatted_book
    
    def getTime(self, time):
        """ Converts binary time to time stamps """
        integer_time = [int.from_bytes(x, byteorder='big', signed=False) for x in time]
        timestamps = [self._decodeTime(x) for x in integer_time]
        return timestamps
    
    def _decodeTime(self, time_stamp):
        """ Converst nanoseconds from midnight into full time stamps """
        nanoseconds_since_midnight = time_stamp
        nanoseconds_per_second = 1_000_000_000
        seconds = nanoseconds_since_midnight // nanoseconds_per_second
        remaining_nanoseconds = nanoseconds_since_midnight % nanoseconds_per_second
        delta = timedelta(seconds=seconds, microseconds=remaining_nanoseconds / 1000)
        event_time = self.date + delta
        return event_time
    
    def formatTimeSales(self, start_from):
        
        buy = [x for x in self.time_sales[start_from:] if x[2] == 1] 
        sell = [x for x in self.time_sales[start_from:] if x[2] == -1]

        formatted_buys = pd.DataFrame(buy, columns=["Price", "Shares", "Side", "Time"])
        formatted_sells = pd.DataFrame(sell, columns=["Price", "Shares", "Side", "Time"])

        return formatted_buys, formatted_sells