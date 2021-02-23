from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from txGenerator import generate_hash
class Transaction:
    def __init__(self, tx):
        # TODO validate tx
        print("creating tx from " + str(tx))
        self.input = tx['input']
        self.number = tx['number']
        self.output = tx['output']
        self.sig = tx['sig']
        self.validate()

    def netTx(tx):
        net = {}
        for i in tx.input:
            output = i['output']
            senderPk = output['pubkey']
            sendAmount = output['value']
            if senderPk not in net:
                net[senderPk] = 0
            net[senderPk] -= sendAmount
        for o in tx.output:
            receiverPk = o['pubkey']
            receiveAmount = o['value']
            if receiverPk not in net:
                net[receiverPk] = 0
            net[receiverPk] += receiveAmount
        return net

    def validate(self):
        # if not valid, throw error
        if len(self.input) == 0:
            raise Exception
        elif len(self.output) == 0:
            raise Exception
        elif not self.sig:
            raise Exception
        elif not self.number:
            raise Exception

        hexHash = generate_hash([self.input.encode('utf-8'), self.output.encode('utf-8'), HexEncoder.decode(self.sig.signature)])

        if self.number != hexHash:
            raise Exception
        totalInOut = 0
        for val in Transaction.netTx(self):
            totalInOut += val
        if totalInOut != 0:
            raise Exception

        vk = VerifyKey(self.input[0][1][1], encoder=HexEncoder)
        vk.verify(self.sig, encoder=HexEncoder)

