import struct
import gzip
import shutil
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import urljoin

class StockSelector:
    """
    Loads full NASDAQ ITCH file then extracts and repackages binary data to a seperate file
    for a given stock. It only exports the Add order (A, F), Modify order (E, C, X, U, D), and
    Trade (P, Q) messages to binary, so all other system and stock related messages are excluded
    from the output.
    Once again, this based on code from Stefan Jansen's 01_parse_itch_order_flow_messages.ipynb

    Attributes:
        stock (str): stock you want to extract binary data for
        file_name (Path): path to full ITCH sample 
        message_tyoes {dict}: All ITCH message unpack formats
    """

    def __init__(self, stock):
        self.stock = stock
        self.file_name = self.may_be_download()
        self.message_types = {'A': '>HH6sQsI8sI',
                              'B': '>HH6sQ',
                              'C': '>HH6sQIQsI',
                              'D': '>HH6sQ',
                              'E': '>HH6sQIQ',
                              'F': '>HH6sQsI8sI4s',
                              'H': '>HH6s8sss4s',
                              'I': '>HH6sQQs8sIIIss',
                              'J': '>HH6s8sIIII',
                              'K': '>HH6s8sIsI',
                              'L': '>HH6s4s8ssss',
                              'P': '>HH6sQsI8sIQ',
                              'Q': '>HH6sQ8sIQs',
                              'R': '>HH6s8sssIss2ssssssIs',
                              'S': '>HH6ss',
                              'U': '>HH6sQQII',
                              'V': '>HH6sQQQ',
                              'W': '>HH6ss',
                              'X': '>HH6sQI',
                              'Y': '>HH6s8ss',
                              'h': '>HH6s8sss'}

    def may_be_download(self):
        """Download & unzip ITCH data if not yet available"""
        data_path = Path("../../../../Volumes/external_drive/nasdaq_itch/data")
        URL = "https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/"
        SOURCE_FILE = "12302019.NASDAQ_ITCH50.gz"
        url = urljoin(URL, SOURCE_FILE)
        if not data_path.exists():
            print('Creating directory')
            data_path.mkdir()
        else: 
            print('Directory exists')

        filename = data_path / url.split('/')[-1]        
        if not filename.exists():
            print('Downloading...', url)
            urlretrieve(url, filename)
        else: 
            print('File exists')        

        unzipped = data_path / (filename.stem + '.bin')
        if not unzipped.exists():
            print('Unzipping to', unzipped)
            with gzip.open(str(filename), 'rb') as f_in:
                with open(unzipped, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else: 
            print('File already unpacked')
        return unzipped
    
    def getBinary(self):
        """ get the binary file for specific stock """
        # check if stock binary already exists
        if Path("../data/{}.bin".format(self.stock)).is_file():
            print("{} binary file already exists".format(self.stock))
            return
        # create destination for output file
        output_file = "../data/{}.bin".format(self.stock)
        print("Creating binary file for {}".format(self.stock))
        # open and read ITCH sample
        with self.file_name.open('rb') as data, open(output_file, 'wb') as outfile:
            while True:
                # determine message size in bytes
                message_size = int.from_bytes(data.read(2), byteorder='big', signed=False)
                # get message type
                message_type = data.read(1).decode('ascii')  
                try:
                    # using the message size, read the relevant number of bytes
                    binary_stream = data.read(message_size - 1)
                    # check system events, break while loop if system event is type C
                    # "C" : End of Messages. This is always the last message sent in any trading day.
                    if message_type == "S":
                        s_message = struct.unpack(self.message_types[message_type], binary_stream)
                        if s_message[3].decode('ascii') == 'C':
                            break
                    # to get only self.stock events, first find the stock_locate attribute
                    elif message_type == "R":
                        r_message = struct.unpack(self.message_types[message_type], binary_stream)
                        # find self.stock
                        if r_message[3].decode('ascii').strip() == self.stock:
                            stock_locate = r_message[0]
                    # read all stock messages
                    elif message_type in ["A", "F", "E", "C", "X", "U", "D", "P", "Q"]:
                        message = struct.unpack(self.message_types[message_type], binary_stream)
                        # repackage all self.stock ones and save to their own file
                        if message[0] == stock_locate:
                            # get the binary format for the original message type
                            new_fmt = self.message_types[message_type]
                            # edit format so we can re-encode the message type again
                            # use > to ensure big-endian
                            new_fmt = new_fmt.strip(">")
                            repackaged = struct.pack(">c"+new_fmt, message_type.encode('ascii'), *message)
                            # check the length of the repackaged message
                            # add 1 becasue, we will also encode this length as an unsigned int to the front of the message
                            # this will ensure that we can decode the binary the same way that we decoded it above 
                            new_len = len(repackaged)+1
                            # repackage again, this time including the new length
                            repackaged_w_len = struct.pack(">Hc"+new_fmt, new_len, message_type.encode('ascii'), *message)
                            # add to the output file
                            outfile.write(repackaged_w_len)
                    else:
                        pass
                except Exception as e:
                    print(e)