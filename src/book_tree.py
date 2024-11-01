import copy

class Limit:
    """
    Limit object is a node that existis within the BST of each side of the book

    Attributes:
        limit_price (float): price level
        total_volume (int): total number of shares from orders at this price level
        num_orders (int): total number of orders at this price level
        left : reference to left child
        right : reference to right child
        parent : reference to parent
    """

    def __init__(self, first_order):
        """ Initaliszes Limit Node """
        self.limit_price = copy.deepcopy(first_order.price)
        self.total_volume = copy.deepcopy(first_order.shares)
        self.num_orders = 1

        self.left = None
        self.right = None
        self.parent = None

    def getLimitVals(self):
        """
        Get key limit node info

        Args:
            None
        
        Returns:
            list [list]: price, volume, orders
        """
        return [self.limit_price, self.total_volume, self.num_orders]

class BookLimits:
    """
    This is the binary search tree made up of nodes that are limit objects

    Attriburtues:
        root (limit): root of tree, will be the first added limit
        limit_dict (dict): dict of limits in tree - allows for O(1) access
        side (int): == 1 for bid == -1 for ask
        best (float): current best price in BST
    """

    def __init__(self, side):
        """ Initializes BST """
        self.root = None
        self.limit_dict = {}
        self.side = side
        self.best = None
        
    def addOrder(self, order):
        """
        Adds an order to the BST

        Args:
            order (order): order object to add to tree

        Returns:
            None
        """
        # find the limit in the dict based on the order price
        target_limit = self.limit_dict.get(order.price)
        # if limit doesn't exist, create a new one otherwise add order to existing one
        if target_limit is None:
            self.addLimit(order)
        else:
            self.addOrderHelper(target_limit, order)
                
    def executeOrder(self, order, executed_shares):
        """
        Executes existing order in BST

        Args:
            Order (order): order object to execute shares
            executed_shares (int): number of shares to execute from Event

        Returns:
            None
        """
        # find the limit in the dict based on the order price
        target_limit = self.limit_dict.get(order.price)
        # if the limit exists, execute
        if target_limit is None:
            return None
        else:
            self.executeOrderHelper(order, target_limit, executed_shares)

    def cancelOrder(self, order, cancelled_shares):
        """
        Cancels existing order in BST

        Args:
            Order (order): order object to execute shares
            cancelled_shares (int): number of shares to cancel from Event

        Returns:
            None
        """
        # find the limit in the dict based on the order price
        target_limit = self.limit_dict.get(order.price)
        # if the limit exists, cancel shares
        if target_limit is None:
            return None
        else:
            self.cancelOrderHelper(order, target_limit, cancelled_shares)

    def deleteOrder(self, order, remaining_shares):
        """
        Deletes existing order in BST

        Args:
            Order (order): order object to execute shares
            remaining_shares (int): number of shares remaining in order from order object

        Returns:
            None
        """
        # find the limit in the dict based on the order price
        target_limit = self.limit_dict.get(order.price)
        # if the limit exists, delete order
        if target_limit is None:
            return None
        else:
            self.deleteOrderHelper(target_limit, remaining_shares)

