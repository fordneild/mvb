from txGenerator import generate_hash
from Transaction import Transaction
from Block import Block
import copy

class Chain:
    def __init__(self, genesisBlock: Block):
        self.blocks = [genesisBlock]
        self.unspentCoin2BlockIdx = {}

    def addTx(self, rawTx):
        tx = Transaction(rawTx)
        lastBlockHash = self.blocks[len(self.blocks) - 1].hash()
        newBlock = Block(tx, lastBlockHash)
        self.unspentCoin2BlockIdx = Chain.validateBlock(self.blocks, newBlock, self.unspentCoin2BlockIdx)
        self.blocks.append(newBlock)
        return True


    def validateBlock(blocks, newBlock: Block, unspentCoin2BlockIdx):
        assert len(blocks) > 0
        newUnspentCoin2BlockIdx = copy.deepcopy(unspentCoin2BlockIdx)
        newTx = newBlock.tx
        senderPk  = newTx.input[0].output.pubkey
        for nextTxInput in newTx.input:
            newTxInputNum  = nextTxInput.number
            key = generate_hash([newTxInputNum,senderPk])
            # i am claiming to use this coin
            if(key not in unspentCoin2BlockIdx):
                raise Exception("Either a double spend or new block is spending money that was never made")
            claimedBlockIndex = unspentCoin2BlockIdx[newTxInputNum]
            claimedBlock = blocks[claimedBlockIndex]
            # the output they recieved is equal to what they want to spend
            claimedTxOuputs = claimedBlock.tx.output
            foundOutput = False
            for output in claimedTxOuputs:
                if(output['pubkey'] == nextTxInput['pubkey'] and output['value'] == nextTxInput['value']):
                    foundOutput = True
            if(not foundOutput):
                raise Exception("user " + nextTxInput['pubkey'] + " does not have money they are claiming")
            # remove the spend coin from this tx
            del newUnspentCoin2BlockIdx[key]
        # and we add back all the coins in this tx output
        for output in newBlock.tx.output:
            recieverKey= output.pubkey
            newKey = generate_hash([newTx.number,recieverKey])
            newUnspentCoin2BlockIdx[newKey] = len(blocks)
        return newUnspentCoin2BlockIdx


    def validateChain(blocks, genesisBlock):
        try:
            if (blocks[0].hash() != genesisBlock.hash()):
                return False
            # we have the same genesis
            builtBlocks = [genesisBlock]
            unspentCoin2BlockIdx = {}
            for block in blocks[1:]:
                if block.pow < 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    unspentCoin2BlockIdx = Chain.validateBlock(builtBlocks, block, unspentCoin2BlockIdx)
                    if(not unspentCoin2BlockIdx):
                        raise Exception("Incoming chain was found to have invalid block")
                    else:
                        builtBlocks.append(block)
            return True
        except:
            return False