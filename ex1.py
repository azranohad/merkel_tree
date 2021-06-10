# Ohad Azran, 303080097, Amit Ilovitch, 313581688
import hashlib, sys, base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


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
        self.leaves = []
        self.root = None
        self.private_key = None
        self.public_key = None

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
        if self.root is not None:
            return str(self.root.hashValue)
        else:
            return ""

    def getProof(self, index):
        result = self.getRoot()
        B = ""
        if len(self.leaves) > 0:
            node = self.leaves[int(index)]
        else:
            return ""
        p = node.parent
        while p is not None:
            if p.left is node:
                B = "1" + p.right.hashValue
            else:
                B = "0" + p.left.hashValue
            node = p
            p = p.parent
            result = result + " " + B
        return result

    def merge_string(self, arri, string):
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

    """
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
    """

    def getHashValue(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def create_RSA(self):

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        pep = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pem_d = pem.decode('utf-8')
        pep_d = pep.decode('utf-8')
        return pem_d + "\n" + pep_d

    def create_sign(self, sign_key):
        sign_key_replace = sign_key.replace("\\n", "\n")
        sign_key_bytes = str.encode(sign_key_replace)
        try:
            private_key = serialization.load_pem_private_key(
                sign_key_bytes,
                password=None,
            )
        except:
            return ("1")
        root_bytes = str.encode(self.root.value)
        signature = private_key.sign(
            root_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        signature_str = base64.b64encode(signature)
        sign_d = signature_str.decode('utf-8')
        return sign_d

    def verify_sign(self, verify_key, sign, text):
        sign_key_replace = sign.replace("\\n", "\n")
        verify_key_replace = verify_key.replace("\\n", "\n")
        sign_key_bytes = base64.decodebytes(sign_key_replace.encode())
        text_bytes = str.encode(text)
        verify_key_bytes = str.encode(verify_key_replace)
        try:
            public_key = serialization.load_pem_public_key(
                verify_key_bytes,
            )
        except:
            print(2)
        try:
            public_key.verify(
                sign_key_bytes,
                text_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except:
            return False
        return True

    def add_leave(self, leave):
        node = Node(leave)
        self.leaves.append(node)
        self.create_tree()


class Merkle_Tree_S:
    def __init__(self):
        self.leaves_on = []
        self.root = None
        self.default_levels = []
        #the max value leave
        self.max = self.hex_to_int("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
        """
        this function initialize root with default value, and range of number of leaves
        """
    def create_tree(self):
        l = "0"
        for i in range(257):
            self.default_levels.append(l)
            l = self.getHashValue(l + l)
        self.default_levels.reverse()
        root = Node(self.default_levels[0])
        root.start = 0
        root.end = self.max
        root.level = 0

        self.root = root
        """
        after open path to the new leave, this function initialize value all node.
        the leave argument, this digest 
        """
    def change_path(self, leave):
        temp = leave
        level = 256
        while temp.parent is not None:
            default_level = self.default_levels[level]
            p = temp.parent
            ## who is the last node
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

            level = level - 1
            temp = temp.parent

    """
    create proof for leave
    """
    def getProof(self, leave):
        val = self.hex_to_int(leave)
        temp = self.root
        level = 0

        result = self.root.value
        B = ""
        default_level = self.default_levels[level]
        """
        if all leaves is value 0
        """
        if self.root.value is self.default_levels[0]:
            result = result + " " + result
            return result

        while temp.value is not default_level and level != 256:
            default_level = self.default_levels[level]

            half = int((temp.end - temp.start) // 2)
            half = int(temp.start + half)
            ## the left node
            if val <= half:
                """
                is leave
                """
                if temp.left is None or temp.left.value is self.default_levels[level + 1]:
                    if level == 255:
                        B = B + " " + "1"
                    else:
                        B = B + " " + self.default_levels[level + 1]
                    break
                elif temp.left.value == '1':
                    if temp.right is None:
                        B = B + " " + '0'
                    else:
                        B = B + " " + '1'

                else:
                    temp = temp.left
                    ## the right node
            elif val > half:
                if temp.right is None or temp.right.value is self.default_levels[level + 1]:
                    if level == 255:
                        B = B + " " + "1"
                    else:
                        B = B + " " + self.default_levels[level + 1]
                    break
                elif temp.right.value == '1':
                    if temp.left is None:
                        B = B + " " + '0'
                    else:
                        B = B + " " + '1'
                else:
                    temp = temp.right
            level = level + 1
        if temp.level == 0:
            if val <= half:
                B = B + " " + temp.right.value
            elif val > half:
                B = B + " " + temp.left.value
        p = temp.parent
        """
        add all value to the proof
        """
        while p is not None:
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
    """
    open path and create all node to the new leave
    """
    def find_leave(self, leave):
        val = self.hex_to_int(leave)
        start = int(0)
        end = int(self.max)
        temp = self.root
        level = 1

        while (temp.end > temp.start):
            default_level = self.default_levels[level]

            half = int((temp.end - temp.start) // 2)
            half = int(temp.start + half)
            if val <= half:
                if temp.left is None:
                    temp.left = Node(default_level)
                    temp.left.level = temp.level + 1
                    temp.left.start = temp.start
                    temp.left.end = half
                    temp.left.parent = temp
                temp = temp.left
            else:
                if temp.right is None:
                    temp.right = Node(default_level)
                    temp.right.level = temp.level + 1
                    temp.right.start = half + 1
                    temp.right.end = temp.end
                    temp.right.parent = temp
                temp = temp.right
            level = level + 1
        return temp
    """
    call to function to open path and change path.
    """
    def add_leave(self, leave):
        leave_p = self.find_leave(leave)
        leave_p.set_value("1")
        self.change_path(leave_p)
    """
    return root value
    """
    def getRoot(self):
        return self.root.value
    """
    check if the leave in digest with v , match to hash proof.
    """
    def check_inclusion(self, digest, v, hash):
        value = int(v)
        arr_hash = hash.split()
        node_temp = None
        node_list = ""
        val = self.hex_to_int(digest)
        start = int(0)
        end = int(self.max)
        half = None
        x = 2
        list_half = []
        ## the value is 1 and the proof is small.
        if len(arr_hash) < 257 and value == 1:
            return False
        """
        craete hash value from the proof
        """
        for i in range(0, len(arr_hash) - 2):
            half = int((end - start) // 2)
            half = int(start + half)
            list_half.append(half)
            if val <= half:
                end = half
            elif val > half:
                start = half + 1
        if len(arr_hash) == 257:
            if val % 2 == 0:
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
        for i in range(t):
            if list_half[t] <= list_half[t - 1]:
                node_temp = self.getHashValue(node_temp + arr_hash[x])
            elif list_half[t] > list_half[t - 1]:
                node_temp = self.getHashValue(arr_hash[x] + node_temp)
            x = x + 1
            node_list = node_list + "\n" + node_temp

        if len(arr_hash) == x + 1:
            if val <= half:
                node_temp = self.getHashValue(node_temp + arr_hash[x])
            elif val > half:
                node_temp = self.getHashValue(arr_hash[x] + node_temp)
        """
        check if the root in proof match to root calculate
        """
        if node_temp == arr_hash[0]:
            return True
        else:
            return False

    def getHashValue(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    """
    change digest to int num.
    """
    def hex_to_int(self, string_h):
        return int(string_h, 16)


def main():

    mt = Merkle_Tree()
    mts = Merkle_Tree_S()
    mts.create_tree()
    while (True):
        str_input = input()
        str_list = str_input.split()
        if str_list[0] == "1":
            mt.add_leave(str_list[1])

        elif str_list[0] == "2":
            print(mt.getRoot())

        elif str_list[0] == "3":
            print(mt.getProof(str_list[1]))

        elif str_list[0] == "4":
            str_second_arg = ""
            for i in range(2, len(str_list)):
                if i == 2:
                    str_second_arg = str_list[i]
                else:
                    str_second_arg = str_second_arg + " " + str_list[i]
            print(mt.check_inclusion(str_list[1], str_second_arg))

        elif str_list[0] == "5":
            print(mt.create_RSA())

        elif str_list[0] == "6":

            str_second_arg = str_input.split(" ", 1)
            # new_sign_key = ("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAzg4xczjX3XASNt5dZu9o7IYstSa25cXf4LNjaer+EhGRDMpL\nNiD3l9QXdx0sTAA3eNYHBXmSO8QLfl08pFJyagTOItkG0cSzvASm+/rlqSTdENfz\nQeIF8d1jm0hzpRF7FMYvJRRDdFJXk2z5N6YTa+V1KyYPxawSM9AaJ636DUeCm9g/\nQwzv5ozdjnB6bjuD+foITo5v90uX/vul8ywHf66ckuGVmJ95efxsY4LKN/Vmnmst\n5SzRxJDfGDXZa9lUmWJAILMQx7/gjxvFaRzLmdiTvVjJw/a2hlKnd6zdKcBzEoDl\nDU+AXp30FxbF/OgygeQTkWaO5+hPO8uR1EqfOQIDAQABAoIBAQCwtVVNFeNxwKmu\nKlZ5bzlRFeQDWnchZ+eN4OmRrPhEcJIvINENU4phx350JS2W49yuoQWWeWKiJIci\n0DywQxBhwUsycWI6xPDKfkbh85G+06FNz5SK3JXyjMTeJ20dk3c1IpzNtKoAeJko\nEh1Lzv362uX3ogWGpQFbM80qWDYH6dAB+SeyITaLtEtZLaUKWozEcW/gQHktjwYH\nwfcyGpUi1OWeT4YeVXw/Qdd8qosKl2ik+V7vTmCCN8q/yM+VRkbWlqH8tVmZDtT/\nZ2d2AXY0hduPwrW46XEumo+Aw/OZ3V8aaLT3j9Cj11w8OIL+h8SNYb2nTIvF4/xo\niIZgfyL9AoGBAPPYIYv85+S6q0vjDVPvtGaO9t1GoRBaIjWGN84vTfGH8X8qjMzr\nYy913CN8v5/J7MAdyZLneFnodysprgZtN9C2BVcGBrBdL8+fOAfA+7RJ4EOITuBI\nPA14WH7R2bPBI3fscbe6jPOoIkfQ8E9Kh5PRi+FFd/pUgp2V38bRJy4HAoGBANhT\nz/H1HPb2LMG9a5XHrVSCgEt1dljU3OHUBdWtu0x/T6Yoq8fmAVdfT4LlmJ6dtBit\nx4/dZmp+MLgQo8kAMs2IW6xuX3qnwGXr8EyjZs/tg+FQnhTPuJeN7QybL+Jwd0xh\nzpdWds9Aq5AgZUw5/yFv4vURuUhwN1ZR1m0ipHi/AoGAVZCw7ON5J/0M4NsysRJ7\nFkXygGEpYYiPWoLXkEVvL2MJrhrrP3kV2/Cap+U9hL+hkSSiuCb7R2lYb8/3Xg/z\nNwy4QPo/XKHGhi+TxLzGVlRaGrh5HSCb2gox24adwwLyBEH3AYa3sUR9iv/ZY6l+\ne7NbR1hOKox/LPcLiEOaYP8CgYBB6h/FaNtfgJkYm1/proLo6i6vT2Y1IP8ArHru\npdYZM/2P8nqNGU81USxIBS9gvUq/7kuNUXfAYRz1KNTPDQltyOut+Z+MHwsnwyFg\nKLXOC2AQymCwlK55N1yQZ8TKaVxgYLjzMfxXoCvmaYiUFmPfy1jLNZBQOykRWzRL\n4q9cvwKBgHH8GmC4x+GnlBFuRwKxqcJUfUFEfkM6HoF9Y4yM21UytmBS59vlHpQe\nXCQNN6zsi0y6WqIpuZf90oEX2IGhoWbnVj4e8zI6+jSBQh0v+2pYkdoERfJE9dkB\nYMndTXKHPlh7u+wlDWP5Sq7dgiWxEKnstl1NhOH1qePINalcvdUJ\n-----END RSA PRIVATE KEY-----\n")
            temp_input = input()
            while "-----END RSA PRIVATE KEY-----" != temp_input:
                str_second_arg[1] = str_second_arg[1] + "\n" + temp_input
                temp_input = input()

            str_second_arg[1] = str_second_arg[1] + "\n-----END RSA PRIVATE KEY-----\n"
            print(mt.create_sign(str_second_arg[1]))
            bla = input()

        elif str_list[0] == "7":
            str_second_arg = str_input.split(" ", 1)
            new_line_number_1 = False
            temp_input = input()
            while "-----END PUBLIC KEY-----" != temp_input:
                str_second_arg[1] = str_second_arg[1] + "\n" + temp_input
                temp_input = input()

            str_second_arg[1] = str_second_arg[1] + "\n-----END PUBLIC KEY-----\n"
            bla = input()
            sign = input()
            sign_split = sign.split(" ", 1)
            print(mt.verify_sign(str_second_arg[1], sign_split[0], sign_split[1]))

        elif str_list[0] == "8":
            mts.add_leave(str_list[1])
        elif str_list[0] == "9":
            print(mts.getRoot())
        elif str_list[0] == "10":
            print(mts.getProof(str_list[1]))
        elif str_list[0] == "11":
            str_third_arg = ""
            for i in range(3, len(str_list)):
                if i == 3:
                    str_third_arg = str_list[i]
                else:
                    str_third_arg = str_third_arg + " " + str_list[i]
            print(mts.check_inclusion(str_list[1], str_list[2], str_third_arg))

        """
        mt.add_leave("a")
        root1 = mt.getRoot()
        mt.add_leave("b")
        root2 = mt.getRoot()
        mt.add_leave("c")
        root3 = mt.getRoot()
        proof0 = mt.getProof(0)
        proof2 = mt.getProof(2)

      #  check1 = mt.check_inclusion("a", "d71dc32fa2cd95be60b32dbb3e63009fa8064407ee19f457c92a09a5ff841a8a 13e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d 12e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6")
        rsa5 = mt.create_RSA()
        new_sign_key =("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAzg4xczjX3XASNt5dZu9o7IYstSa25cXf4LNjaer+EhGRDMpL\nNiD3l9QXdx0sTAA3eNYHBXmSO8QLfl08pFJyagTOItkG0cSzvASm+/rlqSTdENfz\nQeIF8d1jm0hzpRF7FMYvJRRDdFJXk2z5N6YTa+V1KyYPxawSM9AaJ636DUeCm9g/\nQwzv5ozdjnB6bjuD+foITo5v90uX/vul8ywHf66ckuGVmJ95efxsY4LKN/Vmnmst\n5SzRxJDfGDXZa9lUmWJAILMQx7/gjxvFaRzLmdiTvVjJw/a2hlKnd6zdKcBzEoDl\nDU+AXp30FxbF/OgygeQTkWaO5+hPO8uR1EqfOQIDAQABAoIBAQCwtVVNFeNxwKmu\nKlZ5bzlRFeQDWnchZ+eN4OmRrPhEcJIvINENU4phx350JS2W49yuoQWWeWKiJIci\n0DywQxBhwUsycWI6xPDKfkbh85G+06FNz5SK3JXyjMTeJ20dk3c1IpzNtKoAeJko\nEh1Lzv362uX3ogWGpQFbM80qWDYH6dAB+SeyITaLtEtZLaUKWozEcW/gQHktjwYH\nwfcyGpUi1OWeT4YeVXw/Qdd8qosKl2ik+V7vTmCCN8q/yM+VRkbWlqH8tVmZDtT/\nZ2d2AXY0hduPwrW46XEumo+Aw/OZ3V8aaLT3j9Cj11w8OIL+h8SNYb2nTIvF4/xo\niIZgfyL9AoGBAPPYIYv85+S6q0vjDVPvtGaO9t1GoRBaIjWGN84vTfGH8X8qjMzr\nYy913CN8v5/J7MAdyZLneFnodysprgZtN9C2BVcGBrBdL8+fOAfA+7RJ4EOITuBI\nPA14WH7R2bPBI3fscbe6jPOoIkfQ8E9Kh5PRi+FFd/pUgp2V38bRJy4HAoGBANhT\nz/H1HPb2LMG9a5XHrVSCgEt1dljU3OHUBdWtu0x/T6Yoq8fmAVdfT4LlmJ6dtBit\nx4/dZmp+MLgQo8kAMs2IW6xuX3qnwGXr8EyjZs/tg+FQnhTPuJeN7QybL+Jwd0xh\nzpdWds9Aq5AgZUw5/yFv4vURuUhwN1ZR1m0ipHi/AoGAVZCw7ON5J/0M4NsysRJ7\nFkXygGEpYYiPWoLXkEVvL2MJrhrrP3kV2/Cap+U9hL+hkSSiuCb7R2lYb8/3Xg/z\nNwy4QPo/XKHGhi+TxLzGVlRaGrh5HSCb2gox24adwwLyBEH3AYa3sUR9iv/ZY6l+\ne7NbR1hOKox/LPcLiEOaYP8CgYBB6h/FaNtfgJkYm1/proLo6i6vT2Y1IP8ArHru\npdYZM/2P8nqNGU81USxIBS9gvUq/7kuNUXfAYRz1KNTPDQltyOut+Z+MHwsnwyFg\nKLXOC2AQymCwlK55N1yQZ8TKaVxgYLjzMfxXoCvmaYiUFmPfy1jLNZBQOykRWzRL\n4q9cvwKBgHH8GmC4x+GnlBFuRwKxqcJUfUFEfkM6HoF9Y4yM21UytmBS59vlHpQe\nXCQNN6zsi0y6WqIpuZf90oEX2IGhoWbnVj4e8zI6+jSBQh0v+2pYkdoERfJE9dkB\nYMndTXKHPlh7u+wlDWP5Sq7dgiWxEKnstl1NhOH1qePINalcvdUJ\n-----END RSA PRIVATE KEY-----\n")
        rsa6 = mt.create_sign(new_sign_key)



        public_key = ("-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1MAmLr5TwN8OnQF9OjfW\nGyGuHfl5056u7XBjYcsidkQHVLkK8NhFzSvBnQbi18PcXVSLusLPVnGs6a9rfN9N\nkCM6uSom0+lpFgMWuD/7w0HPIW7Cw0hVlFNWvZ8vv5uzA/mzpF8S1fRmCMkfQyP4\nTDJ2MImQxcdkWDpFDq1pmvRJweavzUnc2eUmuz4bwLYwv3CBKDlCSdIAFCkVP6PJ\nl8cbZkOPqbVPMW+MLf+pZrKfWczCxCnzHmLbzngClQp+4meAtGOGgKKwsmS1eA0B\nAYfao0g+cu1ESU5ePea/jrX0nJONvDOAeh00keQvxE1xoEnKppbKT2F6RTyBITbC\nmwIDAQAB\n-----END PUBLIC KEY-----\n")

        sign_7 = ("LhnptHJUc4M0GVZR+wbp5NC6owLwH2+N/UpOKV6jnyH8iA8YoVSQkMU63z8QZyr50L1f4hTWSxZbjzeQ1Rm/1OyAyX9QdQHIrMWRjOx0GPfqPi4wmcmF9ZxPr7ShwRZtbqz9mAekKYDell44Pj21xKsFFy4PgpnxrXFNppPOA3ZpQk245bYPIdzYpcmq0FyYx5RQQCQYBV69QrQOAvvkVVkwZbiqI0/+tZWmfNdV/x6E3PWYljSccMLW/m4nhcy+XQ39Q2oxIzYlobwndW3epxEReLzP7qeN9BR/BVew2yCn4quhm1fA7544mpZaW0VynQDRHBy7gqJDhuWRLjKOcQ==")
        text = ("ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb")
        rsa7 = mt.verify_sign(public_key, sign_7, text)
        x = 3
        """


if __name__ == "__main__":
    main()
