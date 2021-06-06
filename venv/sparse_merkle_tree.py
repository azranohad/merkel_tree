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
        self.default_levels = []
        self.max = self.hex_to_int("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")



    def create_tree(self):
        l = "0"
        for i in range (257):
            self.default_levels.append(l)
            l = self.getHashValue(l + l)
        self.default_levels.reverse()
        root = Node (self.default_levels[0])
        root.start = 0
        root.end = self.max
        root.level = 0

        self.root = root;


    def change_path(self, leave):
        temp = leave
        check = self.getHashValue("0")
        level = 256
        while temp.parent is not None:
            default_level = self.default_levels[level]
            p = temp.parent
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
            level = level - 1
            temp = temp.parent

    def find_leave(self, leave):
        val = self.hex_to_int(leave)
        ##self.leaves_on.append(self.hex_to_int(leave))
        ##self.leaves_on.sort()
        start = int(0)
        end = int (self.max)
        temp = self.root
        level = 1

        while (temp.end > temp.start):
            default_level = self.default_levels[level]

            half = int((temp.end - temp.start) // 2)
            half = int(temp.start + half)
            if val <= half:
                if temp.left is None:
                    temp.left = Node(default_level)
                    temp.left.level = temp.level+1
                    temp.left.start = temp.start
                    temp.left.end = half
                    temp.left.parent = temp
                temp = temp.left
            else:
                if temp.right is None:
                    temp.right = Node(default_level)
                    temp.right.level = temp.level+1
                    temp.right.start = half+1
                    temp.right.end = temp.end
                    temp.right.parent = temp
                temp = temp.right
            level = level + 1
        ##if temp.parent.left is None:
          ##  temp.parent.left = Node("0")
          ##  temp.parent.left.level = 256
        ##if temp.parent.right is None:
        ##    temp.parent.right = Node("0")
        ##    temp.parent.left.level = 256
        return temp

    def add_leave(self, leave):
        leave_p = self.find_leave(leave)
        leave_p.set_value("1")
        self.change_path(leave_p)


    def getRoot(self):
        return self.root.value

    def getProof(self, leave):
        node = self.find_leave(leave)
        ##self.change_path(leave_p)
        level = 255

        result = self.root.value
        B = ""
        if self.root.value is self.default_levels[0]:
            result = result + " " + result
            return result
        p = node.parent
        while p is not None:
            default_level = self.default_levels[level]

            if p.value is not default_level:
                if p.left is node:
                    if p.right is None:
                        B = B + " " + self.default_levels[level+1]
                    else:
                        if p.left is None:
                            B = B + " " + self.default_levels[level + 1]
                        else:
                            B = B + " " + p.left.value
                        B = B + " " + p.right.value

                elif p.right is node:
                    if p.left is None:
                        B = B + " " + self.default_levels[level+1]
                    else:
                        if p.right is None:
                            B = B + " " + self.default_levels[level + 1]
                        else:
                            B = B + " " + p.right.value
                        B = B + " " + p.left.value

            node = p
            p = p.parent
            level = level - 1
        result = result + " " + B
        return result



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
        proof2 = mt.getProof("0000000000000000000000000000000000000000000000000000000000000000")
        proof3 = mt.getProof("0000000000000000000000000000000000000000000000000000000000000001")

        proof4 = mt.getProof("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")

        #mt.add_leave("0000000000000000000000000000000000000000000000000000000000010000")
        mt.add_leave("0000000000000000000000000000000000000000000000000000000000000001")
        mt.add_leave("1000000000000000000000000000000000000000000000000000000000000011")
        h1 = mt.getHashValue("0")
        h2 = mt.getHashValue(h1 + h1)
        x = 3





if __name__ == "__main__":
        main()