################################ helper methods

    def addOrderHelper(self, target_limit, order):
        """
        Helper increments values at given limit based on addition

        Args:
            target_limit (limit): node at which we weill edit value
            order (order): order to add (sepcifically using shares supplied to increase vol)

        Returns:
            None
        """
        self._increaseVolumeAtLimit(target_limit, order.shares)
        self._increaseOrderAtLimit(target_limit)
        
    def executeOrderHelper(self, order, target_limit, executed_shares):
        """
        Helper increments values at given limit based on execution 

        Args:
            order (order): order that we are executing
            target_limit (limit): limit object that we will edit values
            executed_shares (int): num shares to reduce 

        Returns:
            None

        Raises:
            ValueError: somehow we are trying to ex more shares than exists
        """
        # perfrom ex check to make sure shares at order are >= 0 otherwise something has gone wrong!
        ex_check = order.executeShares(executed_shares)
        if ex_check is True:
            # make sure there are shares left to execute, if so reduce by executed amount 
            if target_limit.total_volume != 0:
                self._decreaseVolumeAtLimit(target_limit, executed_shares)
            # if we execute all the shares in an order, we also decrement the num orders
            if order.shares == 0:
                self._decreaseOrdersAtLimit(target_limit)
            # if both shares and orders are 0, the limit is empty and we can delete it
            if (target_limit.total_volume == 0) & (target_limit.num_orders == 0):
                self.deleteLimit(target_limit)
        else:
            raise ValueError("Execution amount {} incorrect".format(executed_shares))

    def cancelOrderHelper(self, order, target_limit, cancelled_shares):
        """
        Helper increments values at given limit based on cancellation 

        Args:
            order (order): order that we are cancelling
            target_limit (limit): limit object that we will edit values
            cancelled_shares (int): num shares to reduce 

        Returns:
            None

        Raises:
            ValueError: somehow we are trying to cancel more shares than exists
        """
        # perfrom cancel check to make sure shares at order are >= 0 otherwise something has gone wrong!
        can_check = order.cancelShares(cancelled_shares)
        if can_check is True:
            # make sure there are shares left to cancel, if so reduce by executed amount
            if target_limit.total_volume != 0:
                self._decreaseVolumeAtLimit(target_limit, cancelled_shares)
            # if we execute all the shares in an order, we also decrement the num orders
            if order.shares == 0:
                self._decreaseOrdersAtLimit(target_limit)
        else:
            raise ValueError("Cancellation amount {} incorrect".format(cancelled_shares))

    def deleteOrderHelper(self, target_limit, remaining_shares):
        """
        Helper increments values at given limit based on deletion 

        Args:
            target_limit (limit): limit object that we will edit values
            remaining_shares (int): num shares to reduce 

        Returns:
            None

        Raises:
            ValueError: somehow we are trying to cancel more shares than exists
        """
        # reduce shares and orders at the target limit
        self._decreaseVolumeAtLimit(target_limit, remaining_shares)
        self._decreaseOrdersAtLimit(target_limit)
        # if both shares and orders are 0, the limit is empty and we can delete it
        if (target_limit.total_volume == 0) & (target_limit.num_orders == 0):
            self.deleteLimit(target_limit)

################################ Private incrementaion methods

    def _increaseVolumeAtLimit(self, target_limit, new_shares):
        """ increases shares at limit by new_shares abount """
        target_limit.total_volume += new_shares

    def _increaseOrderAtLimit(self, target_limit):
        """ increases num orders at limit by 1 """
        target_limit.num_orders += 1

    def _decreaseVolumeAtLimit(self, target_limit, shares):
        """ decreases shares at limit by new_shares abount """
        target_limit.total_volume -= shares

    def _decreaseOrdersAtLimit(self, target_limit):
        """ decreases num orders at limit by 1 """
        target_limit.num_orders -= 1

################################ Tree Edit Methods

    def addLimit(self, first_order):
        """
        Adds a new limit node to the tree

        Args:
            first_order (order): first order at the new limit price to add

        Returns:
            None
        """
        # if the tree doesn't exist, make the root the new limit, otherwise add a new one
        # define the new best price and add the limit to the dict
        if self.root is None:
            self.root = Limit(first_order)
            self.best = self.root
            self.limit_dict[self.root.limit_price] = self.root
        else:
            self._addLimit(self.root, first_order)
            self.updateBest()

    def _addLimit(self, current_limit, first_order):
        """
        Recursivley adds a new limit node given root exists

        Args:
            current_limit (limit): current node passed in recursion
            first_order (order): first order to add to the new limit
        """

        # traverse tree and add node appropriately
        if first_order.price < current_limit.limit_price:
            if current_limit.left is None:
                new_limit = Limit(first_order)
                new_limit.parent = current_limit
                current_limit.left = new_limit
                self.limit_dict[new_limit.limit_price] = new_limit
            else:
                self._addLimit(current_limit.left, first_order)

        if first_order.price > current_limit.limit_price:
            if current_limit.right is None:
                new_limit = Limit(first_order)
                new_limit.parent = current_limit
                current_limit.right = new_limit
                self.limit_dict[new_limit.limit_price] = new_limit
            else:
                self._addLimit(current_limit.right, first_order)



    def deleteLimit(self, target_limit):
        """
        Deletes a node from the bst

        Args:
            target_limit (limit): the node we want to delete

        Returns:
            None
        """
        
        # delete the limit from the dict 
        temp = target_limit
        del self.limit_dict[temp.limit_price]
        self._deleteLimit(self.root, target_limit.limit_price)
        self.updateBest()


    def _deleteLimit(self, current_node, price_to_delete):
        """
        Recursivley deletes a limit node given specified limit

        Args:
            Current_node (limit): current node passed in recursion
            price_to_delete (float): target deletion price
        """
        if current_node is None:
            return None
        # navigate to target node
        if price_to_delete < current_node.limit_price:
            current_node.left = self._deleteLimit(current_node.left, price_to_delete)
        elif price_to_delete > current_node.limit_price:
            current_node.right = self._deleteLimit(current_node.right, price_to_delete)
        else:
            # case 1: target node has no children
            if current_node.left is None and current_node.right is None:
                return None
            
            # case 2: target node has left or right child
            if current_node.left is None:
                return current_node.right
            elif current_node.right is None:
                return current_node.left
            
            # case 3: target node has left and right child
            else:
                # find in order sucessor
                tmp = current_node.right
                while tmp.left is not None:
                    tmp = tmp.left
                
                # replace successor variables
                current_node.limit_price = tmp.limit_price
                current_node.total_volume = tmp.total_volume
                current_node.num_orders = tmp.num_orders

                # updated limit dict reference
                self.limit_dict[current_node.limit_price] = current_node

                # recursively transfer remaining sucessors
                current_node.right = self._deleteLimit(current_node.right, current_node.limit_price)

        return current_node

