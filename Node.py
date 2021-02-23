from Block import Block
import threading
from Chain import Chain
from Transaction import Transaction
import queue
import copy
import time
import random
from driver import stop_threads, nodes, unverifiedTxs


class HonestNode(threading.Thread):
    def __init__(self, name, genesisBlock):
        threading.Thread.__init__(self)
        self.name = name
        # Each Node has a Queue to track incoming chains from others
        self.q = queue.Queue()
        # we use these two to determine which unverified transaction we should look at next...
        self.invalidTx = set()
        self.unverifiableTx = set()
        # each node holds their own chain
        self.chain = Chain(genesisBlock)

    def run(self):
        # target function of the thread class
        try:
            print(self.name + " running...")
            while True:
                # process all new chains in queue
                while not self.q.empty():
                    self.receiveChain()
                # process any new unverified transactions
                self.processUnverifiedTx()
                global stop_threads
                if stop_threads:
                    break
        finally:
            print(self.name + " stopped")

    # gets a new unverified transaction not already in out chain
    def processUnverifiedTx(self):
        global unverifiedTxs
        # loop over all unverified Tx
        for (unverifiedTxNum, unverifiedTx) in unverifiedTxs.items():
            # until we find possible valid Tx that we do not already have in our chain
            if not self.chain.hasTx(unverifiedTxNum) and unverifiedTxNum not in self.invalidTx and unverifiedTxNum not in self.unverifiableTx:
                try:
                    tx = Transaction(unverifiedTx)
                except:
                    # this was an invalidTX, mark it as such
                    self.invalidTx.add(unverifiedTxNum)
                    # lets see if we got new chains from our neighbors
                    break
                try:
                    self.chain.addTx(tx)
                    self.unverifiableTx = {}
                    self.broadcastChain()
                except:
                    self.unverifiableTx.add(unverifiedTxNum)
                    break

    def sendChain(self, chain):
        self.q.put(chain)

    def receiveChain(self):
        newChain = self.q.get()
        if len(newChain.blocks) > len(self.chain.blocks):
            if Chain.validateChain(newChain, self.chain.blocks[0]):
                self.unverifiableTx = {}
                self.chain = copy.deepcopy(newChain)

    def broadcastChain(self):
        print(self.name + " broadcasting chain ")
        global nodes
        for nodeKey, node in nodes.items():
            if nodeKey != self.name:
                node.sendChain(self.chain)

class MaliciousNode(threading.Thread):
    def __init__(self, name, genesisBlock):
        threading.Thread.__init__(self)
        self.name = name
        # Each Node has a Queue to track incoming chains from others
        self.q = queue.Queue()
        # each node holds their own chain
        self.chain = Chain(genesisBlock)
        self.badBlocks = [RandomBlock, MissingNonceBlock, MissingPowBlock, MissingPrevBlock, MissingTxBlock]

    def run(self):
        # target function of the thread class
        try:
            print(self.name + " running...")
            while True:
                # process all new chains in queue
                while not self.q.empty():
                    self.receiveChain()
                # process any new unverified transactions
                global stop_threads
                if stop_threads:
                    break
        finally:
            print(self.name + " stopped")

    def sendChain(self, chain):
        self.q.put(chain)

    def receiveChain(self):
        newChain = self.q.get()
        if len(newChain.blocks) >= len(self.chain.blocks):
            newChain = copy.deepcopy(newChain)
            blocks  = newChain.blocks
            numBlocksToAdd = 3
            for i in range(numBlocksToAdd):
                badBlockClass = random.choice(self.badBlocks)
                blocks.append(badBlockClass())
            self.broadcastChain(newChain)

    def broadcastChain(self,chain):
        print(self.name + " broadcasting chain ")
        global nodes
        for nodeKey, node in nodes.items():
            if nodeKey != self.name:
                node.sendChain(chain)

def generate_nonce(length):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

class RandomBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)



class MissingTxBlock():
    def __init__(self):
        self.prev = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)
class MissingPrevBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)

class MissingNonceBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.pow = generate_nonce(128)

class MissingPowBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)
