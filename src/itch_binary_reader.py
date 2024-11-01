import struct
from tqdm import tqdm
from event import Event
from pathlib import Path
from order_book_builder import OrderBook

class Reader:
    """
    Reads binary data and passes decoded messages to the orderbook for handling

    Attributes:
        message_types {Dict} : defines the specific character format to unpack the binary content of each message
        book (OrderBook) : order book object that will handle all messages and update accordingly
    """
    def __init__(self):
        self.message_types = {'A': '>HH6sQsI8sI',
                              'C': '>HH6sQIQsI',
                              'D': '>HH6sQ',
                              'E': '>HH6sQIQ',
                              'F': '>HH6sQsI8sI4s',
                              'P': '>HH6sQsI8sIQ',
                              'Q': '>HH6sQ8sIQs',
                              'U': '>HH6sQQII',
                              'X': '>HH6sQI'}
        self.book = None
        
    def createBook(self, ticker, levels=1):
        """ Creates OrderBook object with defined ticker and levels for output """
        print('Creating {} Order Book'.format(ticker))
        self.book = OrderBook(ticker, levels)

    def readData(self, path, num_messages):
        """ Reads x number of binary messages from binary file """
        print('Processing {} messages'.format(num_messages))
        file_name = Path(path)
        with file_name.open('rb') as data:
            for i in tqdm(range(num_messages)):
                message_size = int.from_bytes(data.read(2), byteorder='big', signed=False)
                message_type = data.read(1).decode('ascii')
                message = data.read(message_size-2)

                output = struct.unpack(self.message_types[message_type], message)

                self.book.handleEvent(Event(message_type, output))

    def getOrderBook(self):
        """ Returns the order book object """
        return self.book