################################ Traversal Methods
        
    def updateBest(self):
        """ finds the best price in a tree """
        keys = self.limit_dict.keys()
        if self.side == 1 and keys:
            self.best = self.limit_dict.get(max(keys))
            return [[self.best.limit_price, self.best.total_volume, self.best.num_orders]]
        elif self.side == -1 and keys:
            self.best = self.limit_dict.get(min(keys))
            return [[self.best.limit_price, self.best.total_volume, self.best.num_orders]]
        else:
            return
        
    def maxValueLimit(self):
        if self.root is not None:
            return self._maxValueLimit(self.root)
        else:
            return None

    def _maxValueLimit(self, current_limit):
        """ finds largest value in tree """
        tmp = current_limit
        while tmp.right is not None:
            tmp = tmp.right
        return [[tmp.limit_price, tmp.total_volume, tmp.num_orders]]
    
    def minValueLimit(self):
        if self.root is not None:
            return self._minValueLimit(self.root)
        else:
            return None
    
    def _minValueLimit(self, current_limit):
        """ finds smallest value in tree """
        tmp = current_limit
        while tmp.left is not None:
            tmp = tmp.left
        return [[tmp.limit_price, tmp.total_volume, tmp.num_orders]]
    
    def getLimit(self, price):
        """ returns a specificd limit by in-order traversal """
        if self.root is not None:
            return self._getLimit(self.root, price)
        else:
            return None
    
    def _getLimit(self, current_limit, price):
        if (price < current_limit.limit_price) & (current_limit.left is not None):
            return self._getLimit(current_limit.left, price)
        if price == current_limit.limit_price:
            return current_limit
        if (price > current_limit.limit_price) & (current_limit.right is not None):
            return self._getLimit(current_limit.right, price)
        else:
            return None

    def inOrderTraversal(self):
        """ returns all vlaues in tree by in-order traversal """
        if self.root is not None:
            return self._inOrderTraversal(self.root)
        else:
            return None
        
    def _inOrderTraversal(self, current_node):
        elements = []
        if current_node.left is not None:
            elements.extend(self._inOrderTraversal(current_node.left))
        if current_node.num_orders >= 0:
            elements.append([current_node.limit_price, current_node.total_volume, current_node.num_orders])
        if current_node.right is not None:
            elements.extend(self._inOrderTraversal(current_node.right))
        return elements
    

    def inOrderTraversalMax(self, max_levels):
        """ returns first X values (ascending) in tree by in-order traversal (for ask side) """
        if self.root is not None:
            return self._inOrderTraversalMax(self.root, max_levels)
        else:
            return None
        
    def _inOrderTraversalMax(self, current_node, max_levels, current_i=None):
        elements = []

        if current_i is None:
            current_i = [0]

        if current_node.left is not None and current_i[0] < max_levels:
            elements.extend(self._inOrderTraversalMax(current_node.left, max_levels, current_i))
        if current_i[0] < max_levels:
            elements.append([current_node.limit_price, current_node.total_volume, current_node.num_orders])
            current_i[0] += 1
        if current_node.right is not None and current_i[0] < max_levels:
            elements.extend(self._inOrderTraversalMax(current_node.right, max_levels, current_i))
        return elements

    def inOrderReversalMax(self, max_levels):
        """ returns first X values (decending) in tree by in-order traversal (for bid side) """
        if self.root is not None:
            return self._inOrderReversalMax(self.root, max_levels)
        else:
            return None
        
    def _inOrderReversalMax(self, current_node, max_levels, current_i=None):
        elements = []

        if current_i is None:
            current_i = [0]

        if current_node.right is not None and current_i[0] < max_levels:
            elements.extend(self._inOrderReversalMax(current_node.right, max_levels, current_i))
        if current_i[0] < max_levels:
            elements.append([current_node.limit_price, current_node.total_volume, current_node.num_orders])
            current_i[0] += 1
        if current_node.left is not None and current_i[0] < max_levels:
            elements.extend(self._inOrderReversalMax(current_node.left, max_levels, current_i))
        return elements
        


