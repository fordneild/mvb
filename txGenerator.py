import hashlib
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
import os
import json


class User:
    def __init__(self, name):
        self.name = name
        self.sk = SigningKey.generate()
        self.vk = self.sk.verify_key.encode(encoder=HexEncoder).decode('utf-8')


class Transaction:
    def __init__(self, input, number, output, sig):
        self.input = input
        self.number = number
        self.output = output
        self.sig = sig


# TODO fix
def generate_hash(secrets):
    dk = hashlib.sha256()
    # ERROR
    #   File "/Users/fordneild/workdir/blockchain/mvb/txGenerator.py", line 26, in generate_hash
    #     dk.update(s)
    # TypeError: object supporting the buffer API required
    for s in secrets:
        dk.update(s)
    return dk.hexdigest()


# QUESTION: Should this live in the user class? Can we have a users without these fields? Is there a benefit to doing them all at once?
# generates and saves signing keys (private) and verify (public) keys for all users
# signatures/keys are all encoded in HexEncoder
# def generateSkVk(users):
#     for u in users:
#         tempSk = SigningKey.generate()
#         u.sk = tempSk
#         # QUESTION: [tempSk.verify_key] vs [from nacl.signing import VerifyKey]?
#         tempPk = tempSk.verify_key
#         u.vk = tempPk.encode(encoder=HexEncoder)


# generates output file with a list of transactions based on specified transactions including genesis transaction
def generateTransactionList(users, outFilename):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, outFilename)

    f = open(abs_file_path, "w")
    f.write("[\n")
    # genesis block/transaction
    genesisBlock = generateTransaction([], [], [users[0]], [], [100], True)
    # print(buildJsonTransaction(genesisBlock), file=f)

    # all other transactions
    tx1 = generateTransaction([users[0]], [genesisBlock.number],
                              [users[0], users[1]], [100], [70, 30], False)  # Bob is paying Alice 30
    print(buildJsonTransaction(tx1), file=f)

    tx2 = generateTransaction([users[0]], [tx1.number],
                              [users[0], users[2]], [70], [40, 30], False)  # Bob is paying Steve 30
    print(buildJsonTransaction(tx2), file=f)

    tx3 = generateTransaction([users[2]], [tx2.number],
                              [users[2], users[3]], [30], [20, 10], False)  # Steve is paying Phil 10
    print(buildJsonTransaction(tx3), file=f)

    malTx1 = generateTransaction([users[6]], [tx1.number],
                                 [users[6], users[7]], [10], [5, 5], False)  # BAD TX: Stacy (no coins) paying Candice 5
    print(buildJsonTransaction(malTx1), file=f)

    tx4 = generateTransaction([users[0]], [tx2.number],
                              [users[0], users[5]], [40], [25, 15], False)  # Bob is paying John 15
    print(buildJsonTransaction(tx4), file=f)

    tx5 = generateTransaction([users[1]], [tx1.number],
                              [users[1], users[4]], [30], [15, 15], False)  # Alice is paying Barbara 15
    print(buildJsonTransaction(tx5), file=f)

    tx6 = generateTransaction([users[2]], [tx3.number],
                              [users[2], users[6]], [20], [15, 5], False)  # Steve is paying Stacy 5
    print(buildJsonTransaction(tx6), file=f)

    malTx2 = generateTransaction([users[6]], ['0'],
                                   [users[6], users[7]], [10], [5, 5], False)  # BAD TX: Invalid input transaction number
    print(buildJsonTransaction(malTx2), file=f)

    tx7 = generateTransaction([users[0]], [tx4.number],
                              [users[0], users[7]], [25], [15, 10], False)  # Bob paying Candice 10
    print(buildJsonTransaction(tx7), file=f)

    tx8 = generateTransaction([users[2]], [tx6.number],
                              [users[2], users[0]], [15], [10, 5], False)  # Steve is paying Bob 5
    print(buildJsonTransaction(tx8), file=f)

    tx9 = generateTransaction([users[5]], [tx4.number],
                              [users[5], users[6]], [15], [10, 5], False)  # John is paying Stacy 5
    print(buildJsonTransaction(tx9), file=f)

    malTx3 = generateTransaction([users[6]], [tx9.number],
                                 [users[6], users[7]], [10], [6, 5], False)  # BAD TX: Inputs outputs dont add up
    print(buildJsonTransaction(malTx3), file=f)

    tx10 = generateTransaction([users[4]], [tx5.number],
                               [users[4], users[3]], [15], [10, 5], False)  # Barbara is paying Phil 5
    print(buildJsonTransaction(tx10), file=f)

    tx11 = generateTransaction([users[6]], [tx6.number, tx9.number],
                               [users[4]], [5, 5], [10], False)  # Stacy is paying Barbara 10
    print(buildJsonTransaction(tx11), file=f)

    tx12 = generateTransaction([users[7]], [tx7.number],
                               [users[5]], [10], [10], False)  # Candice is paying John 10
    print(buildJsonTransaction(tx12), file=f)

    malTx4 = generateTransaction([users[7]], [tx7.number],
                                 [users[6]], [10], [10], False)  # BAD TX: Candice trying to double spend
    print(buildJsonTransaction(malTx4), file=f)

    tx13 = generateTransaction([users[5]], [tx9.number, tx12.number],
                               [users[2]], [10, 10], [20], False)  # John is paying Steve 20
    print(buildJsonTransaction(tx13), file=f)

    tx14 = generateTransaction([users[4]], [tx10.number, tx11.number],
                               [users[1]], [10, 10], [20], False)  # Barbara is paying Alice 20
    print(buildJsonTransaction(tx14), file=f)

    tx15 = generateTransaction([users[2]], [tx8.number, tx13.number],
                               [users[2], users[0]], [10, 20], [15, 15], False)  # Steve is paying Bob 15
    print(buildJsonTransaction(tx15)[:-1], file=f)

    f.write("]")
    f.close()
    return genesisBlock


