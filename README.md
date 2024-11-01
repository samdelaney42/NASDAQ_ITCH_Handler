# NASDAQ_ITCH_Handler
This project reconstructs the order book for a given stock using NASDAQ ITCH Data

To begin we download ITCH sample data using methods borrowed from [Stefan Jansen]([https://github.com/PacktPublishing/Hands-On-Machine-Learning-for-Algorithmic-Trading/blob/master/Chapter02/01_NASDAQ_TotalView-ITCH_Order_Book/01_build_itch_order_book.ipynb](https://github.com/stefan-jansen/machine-learning-for-trading/blob/main/02_market_and_fundamental_data/01_NASDAQ_TotalView-ITCH_Order_Book/01_parse_itch_order_flow_messages.ipynb)).

First, we read the full ITCH sample, extracting only the add order (A, F), modify order (E, C. X. U. D), and trade (P, Q) messages for the specified stock, then repackage these messages back into their own binary file

Then, we use itch_binary_reader to parse this binary data and reconstruct the order book for x number of messages.

The order book consists of 2 binary saech trees, one for each side, where each node is a price level.

Orders are stored in the order book object in a dict, keyed on order_reference_number

We also use a dictionary to store each active price in the bid and ask tree.

This way, we can ensure O(1) time to access to any limit when adding orders, executing, cancelling, or deleting orders at any pre-existing price level.

We then only have O(log(n)) time when addidng a new price limit or deleting a price limit.

This implementation processes ~ 23,000 messages per second.

![comparsion_1](https://github.com/samdelaney42/NASDAQ_ITCH_Handler/blob/main/data/images/v2_itch.png)

The previous implementation, found in 'archive', processed ~1,000 messages per second

![comparsion_2](https://github.com/samdelaney42/NASDAQ_ITCH_Handler/blob/main/data/images/v1_itch.png)

And my [LOBSTER](https://github.com/samdelaney42/L2_Order_Book_Handler) implemenation processed ~200 messages per second.

![comparsion_3](https://github.com/samdelaney42/NASDAQ_ITCH_Handler/blob/main/data/images/lob.png)
