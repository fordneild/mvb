import hashlib
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
import json
import os


class User:
    def __init__(self, name):
        self.name = name
        self.sk = SigningKey.generate()
        self.vk = self.sk.verify_key.encode(encoder=HexEncoder)


class Transaction:
    def __init__(self, input, number, output, sig):
        self.input = input
        self.number = number
        self.output = output
        self.sig = sig


def generate_hash(secrets):
    dk = hashlib.sha256()
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
def generateTransactionList(users):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    outFilename = "transactions.json"
    rel_path = "input/" + outFilename
    abs_file_path = os.path.join(script_dir, rel_path)

    f = open(abs_file_path, "w")
    f.write("[\n")
    # genesis block/transaction
    genesisBlock = generateTransaction([], [], users, [1, 1, 1, 1, 1, 1, 1, 1], True)

    # all other transactions
    tx = generateTransaction([users[3]], ["bc9dde8f88cd0680819b112df41b71f5b2d57c4f0462d408b6dfd508040d0538"],
                             [users[4]], [1], False)  # Phil is paying Barbara 1
    print(buildJsonTransaction(tx), file=f)



    tx = generateTransaction([users[4]], ["a578ab2a1b3eadc0d018c02b08df5e2267803548ee57edf927e72270b05e3dd6"],
                             [users[2]], [1], False)  # Barbara is paying Steve 2
    print(buildJsonTransaction(tx)[:-1], file=f)
    f.write("]")
    f.close()
    return genesisBlock


def generateTransaction(sUsers, sTxs, rUsers, values, genesis):
    # generate input
    input = '[\n'
    index = 0
    for s in sUsers:
        input += '            {\n                "number": \"' + sTxs[index] + '\",\n                "output": {"value": ' + str(values[
            index]) + ', "pubkey": \"' + str(s.vk) + '\"}\n            },\n'
        index += 1
    if index > 0:
        input = input[: -2]
    input += '\n        ]'
    if genesis:
        input = '[]'

    # generate output
    output = '[\n'
    index = 0
    for r in rUsers:
        output += '            {"value": ' + str(values[index]) + ', "pubkey": \"' + str(r.vk) + '\"},'
        index += 1
    if index > 0:
        output = output[: -1]
    output += '\n        ]'

    if genesis:
        signature = generateSignature(input, output, rUsers[0])
    else:
        signature = generateSignature(input, output, sUsers[0])
    number = generate_hash([input.encode('utf-8'), output.encode('utf-8'), HexEncoder.decode(signature.signature)])
    return Transaction(input, number, output, signature)


def generateSignature(input, output, user):
    temp = input.encode('utf-8')
    temp += output.encode('utf-8')
    signature = user.sk.sign(temp, encoder=HexEncoder)
    return signature


def buildJsonTransaction(tx):
    return "    {\n        \"number\": \"" + str(tx.number) + \
           "\",\n        \"input\": " + tx.input + \
           ",\n        \"output\": " + tx.output + \
           ",\n        \"sig\": \"" + str(tx.sig) + \
           "\"\n    },"


def main():
    names = ['Bob', 'Alice', 'Steve', 'Phil', 'Barbara', 'John', 'Stacy', 'Candice']
    users = []

    # make user objects from list of names and append to list of users
    for n in names:
        users.append(User(n))

    # generate and save public and secret keys for all users
    # generateSkVk(users)

    # generate an output file with a list of legitimate and illegitimate transactions
    return generateTransactionList(users)


if __name__ == "__main__":
    main()
