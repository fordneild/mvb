import threading
import hashlib
import nacl
import time
import queue
import json
import sys
import random
import copy

# these variables are globally accessible to all nodes
stop_threads = False
nodes = {}
# when we detect we are on a fork, add back transactions from shorter block that are also not on the larger block
unverifiedTxs = {}
# once the longest chain has all of the transactions, we are done
txInLongestChain = set()


# driver takes transactions and number of nodes to process them

# TODO validate other nodes incoming new chain (forking)
# TODO generate examples
# TODO signing blocks and verifying signatures in TX


def driver(txs, numNodes):
    startNodes(numNodes)
    # add transactions, which causes nodes to process them
    for tx in txs:
        randomSleepTime = random.uniform(0, 1)
        time.sleep(randomSleepTime)
        unverifiedTxs[tx['number']] = tx
    # put in an order to stop all Nodes
    global stop_threads
    stop_threads = True
    # wait for all nodes to stop
    for i in range(numNodes):
        key = idxToKey(i)
        nodes[key].join()
    print('all done!')


# Each node wraps a thread

def generate_hash(secrets):
    dk = hashlib.sha256()
    for s in secrets:
        bsecret = s.encode('utf-8')
        dk.update(bsecret)
    return dk.hexdigest()


class Transaction:
    def __init__(self, tx):
        # TODO validate tx
        print("creating tx from " + str(tx))
        self.input = tx['input']
        self.number = tx['number']
        self.output = tx['output']
        self.sig = tx['sig']
        Transaction.validate(self)

    def netTx(tx):
        bank = {}
        for i in tx.input:
            output = i['output']
            senderPk = output['pubkey']
            sendAmount = output['value']
            if senderPk not in bank:
                bank[senderPk] = 0
            bank[senderPk] -= sendAmount
        for o in tx.output:
            receiverPk = o['pubkey']
            receiveAmount = o['value']
            if receiverPk not in bank:
                bank[receiverPk] = 0
            bank[receiverPk] += receiveAmount
        return bank

    def validate(self):
        #
        # if not valid, throw error
        hexHash = generate_hash([self.input, self.output, self.sig])
        if self.number != hexHash:
            return False
        totalInOut = 0
        for val in Transaction.netTx(self):
            totalInOut += val
        if totalInOut != 0:
            return False
        vk = VerifyKey(verify_key_hex, encoder=HexEncoder)


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


class Chain:
    def __init__(self, genesisBlock: Block):
        self.blocks = [genesisBlock]
        # a set of tx in the chain
        self.tx = set()
        # the current state of everyone wallet
        # <pk>:<totalCoins>
        self.bank = {}

    def addTx(self, rawTx):
        tx = Transaction(rawTx)
        net = Transaction.netTx(rawTx)
        for (userPk, delta) in net.items():
            if userPk not in self.bank:
                self.bank[userPk] = 0
            if delta < 0:
                if self.bank[userPk] < delta * -1:
                    raise Exception("user " + userPk + " does not have enough money")

        # for each person that lost money from this transaction
        # if they dont have the money they lost
        # dont add the transaction to our chain

        lastBlockHash = self.blocks[len(self.blocks) - 1].hash()
        block = Block(tx, lastBlockHash)
        # create tx
        # create block
        # validate block (they have the money for it in bank)
        # add the block to our chain
        # add tx to self.tx
        # update bank
        return 'nonce'

    def hasTx(self, txNum):
        return txNum in self.tx

    def validate(blocks, genesisBlock):
        try:
            if (blocks[0].hash() != genesisBlock.hash()):
                return False
            # we have the same genesis
            for block in blocks[1:]:
                if block.pow < 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    # TODO for forking
                    # make sure this block makes sense in the context of the rest of the chain
                    # temp_bank stuff
                    # prev matches up
                    # hashes all make sense
                    pass
        except:
            return False


class Node(threading.Thread):
    def __init__(self, name, genesisBlock):
        threading.Thread.__init__(self)
        self.name = name
        # Each Node has a Queue to track incoming chains from others
        self.q = queue.Queue()
        # we use these two to determine which unverified transaction we should look at next...
        self.invalidTx = set()
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
            if not self.chain.hasTx(unverifiedTxNum) and unverifiedTxNum not in self.invalidTx:
                try:
                    tx = Transaction(unverifiedTx)
                except:
                    # this was an invalidTX, mark it as such
                    self.invalidTx.add(unverifiedTxNum)
                    # lets see if we got new chains from our neighbors
                    break
                try:
                    self.chain.addTx(tx)
                    self.broadcastChain()
                except:
                    # this tx is not valid for our chain, but may be so later on
                    # so lets try another Tx
                    pass

    def sendChain(self, chain):
        self.q.put(chain)

    def receiveChain(self):
        newChain = self.q.get()
        if len(newChain.blocks) > len(self.chain.blocks):
            if Chain.validate(newChain, self.chain.blocks[0]):
                self.chain = copy.deepcopy(newChain)

    def broadcastChain(self):
        print(self.name + " broadcasting chain ")
        global nodes
        for nodeKey, node in nodes.items():
            if nodeKey != self.name:
                node.sendChain(self.chain)


def idxToKey(idx):
    return 'Node' + str(idx)


def startNodes(num):
    for i in range(num):
        key = idxToKey(i)
        # Create node in thread
        global nodes
        nodes[key] = Node(key, )
        # Start it
        nodes[key].start()


if __name__ == "__main__":
    # validate user input
    if len(sys.argv) < 2:
        print("you must specify a path to your input json")
        exit(0)
    # get data
    with open(sys.argv[1]) as json_file:
        txs = json.loads(json_file.read())
    NUM_NODES = 3
    driver(txs, NUM_NODES)
