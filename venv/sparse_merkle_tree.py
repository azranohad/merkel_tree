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

class Merkle_Tree_S:
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
        true_list = ""
        while temp.parent is not None:
            default_level = self.default_levels[level]
            p = temp.parent
            if level == 255:
                c = 3
            if p.left is temp:
                if p.right is None or p.right.value is default_level:
                    p.set_value(self.getHashValue(p.left.value + default_level))
                    true_list = true_list + " " + p.left.value+ " " + default_level + " " + p.value + "\n"

                else:
                    p.set_value(p.left.value + p.right.value)
                    true_list = true_list + " " + p.left.value + " " + p.right.value + " " + p.value + "\n"
            elif p.right is temp:
                if p.left is None or p.left.value is default_level:
                    p.set_value(default_level + p.right.value)
                    true_list = true_list + " " + default_level + " " + p.right.value + " " + p.value + "\n"

                else:
                    p.set_value(p.left.value + p.right.value)
                    true_list = true_list + " " + p.left.value + " " + p.right.value + " " + p.value + "\n"

            check = self.getHashValue(check + check)
            level = level - 1
            temp = temp.parent
        x = 3

    def getProof(self, leave):
        val = self.hex_to_int(leave)
        start = int(0)
        end = int (self.max)
        temp = self.root
        level = 0

        result = self.root.value
        B = ""
        default_level = self.default_levels[level]

        if self.root.value is self.default_levels[0]:
            result = result + " " + result
            return result

        while temp.value is not default_level and level != 256:
            default_level = self.default_levels[level]

            half = int((temp.end - temp.start) // 2)
            half = int(temp.start + half)
            if val <= half:
                if temp.left is None or temp.left.value is self.default_levels[level+1]:
                    if level == 255:
                        B = B + " " + "1"
                    else:
                        B = B + " " + self.default_levels[level+1]
                    break
                elif temp.left.value == '1':
                    if temp.right is None:
                        B = B + " " + '0'
                    else:
                        B = B + " " + '1'

                else:
                    temp = temp.left
            elif val > half:
                if temp.right is None or temp.right.value is self.default_levels[level+1]:
                    if level == 255:
                        B = B + " " + "1"
                    else:
                        B = B + " " + self.default_levels[level+1]
                    break
                elif temp.right.value == '1':
                    if temp.left is None:
                        B = B + " " + '0'
                    else:
                        B = B + " " + '1'
                else:
                    temp = temp.right
            level = level+1
        if temp.level == 0:
            if val <= half:
                B = B + " " + temp.right.value
            elif val > half:
                B = B + " " + temp.left.value
        p = temp.parent
        while p is not None:
            default_level = self.default_levels[level]
            if p.left is temp:
                if p.right is None:
                    B = B + " " + self.default_levels[p.level + 1]
                else:
                    B = B + " " + p.right.value
            elif p.right is temp:
                if p.left is None:
                    B = B + " " + self.default_levels[p.level + 1]
                else:
                    B = B + " " + p.left.value
            temp = p
            p = temp.parent
            level = level - 1

        result = result + " " + B
        return result

    def find_leave(self, leave):
        val = self.hex_to_int(leave)
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
        return temp

    def add_leave(self, leave):
        leave_p = self.find_leave(leave)
        leave_p.set_value("1")
        self.change_path(leave_p)


    def getRoot(self):
        return self.root.value


    def check_inclusion(self, digest, v, hash):
        value = int(v)
        arr_hash = hash.split()
        node_temp = None
        node_list = ""
        val = self.hex_to_int(digest)
        start = int(0)
        end = int (self.max)
        half = None
        x = 2
        list_half = []
        if len(arr_hash) < 257 and value is 1:
            return False

        for i in range(0, len(arr_hash) - 2):
            half = int((end - start) // 2)
            half = int(start + half)
            list_half.append(half)
            if val <= half:
                end = half
            elif val > half:
                start = half + 1
        if len(arr_hash) == 257:
            if val % 2 is 0:
                node_temp = self.getHashValue(v + arr_hash[1])
            else:
                node_temp = self.getHashValue(arr_hash[1] + v)
            node_list = node_list + "\n" + node_temp
        else:
            if val <= half:
                node_temp = self.getHashValue(arr_hash[1] + arr_hash[2])
            elif val > half:
                node_temp = self.getHashValue(arr_hash[2] + arr_hash[1])
            x = 3
            node_list = node_list + "\n" + node_temp

        t = len(list_half) - 1
        for i in range (t):
            if list_half[t] <= list_half[t-1]:
                node_temp = self.getHashValue(node_temp + arr_hash[x])
            elif list_half[t] > list_half[t-1]:
                node_temp = self.getHashValue(arr_hash[x] + node_temp)
            x = x + 1
            node_list = node_list + "\n" + node_temp

        if len(arr_hash) == x + 1:
            if val <= half:
                node_temp = self.getHashValue(node_temp + arr_hash[x])
            elif val > half:
                node_temp = self.getHashValue(arr_hash[x] + node_temp)
        if node_temp == arr_hash[0]:
            return True
        else:
            return False


    def getHashValue(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def hex_to_int(self, string_h):
        return int(string_h, 16)


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
        check1 = mt.check_inclusion("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "0", "9ca619dd4a13d02391aeb48fa9dd0a56f6fcf7ed0bc7311c45e64c052eca7133 1ba915e042e9aafcd4348b060345025ef2eb8f93d4fc7fe1719b9a7e1c1034be 451f7cb426ffa960fdad0301d4f4ccf4107751dfbe878cc5a71824f72b4d67bc")
        check2 = mt.check_inclusion("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "1", "9ca619dd4a13d02391aeb48fa9dd0a56f6fcf7ed0bc7311c45e64c052eca7133 1ba915e042e9aafcd4348b060345025ef2eb8f93d4fc7fe1719b9a7e1c1034be 451f7cb426ffa960fdad0301d4f4ccf4107751dfbe878cc5a71824f72b4d67bc")
        check3 = mt.check_inclusion("0000000000000000000000000000000000000000000000000000000000000001", "0", proof3)
        check4 = mt.check_inclusion("0000000000000000000000000000000000000000000000000000000000000000", "1", proof2)
        check5 = mt.check_inclusion("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "0", proof4)

        x = 3





if __name__ == "__main__":
        main()