def generateTransaction(sUsers, sTxs, rUsers, valuesSent, valuesReceived, genesis):
    # generate input
    input = []
    index = 0
    for s in sTxs:
        json_temp = '{"number": "' + s + '", "output": {"value": ' + str(
            valuesSent[index]) + ', "pubkey": "' + str(sUsers[0].vk) + '"}}'
        index += 1
        # print(json_temp)
        input.append(json.loads(json_temp))

    # print(json.dumps(input))
    # generate output
    output = []
    index = 0
    for r in rUsers:
        json_temp = '{"value": ' + str(valuesReceived[index]) + ', "pubkey": "' + str(r.vk) + '"}'
        index += 1
        output.append(json.loads(json_temp))

    # print(json.dumps(output))
    if genesis:
        # generates an invalid signature, can also be used for testing
        user = User("Genesis")
        user.vk = rUsers[0].vk
        signature = generateSignature(json.dumps(input), json.dumps(output), user)
    else:
        signature = generateSignature(json.dumps(input), json.dumps(output), sUsers[0])
    concatSig = signature.signature + signature.message
    number = generate_hash(
        [json.dumps(input).encode('utf-8'), json.dumps(output).encode('utf-8'), concatSig]
    )

    # print(output)
    # print(str(signature))

    return Transaction(input, number, output, concatSig.decode('utf-8'))


def generateSignature(input, output, user):
    temp = input.encode('utf-8')
    temp += output.encode('utf-8')
    signature = user.sk.sign(temp, encoder=HexEncoder)
    return signature


def buildJsonTransaction(tx):
    # print(str(tx.number))
    # print(str(tx.input)[1:-1])
    # print(str(tx.output)[1:-1])
    # print(str(tx.sig))
    fullTx = '{"number":"' + str(tx.number) + '", "input": [' + str(
        json.dumps(tx.input)[1:-1]) + '], "output": [' + str(json.dumps(tx.output)[1:-1]) + '], "sig": "' + str(tx.sig) \
             + '"},'
    return fullTx


def main(file_name):
    names = ['Bob', 'Alice', 'Steve', 'Phil', 'Barbara', 'John', 'Stacy', 'Candice']
    users = []

    # make user objects from list of names and append to list of users
    for n in names:
        users.append(User(n))

    # generate and save public and secret keys for all users
    # generateSkVk(users)

    # generate an output file with a list of legitimate and illegitimate transactions
    return generateTransactionList(users, file_name)


if __name__ == "__main__":
    main("input/transactions.json")
