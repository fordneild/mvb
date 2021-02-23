from txGenerator import generate_hash
from Transaction import Transaction
import random


class Block:
    def __init__(self, tx: Transaction, prev):
        self.tx = tx
        self.prev = prev
        self.nonce = self.generate_nonce(64)
        self.pow = self.generate_pow()

    @staticmethod
    def generate_nonce(length):
        """Generate pseudorandom number."""
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

    def generate_pow(self):
        return generate_hash([self.tx, self.prev, self.nonce])

    def hash(self):
        return generate_hash(self)