import pandas as pd
class Event:

	def __init__(self, data):
		self.tracking_number = data[0]
		self.time = data[1]
		self.order_reference_number = data[2]
		self.direction = data[3]
		self.shares = data[4]
		self.price = data[5]
		self.type = data[6]
		self.attribution = data[7]
		self.executed_shares = data[8]
		self.match_number = data[9]
		self.printable = data[10]
		self.execution_price = data[11]
		self.cancelled_shares = data[12]
		self.original_order_reference_number = data[13]
		self.new_order_reference_number = data[14]
		self.shares_replaced = data[15]
		self.price_replaced = data[16]
		self.cross_type = data[17]