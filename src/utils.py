import numpy as np


class MathUtils:
    def __init__(self):
        pass

    def createColor(r, g, b):
        if (r <= 255 and g <= 255 and b <= 255):
            return [r / 255, g / 255, b / 255]
        else:
            raise Exception("Please input valid RGB values.")

    def Down():
        return np.array([0, -1.0, 0], dtype=np.float32)

    def __gaussian(self, x):
        return (x * x) + 0.5
        #return np.pow(np.e, -np.pow(x + 1, 2, dtype=np.float32), dtype=np.float32) + np.pow(np.e, -np.pow(x - 1, 2, dtype=np.float32), dtype=np.float32)

    def computeGaussianIntegral(self, lower, upper):
        lower_bound = self.__gaussian(lower)
        upper_bound = self.__gaussian(upper)

        rectangle = (np.min([upper_bound, lower_bound]) * (upper - lower))
        triangle = (np.abs(upper_bound - lower_bound) * (upper - lower) / 2)

        area = rectangle + triangle

        return int(area * 200)
    
class Node: 
    def __init__(self, key, value): 
        self.key = key 
        self.value = value 
        self.next = None

class HashTable: 
    def __init__(self, capacity): 
        self.capacity = capacity 
        self.size = 0
        self.table = [None] * capacity 

    def _hash(self, key): 
        return hash(key) % self.capacity 

    def insert(self, key, value): 
        index = self._hash(key) 

        if self.table[index] is None: 
            self.table[index] = Node(key, value) 
            self.size += 1
        else: 
            current = self.table[index] 
            while current: 
                if current.key == key: 
                    current.value = value 
                    return
                current = current.next
            new_node = Node(key, value) 
            new_node.next = self.table[index] 
            self.table[index] = new_node 
            self.size += 1

    def search(self, key): 
        index = self._hash(key) 

        current = self.table[index] 
        while current: 
            if current.key == key: 
                return current.value 
            current = current.next

        raise KeyError(key) 

    def remove(self, key): 
        index = self._hash(key) 

        previous = None
        current = self.table[index] 

        while current: 
            if current.key == key: 
                if previous: 
                    previous.next = current.next
                else: 
                    self.table[index] = current.next
                self.size -= 1
                return
            previous = current 
            current = current.next

        raise KeyError(key) 

    def __len__(self): 
        return self.size 

    def __contains__(self, key): 
        try: 
            self.search(key) 
            return True
        except KeyError: 
            return False