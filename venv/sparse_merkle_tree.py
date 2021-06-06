import hashlib, sys


class Node:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.start = None
        self.end = None
        self.level = None
        self.value = value
        self.parent = None
        self.hashValue = hashlib.sha256(value.encode('utf-8')).hexdigest()
    def set_value(self, value):
        self.value = value
        self.hashValue = self.getHashValue(value)

    def getHashValue(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

class Merkle_Tree:
    def __init__(self):
        self.leaves_on = []
        self.root = None
        self.max = self.hex_to_int("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
        ##self.max = self.hex_to_int("f")



    def create_tree(self):
        ##l = self.getHashValue("0")
        l = "0"
        s = "0 256\n"
        for i in range (256):
            l = self.getHashValue(l + l)
            index =str(255 - i)
            s = s + l +" " + index +"\n"
        root = Node(l)
        root.start = 0
        root.end = self.max
        root.level = 0

        self.root = root;


    def change_path(self, leave):
        temp = leave
        check = self.getHashValue("0")
        default_level = "0"
        while temp.parent is not None:
            p = temp.parent
            c = self.getHashValue(default_level)
            if p.left is temp:
                if p.right is None or p.right.value is default_level:
                    p.set_value(self.getHashValue(p.left.value + default_level))
                else:
                    p.set_value(p.left.value + p.right.value)
            elif p.right is temp:
                if p.left is None or p.left.value is default_level:
                    p.set_value(default_level + p.right.value)
                else:
                    p.set_value(p.left.value + p.right.value)
            check = self.getHashValue(check + check)
            temp = temp.parent
            ##pppp = "0"
            ##if (self.root.value != "60803f6b16c86ae695b1d62d6f3693e658a3278a656d698382c92bad8bfb14cf"):
            ##    pppp = self.getHashValue(p.hashValue + p.hashValue)
            ##if (p.value == "60803f6b16c86ae695b1d62d6f3693e658a3278a656d698382c92bad8bfb14cf"):
            ##    x = 5
            default_level = self.getHashValue(default_level+default_level)

    def find_leave(self, leave):
        val = self.hex_to_int(leave)
        self.leaves_on.append(self.hex_to_int(leave))
        self.leaves_on.sort()
        start = int(0)
        end = int (self.max)
        temp = self.root
        while (temp.end > temp.start):
            half = int((temp.end - temp.start) // 2)
            half = int(temp.start + half)
            if val <= half:
                if temp.left is None:
                    temp.left = Node("None")
                    temp.left.level = temp.level+1
                    temp.left.start = temp.start
                    temp.left.end = half
                    temp.left.parent = temp
                temp = temp.left
            else:
                if temp.right is None:
                    temp.right = Node("None")
                    temp.right.level = temp.level+1
                    temp.right.start = half+1
                    temp.right.end = temp.end
                    temp.right.parent = temp
                temp = temp.right
        temp.set_value("0")
        return temp

    def add_leave(self, leave):
        leave_p = self.find_leave(leave)
        leave_p.set_value("1")
        self.change_path(leave_p)


    def getRoot(self):
        return self.root.value

    def getProof(self, leave):
        leave_p = self.find_leave(leave)
        self.change_path(leave_p)
        default_level = "0"

        result = self.root.value
        B = ""

        node = leave_p
        p = node.parent
        while p is not None:
            if p.left is node:
                if p.right is None:
                    B = B + " " + self.getHashValue(default_level)
                else:
                    B = B + " " + p.right.hashValue
            else:
                if p.left is None:
                    B = B + " " + self.getHashValue(default_level)
                else:
                    B = B + " " + p.left.hashValue
            node = p
            p = p.parent
            result = result + " " + B
            default_level = self.getHashValue(default_level + default_level)

        return result

    def merge_string(self, arri,  string):
        if arri[0] == '0':
            return self.getHashValue(arri[1:] + string)
        elif arri[0] == '1':
            return self.getHashValue(string + arri[1:])

    def check_inclusion(self, value, hash):
        arr_hash = hash.split()
        hash_node = self.getHashValue(value)
        p_calc = self.merge_string(arr_hash[1], hash_node)
        for i in range(2, len(arr_hash)):
            hash_node = p_calc
            p_calc = self.merge_string(arr_hash[i], hash_node)
        if p_calc == arr_hash[0]:
            return True
        else:
            return False

    def getHashValue(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def hex_to_int(self, string_h):
        return int(string_h, 16)




        #node = Node(leave)
        #self.leaves.append(node)
        #self.create_tree()

def main():
        mt = Merkle_Tree()
        mt.create_tree()
        root1 = mt.getRoot()
        proof1 = mt.getProof("0000000000000000000000000000000000000000000000000000000000000000")
        mt.add_leave("0000000000000000000000000000000000000000000000000000000000000000")
        root2 = mt.getRoot()
        proof2 = mt.getProof("0000000000000000000000000000000000000000000000000000000000000001")
        proof3 = mt.getProof("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")

        #mt.add_leave("0000000000000000000000000000000000000000000000000000000000010000")
        mt.add_leave("0000000000000000000000000000000000000000000000000000000000000001")
        mt.add_leave("1000000000000000000000000000000000000000000000000000000000000011")
        h1 = mt.getHashValue("0")
        h2 = mt.getHashValue(h1 + h1)
        x = 3





if __name__ == "__main__":
        main()
