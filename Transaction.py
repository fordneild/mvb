from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from txGenerator import generate_hash
import json


class Transaction:
    def __init__(self, tx):
        # TODO validate tx
        # print("creating tx from " + str(tx))
        self.input = tx['input']
        self.number = tx['number']
        self.output = tx['output']
        self.sig = tx['sig']
        self.validate()

    def netTx(self):
        net = {}
        for i in self.input:
            output = i['output']
            senderPk = output['pubkey']
            sendAmount = output['value']
            if senderPk not in net:
                net[senderPk] = 0
            net[senderPk] -= sendAmount
        for o in self.output:
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

        print(self.input)
        print(self.output)
        print(self.sig)

        hexHash = generate_hash(
            [json.dumps(self.input).encode('utf-8'), json.dumps(self.output).encode('utf-8'), self.sig.encode('utf-8')]
        )

        if self.number != hexHash:
            raise Exception
        totalInOut = 0
        res = self.netTx()
        print('DEBUG',res,type(res))
        for val in res.values():
            totalInOut += val
        if totalInOut != 0:
            raise Exception

        msg = json.dumps(self.output).encode('utf-8')
        msg += json.dumps(self.input).encode('utf-8')
        vk = self.input[0]['output']['pubkey'].verify(msg, self.sig, encoder=HexEncoder)
