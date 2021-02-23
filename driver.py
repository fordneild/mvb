import time
import json
import sys
import random
import txGenerator
from Node import HonestNode, MaliciousNode

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
    STOP_LENGTH_CHAIN = 3
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
                if(len(honest_node.chain) >= STOP_LENGTH_CHAIN):
                    toRemove = honest_node_id
                    break
            if(toRemove):
                honest_nodes_left_to_finish.remove(toRemove)
    # wait for all nodes to stop
    for node in nodes.items():
        node.join()
    print('all done!')

def idxToKey(idx):
    return 'Node' + str(idx)

def startNodes(numHonest, numMalicious, genesisBlock):
    honest_node_ids = set()
    for i in range(numHonest):
        key = idxToKey(i)
        honest_node_ids.add(key)
        # Create node in thread
        global nodes
        nodes[key] = HonestNode(key, genesisBlock)
        # Start it
        nodes[key].start()
    
    for i in range(numMalicious):
        key = idxToKey(i)
        # Create node in thread
        global nodes
        nodes[key] = MaliciousNode(key, genesisBlock)
        # Start it
        nodes[key].start()
    return honest_node_ids


def setupTxs():
    return txGenerator.main()

if __name__ == "__main__":
    # create genesis block
    # validate user input
    if len(sys.argv) < 2:
        print("you must specify a path to your input json")
        exit(0)
    # get data
    with open(sys.argv[1]) as json_file:
        txs = json.loads(json_file.read())
    NUM_NODES = 3
    genesisBlock = setupTxs()
    driver(txs, NUM_NODES, genesisBlock)
