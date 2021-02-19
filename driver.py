import threading
import time
import queue
import json
import sys
import random

# these varibales are globally accessible to all nodes
stop_threads = False
nodes = {}
unverifiedTxs = {}

# driver takes transactions and number of nodes to process them


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


class Node(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        # Each Node has a Queue to track incoming blocks from other
        self.q = queue.Queue()
        self.seenTxNums = set()

    def run(self):
        # target function of the thread class
        try:
            print(self.name + " running...")
            while True:
                # process all new blocks in queue
                while(not self.q.empty()):
                    self.processBlock()
                # process any new unverified transactions
                self.processUnverifiedTransactions()
                global stop_threads
                if stop_threads:
                    break
        finally:
            print(self.name + " stopped")

    def processUnverifiedTransactions(self):
        global unverifiedTxs
        for (unverifiedTxNum, unverifiedTx) in unverifiedTxs.items():
            if(unverifiedTxNum not in self.seenTxNums):
                self.seenTxNums.add(unverifiedTxNum)
                self.processUnverifiedTransaction(unverifiedTx)
                # important that we only process one new transaction
                # other nodes mat have new blocks for us
                break

    def processUnverifiedTransaction(self, transaction):
        print(self.name + " is processing new transaction " + str(transaction))

    def addBlockToQueue(self, block):
        # target function of the thread class
        self.q.put(block)

    def processBlock(self):
        # target function of the thread class
        block = self.q.get()
        print(self.name + " recieved block " + block)

    def broadcastBlock(self, block):
        print(self.name + " broadcasting block " + block)
        global nodes
        for nodeKey, node in nodes.items():
            if(nodeKey != self.name):
                node.addBlockToQueue(block)


def idxToKey(idx):
    return 'Node'+str(idx)


def startNodes(num):
    for i in range(num):
        key = idxToKey(i)
        # Create node in thread
        global nodes
        nodes[key] = Node(key)
        # Start it
        nodes[key].start()


if(__name__ == "__main__"):
    # validate user input
    if(len(sys.argv) < 2):
        print("you must specify a path to your input json")
        exit(0)
    # get data
    with open(sys.argv[1]) as json_file:
        txs = json.loads(json_file.read())
    NUM_NODES = 3
    driver(txs, NUM_NODES)
