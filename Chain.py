from Transaction import Transaction
from Block import Block
import copy

class Chain:
    def __init__(self, genesisBlock: Block):
        self.blocks = [genesisBlock]
        self.unspentTx2BlockIdx = {}

    def addTx(self, rawTx):
        try:
            tx = Transaction(rawTx)
            lastBlockHash = self.blocks[len(self.blocks) - 1].hash()
            newBlock = Block(tx, lastBlockHash)
            self.unspentTx2BlockIdx = Chain.validateBlock(self.blocks, newBlock, self.unspentTx2BlockIdx)
            self.blocks.append(newBlock)
            return True
        except:
            return False

    def hasTx(self, txNum):
        return txNum in self.tx


    def validateBlock(blocks, newBlock: Block, unspentTx2BlockIdx):
        assert len(blocks) > 0
        newUnspentTx2BlockIdx = copy.deepcopy(unspentTx2BlockIdx)
        newTx = newBlock.tx
        newTxInputNum  = newTx.input[0]
        if(newTxInputNum not in unspentTx2BlockIdx):
            raise Exception("Either a double spend or new block is spending money that was never made")
        claimedBlockIndex = unspentTx2BlockIdx[newTxInputNum]
        claimedBlock = blocks[claimedBlockIndex]
        # the output they recieved is equal to what they want to spend
        claimedTxOuputs = claimedBlock.tx.output
        foundOutput = False
        for output in claimedTxOuputs:
            if(output['pubkey'] == newTx.input[0]['pubkey'] and output['value'] == newTx.input[0]['value']):
                foundOutput = True
        if(not foundOutput):
            raise Exception("user " + newTx.input[0]['pubkey'] + " does not have money they are claiming")
        return newUnspentTx2BlockIdx


    def validateChain(blocks, genesisBlock):
        try:
            if (blocks[0].hash() != genesisBlock.hash()):
                return False
            # we have the same genesis
            builtBlocks = [genesisBlock]
            unspentTx2BlockIdx = {}
            for block in blocks[1:]:
                if block.pow < 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    unspentTx2BlockIdx = Chain.validateBlock(builtBlocks, block, unspentTx2BlockIdx)
                    if(not unspentTx2BlockIdx):
                        raise Exception("Incoming chain was found to have invalid block")
                    else:
                        builtBlocks.append(block)
            return True
        except:
            return False