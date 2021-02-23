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
