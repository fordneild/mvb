import threading
import time
import json
import sys
import random
import txGenerator
# from Node import HonestNode, MaliciousNode
import threading
from Chain import Chain
from Transaction import Transaction
import queue
import copy
import time
import random
class HonestNode(threading.Thread):
    def __init__(self, name, genesisBlock):
        threading.Thread.__init__(self)
        self.name = name
        # Each Node has a Queue to track incoming chains from others
        self.q = queue.Queue()
        # we use these two to determine which unverified transaction we should look at next...
        self.invalidTx = set()
        self.unverifiableTx = set()
        self.txInChain = set()
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
        for (unverifiedTxNum, unverifiedTx) in list(unverifiedTxs.items()):
            # until we find possible valid Tx that we do not already have in our chain
            if unverifiedTxNum not in self.txInChain and unverifiedTxNum not in self.invalidTx and unverifiedTxNum not in self.unverifiableTx:
                # try:
                tx = Transaction(unverifiedTx)
                print(unverifiedTxNum + "is valid")
                # except:
                    # this was an invalidTX, mark it as such
                    # self.invalidTx.add(unverifiedTxNum)
                    # print(unverifiedTxNum + "is invalid")
                    # lets see if we got new chains from our neighbors
                    # break
                try:
                    self.chain.addTx(tx)
                    self.txInChain.add(tx.number)
                    self.unverifiableTx = {}
                    self.broadcastChain()
                except:
                    print(unverifiedTxNum + "is unverifable")
                    self.unverifiableTx.add(unverifiedTxNum)
                    break

    def sendChain(self, chain):
        self.q.put(chain)

    def receiveChain(self):
        newChain = self.q.get()
        if len(newChain.blocks) > len(self.chain.blocks):
            if Chain.validateChain(newChain, self.chain.blocks[0]):
                self.unverifiableTx = {}
                self.txInChain = {}
                self.chain = copy.deepcopy(newChain)
                for block in self.chain.blocks:
                    self.txInChain.add(block.tx.number)

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

# these variables are globally accessible to all nodes
stop_threads = False
nodes = {}
# when we detect we are on a fork, add back transactions from shorter block that are also not on the larger block
unverifiedTxs = {}

def driver(txs, numHonestNodes, numMaliciousNodes, genesisBlock):
    honest_nodes_left_to_finish = startNodes(numHonestNodes, numMaliciousNodes, genesisBlock)
    # add transactions, which causes nodes to process them
    for tx in txs:
        randomSleepTime = random.uniform(0, 1)
        time.sleep(randomSleepTime)
        unverifiedTxs[tx['number']] = tx
    STOP_LENGTH_CHAIN = 4
    while True:
        if(len(honest_nodes_left_to_finish) == 0 ):
            # put in an order to stop all Nodes
            global stop_threads
            stop_threads = True
            break
        else:
            toRemove = False
            for honest_node_id in honest_nodes_left_to_finish:
                honest_node = nodes[honest_node_id]
                if(len(honest_node.chain.blocks) >= STOP_LENGTH_CHAIN):
                    toRemove = honest_node_id
                    break
                # else:
                #     print(honest_node_id + " has chain of len" + str(len(honest_node.chain.blocks)))
            if(toRemove):
                honest_nodes_left_to_finish.remove(toRemove)
    # wait for all nodes to stop
    for node in nodes.items():
        node.join()
    print('all done!')

def idxToKey(idx):
    return 'Node' + str(idx)

def startNodes(numHonest, numMalicious, genesisBlock):
    global nodes
    honest_node_ids = set()
    for i in range(numHonest):
        key = idxToKey(i)
        honest_node_ids.add(key)
        # Create node in thread
        nodes[key] = HonestNode(key, genesisBlock)
        # Start it
        nodes[key].start()
    
    for i in range(numMalicious):
        key = idxToKey(i)
        # Create node in thread
        nodes[key] = MaliciousNode(key, genesisBlock)
        # Start it
        nodes[key].start()
    return honest_node_ids


def setupTxs(file_name):
    return txGenerator.main(file_name)

if __name__ == "__main__":
    # create genesis block
    # validate user input
    if len(sys.argv) < 2:
        print("you must specify a path to your input json")
        exit(0)
    # get data
    file_name = sys.argv[1]
    genesisBlock = setupTxs(file_name)
    with open(file_name) as json_file:
        txs = json.loads(json_file.read())
    NUM_HONEST_NODES = 1
    NUM_MALICIOUS_NODES = 0
    driver(txs, NUM_HONEST_NODES,NUM_MALICIOUS_NODES, genesisBlock)

