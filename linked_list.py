class Node:
    def __init__(self, data = None, next_node = None):
        self.data = data
        self.next_node = next_node

#Note: linked list has better time complexity performance in comparison to regular list

class LinkedList:
    def __init__(self):
        self.head = None
        self.last_node = None
            
    def print_linked_list(self):
        ll_string = ''
        node = self.head
        if node is None:
            print(None)
        while node:
            ll_string += f"{str(node.data)} ->"
            node = node.next_node
        ll_string += " None"
        print(ll_string)
        
    def insert_head(self,data):
        if self.head is None: #check if the list is empty and is this is first entry. If true, head == tail
            self.head = Node(data, None)
            self.last_node = self.head 
        new_node = Node(data, self.head)
        self.head = new_node
 
    def insert_tail(self,data):
        if self.head is None:
           self.insert_head(data)
           return
        
        self.last_node.next_node = Node(data, None)
        self.last_node = self.last_node.next_node
                
    def to_list(self):
        l = []
        if self.head is None:
            return l
        node = self.head
        while node:
            l.append(node.data)
            node = node.next_node 
        return l               

    def get_user_by_id(self, user_id):
        node = self.head
        while node:
            if node.data['id'] is int(user_id):
                return node.data
            node = node.next_node
        return None