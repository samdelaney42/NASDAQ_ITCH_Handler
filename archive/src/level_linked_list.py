# this is a doubly linked list class
# when instantiated, each linked list object will reflect a string of orders
# at a given level in the order book
# here we use the Order class as the node itself

from order_obj import Order
import log

class LinkedList:
	"""
	Represents a doubly linked list of orders.

	Attributes:
		head (Order): The first order in the linked list.
		tail (Order): The last order in the linked list.
	"""

	def __init__(self):
		"""Initializes a new instance of LinkedList."""
		#self.logger = log.get_logger('Level Linked List')

		self.head = None
		self.tail = None

	def addOrder(self, new_order):
		"""
		Adds a new order to the linked list.

		Args:
			new_order (Order): The order to be added.
		"""
		if self.head is None:
			self.head = new_order
			self.tail = new_order
			#self.logger.info("${} limit created, ID: {} is head".format(new_order.price, new_order.id))
			return self
		else:
			self.tail.next = new_order
			new_order.prev = self.tail
			self.tail = new_order
			#self.logger.info("${} has added ID {} to the back of the queue".format(new_order.price, new_order.id))
			return self
  
	def deleteOrder(self, order_to_delete):
		"""
		Deletes an order from the linked list.

		Args:
			order_to_delete (Order): The order to be deleted.
		"""
		if self.head is None or order_to_delete is None:
			return
		
		if self.head.id == order_to_delete.id:
			self.head = order_to_delete.next

		if order_to_delete.next is not None:
			order_to_delete.next.prev = order_to_delete.prev

		if order_to_delete.prev is not None:
			order_to_delete.prev.next = order_to_delete.next
		
		#self.logger.info("Order {} deleted from ${} queue".format(order_to_delete.id, order_to_delete.price))
		return

	# def deleteOrder(self, order_to_delete):
	# 	if self.head is None or order_to_delete is None:
	# 		return
		
	# 	# If order to delete is the head
	# 	if self.head.id == order_to_delete.id:
	# 		self.head = order_to_delete.next
	# 		if self.head is not None:
	# 			self.head.prev = None
	# 		else:
	# 			self.tail = None  # List is now empty

	# 	# If order to delete is the tail
	# 	if self.tail.id == order_to_delete.id:
	# 		self.tail = order_to_delete.prev
	# 		if self.tail is not None:
	# 			self.tail.next = None
	# 		else:
	# 			self.head = None  # List is now empty

	# 	# If the order is somewhere in the middle
	# 	if order_to_delete.next is not None:
	# 		order_to_delete.next.prev = order_to_delete.prev
	# 	if order_to_delete.prev is not None:
	# 		order_to_delete.prev.next = order_to_delete.next


	def getOrderqueue(self):
		"""
		Itterates through the order queue and appends data to a list

		Returns:
			List of orders
		"""
		orders = []
		if self.head is None:
			return
		elif self.head.next is None:
			return [self.head.id, self.head.price, self.head.shares]
		else:
			self.temp = self.head
			while self.temp is not None:
				orders.append([self.temp.id, self.temp.price, self.temp.shares])
				self.temp = self.temp.next
			return orders


