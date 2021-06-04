import hashlib, sys


class Node:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value
        self.parent = None
        self.hashValue = hashlib.sha256(value.encode('utf-8')).hexdigest()





class Merkle_Tree:
    def __init__(self):
        self.leaves = []
        self.root = None

    def create_tree(self):
        level_nodes = []

        for i in self.leaves:
            level_nodes.append(i)

        while len(level_nodes) != 1:
            temp_nodes = []
            for n in range(0, len(level_nodes), 2):
                node_left = level_nodes[n]
                if n + 1 < len(level_nodes):
                    node_right = level_nodes[n + 1]
                else:
                    temp_nodes.append(level_nodes[n])
                    break

                mergeHash = node_left.hashValue + node_right.hashValue
                parent = Node(mergeHash)
                node_left.parent = parent
                node_right.parent = parent
                parent.left = node_left
                parent.right = node_right
                temp_nodes.append(parent)
            level_nodes = temp_nodes
        self.root = level_nodes[0]

    def getRoot(self):
        return self.root

    def getProof(self, index):
        result = self.getRoot().hashValue
        B = ""

        node = self.leaves[index]
        p = node.parent
        while p is not None:
            if p.left is node:
                B = B + " " + p.right.hashValue
            else:
                B = B + " " + p.left.hashValue
            node = p
            p = p.parent
            result = result + " " + B
            return result

    def check_inclusion(self, value, hash):
        arr_hash = hash.split()
        hash_node = self.getHashValue(value)
        s = str(hash_node + arr_hash[1])
        p_calc = self.getHashValue(s)
        for i in range(2, len(arr_hash)):
            hash_node = self.getHashValue(p_calc)
            p_calc = self.getHashValue(hash_node + arr_hash[i])
        if p_calc is arr_hash[0]:
            return True
        else:
            return False

    def getHashValue(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def add_leave(self, leave):
        node = Node(leave)
        self.leaves.append(node)
        self.create_tree()

def main():
        mt = Merkle_Tree()
        mt.add_leave("a")
        root1 = mt.getRoot()
        mt.add_leave("b")
        root2 = mt.getRoot()
        mt.add_leave("c")
        root3 = mt.getRoot()
        proof0 = mt.getProof(0)
        proof2 = mt.getProof(2)
        check1 = mt.check_inclusion("a", "d71dc32fa2cd95be60b32dbb3e63009fa8064407ee19f457c92a09a5ff841a8a 13e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d 12e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6")
        x = 3





        x = 3
if __name__ == "__main__":
        main()
