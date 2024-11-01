# NASDAQ_ITCH_Handler
This project reconstructs the order book for MSFT using NASDAQ ITCH Data

To begin we download ITCH sample data using methods borrowed from [Stefan Jansen]([https://github.com/PacktPublishing/Hands-On-Machine-Learning-for-Algorithmic-Trading/blob/master/Chapter02/01_NASDAQ_TotalView-ITCH_Order_Book/01_build_itch_order_book.ipynb](https://github.com/stefan-jansen/machine-learning-for-trading/blob/main/02_market_and_fundamental_data/01_NASDAQ_TotalView-ITCH_Order_Book/01_parse_itch_order_flow_messages.ipynb))

In order to get a single stock, in itch_msft_extract.ipynb we extract only Add Order, Modify Order, and Trade messages using the stock_locate attribute and repackage these messages into their own binary file.

We then read this binary and reconstruct the order book. 

This implementation processes ~ 25,000 messages per second.

My previous implementaiton processed ~1,000 messages per second and my LOBSTER implemenation processed ~200 messages per second.
