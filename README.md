This is the assignment discription for the mvb (minimum viable blockchain)



Assignment 1
Due: 02/22/2021 at 11:59pm (Note: You have a total of 4 late days that you can divide among the different assignments)w

This assignment exists of two portions, the first part includes 4 questions that you have to answer.
The second portion is a programming assignment, read the instructions closely. Everything should be self contained and easy to run for the checker, don't use any esoteric dependencies or run environments.

Everything should be submitted through Gradescope (Note: Written portion and Programming portion need to be submitted separately through Gradescope.)

Written portion (35 points)
Hash functions (5 points)
Suppose Mallory is launching a new 'secure' messaging app. When Alice installs the app, it creates an account for her on the server using a hash of her phone number. The app then queries the server by sending a hash of each phone number in Alice's contacts to learn which of Alice's friends are already on the platform. The goal is that users can discover their friends without the server learning the contents of every user's address book.

Assuming phone numbers are 10 digits, explain why this does not achieve the intended security goal. How can Mallory act maliciously to determine the phone numbers of every one of Alice's contacts?

Signatures (5 points)
Signature schemes allow for public-key message authentication, meaning that both the integrity and provenance of a message can be checked. However, they are often computationally expensive to compute, especially over large messages.

Given a secure signature scheme and a collision-resistant hash function, explain how you could construct a new secure signature scheme wherein the signature scheme can operate over a smaller input, and informally justify the security of this new scheme. Include an overview of the Sign and Verify operations.

Merkle-Damgård (10 points)
Let h: = {0, 1}n+t → {0, 1}n be a fixed-length compression function. Suppose we forget a few of the important features of the Merkle-Damgård transformation, and construct a hash function H from h as follows:

Let x be the input.
Split x into pieces y0 , x1 , x2 , . . . , xk , where y0 is n bits, and each xi is t bits. The last piece xk should be padded with zeroes if necessary.
For i = 1 to k, set yi = h(yi-1 ||xi ).
Output yk . Basically, it is similar to the Merkle-Damgård transformation, except we loose the IV and the final padding block.
(a) Describe an easy way to find two messages that are broken up into the same number of pieces, which have the same hash value under H.
(b) Describe an easy way to find two messages that are broken up into different number of pieces, which have the same hash value under H. Hint: Pick any string of length n + 2t, then find a shorter string that collides with it. Neither of your collisions above should involve finding a collision in h.
PoW difficulty (10 Points)
We say that a hash function H: PxS → {0, 1}n is proof of work secure with difficulty d (say, d = 250 ) if for a randomly chosen puzzle p ∈ P , it is difficult to find a solution s ∈ S such that H(p||s) < 2n/d in time significantly less than 2n/d . You can verify on your own that if we view a hash function as a Random Oracle, then it indeed satisfies the proof of work security for any suitable choice of parameters. In this question we explore the relation between collision resistance and proof of work security. Show that a collision resistant hash function may not be proof of work secure. Specifically, let H : P × S → {0, 1}n be a collision resistant hash function. Construct a new hash function H' : P × S → {0, 1}n' (where n' may be greater than n) that is also collision resistant, but for a fixed difficulty d is not proof of work secure with difficulty d. This is despite H' being collision resistant. Also, explain why H' is collision resistant, that is, why a collision on H' would yield a collision on H.

Bitcoin (5 points)
Explain qualitatively why the verification of a transaction in the most recently broadcast block is less reliable than one in a block a few prior to the most recent block.

Programming portion (65 points)
Specification

For this program you will write a simulation of a "Minimum Viable Blockchain" (MVB), a simplified version of the technology underlying Bitcoin. You will have nodes which validate transactions, perform proofs of work, and communicate in order to process transactions. This will emulate the mining and transaction verification process of Bitcoin.

Your MVB will implement the following:

Authentic transactions that are resistant to theft
Open competition amongst nodes to validate transactions
Detection of double spending
Use of proof-of-work to raise the cost of running attacks against the network
Detection of and reaction to forks in the chain
Rather than communicating over a network, your simulated nodes will run in threads. Transactions, either valid or intentionally invalid, will be defined in a file which is read by the simulation and provided to the nodes. Your threading should be non-cooperative, which is to say that there should be no synchronization primitives such as locks. This simulates nodes running independent of one another.

You may work with a partner on this program.

Formats

A transaction file will be text/plain JSON data containing a single list as follows:

[{"number": <hash of input, output, and signature fields>,
  "input": [{"number": <transaction number>, "output": {"value": <value>, "pubkey": <sender public key>}}, ...],
  "output": [{"value": <value>, "pubkey": <receiver public key>}, ...],
  "sig": <signature of input and output fields using sender private key>
 }, ...]
where ... implies that there could be an arbitrary number of similar elements in the list. The exception is the first transaction in the file, which will have an empty input list.

A block will be structured as:

{"tx": <a single transaction>,
 "prev": <hash of the previous block>,
 "nonce": <the nonce value, used for proof-of-work>,
 "pow": <the proof-of-work, a hash of the tx, prev, and nonce fields>
}
Hashes should be written as hexadecimal values with no prefix. An example:

# python3
>>> from hashlib import sha256 as H
>>> computed_hash = H(b'hello') # note that the b makes the string a bytes literal
>>> computed_hash.hexdigest()
'2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
Similarly, nonces, signatures, and keys should be formatted as hex. See https://pynacl.readthedocs.io/en/stable/signing/ for an example.

Genesis Block

The first transaction in the transaction file is special:

it does not need to have a valid signature
it will have an empty input list
The first block must contain the first transaction. This block, known as the "Genesis" block, has the following properties:

The prev hash is a hash of arbitrary data
The nonce is an arbitrary value
The pow hash is a hash of arbitrary data
Node behavior

Each node will receive the global Genesis block, and then begin processing transactions from the global unverified transaction pool. Each node should have its own representation of the blockchain at any given time. In order to process a transaction, a node will have to perform the following steps:

Ensure the transaction is not already on the blockchain (included in an existing valid block)
Ensure the transaction is validly structured
number hash is correct
each input is correct
each number in the input exists as a transaction already on the blockchain
each output in the input actually exists in the named transaction
each output in the input has the same public key, and that key can verify the signature on this transaction
that public key is the most recent recipient of that output (i.e. not a double-spend)
the sum of the input and output values are equal
Construct a block containing this transaction, setting prev to the hash of the most recent block
Create a valid proof-of-work for this block by setting nonce and pow
Additionally, each node must periodically check for and react to the broadcast of blocks from other nodes:

Verify the proof-of-work
Verify the prev hash
Validate the transaction in the block
If all three checks pass, append this block to the node's instance of the blockchain, and continue work
Proof-of-Work

In order to be a valid block, the pow value must be less than or equal to the hexadecimal value 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF.

Forking

In the operation of your nodes, forks may occur in your blockchain:

The longest chain is the only valid blockchain
Thus, at any point, any blocks can be invalidated, no block is ever "final"
Each node should work off of the longest chain it is aware of
The contained transaction in an invalidated block become unverified and must be re-added to the global unverified pool by the nodes, if not already there
Forking example (numbers represent blocks in order they are broadcast, and lines represent prev links):

      G
      |
      1
     / \
    2   3
    |   |
    4   5
        |
        6
After 2 and 3 are broadcast (likely at roughly the same time), some nodes might be working off of 2 and some off of 3. Once 4 is broadcast, the transaction in 3 is no longer verified. It is possible (but unlikely) that blocks 5 and 6 might build off of 3 rather than 4, at which point the transactions in both 2 and 4 would be unverified - once that chain no longer represents the longest path back the Genesis block G.

Driver Program

Finally, you are required to write a driver program which, after starting at least 8 nodes, will begin reading the transaction file and populating the global unverified transaction pool. The driver should also create the Genesis block and make it available to the nodes. Nodes should continue processing until all valid transactions in the transaction file are verified. You may implement this by having the driver terminate the node threads. The driver should sleep for a random (changing) time up to 1 second between placing each transaction into the global unverified pool.

Upon termination, each node should write its blockchain to a file. If all has gone well, these files will all be identical, and contain every valid transaction in the transaction file. In the very rare case that two equal-length chains exist when all valid transactions are verified, re-run the entire program.

Output

The blockchain output of each node must be JSON, a list of the described block structures.

Testing

You must generate a transaction file with at least 15 non-Genesis transactions amongst at least 8 different ECDSA keypairs. Use pynacl for ECDSA. Additionally, test with transactions which are invalid for a variety of reasons (double spend, bad structure, missing fields, etc) and ensure these transactions are not accepted by the nodes. Finally, test with some nodes which broadcast invalid blocks to ensure other nodes do not accept these blocks. Again, make these blocks invalid for a variety of reasons.

Notes

It is strongly preferred and recommended that you use Python3 for this project. That said, speak with the TA if you would like to make a case for using another language, but note that likely no debugging/library questions will be considered if you do.

You may wish to implement broadcast as each thread having a thread-safe queue which any node writes to but only it reads from. To broadcast, a node would write to each other node's queue.

Running your program should require no external dependencies or packages, but installation of Python3 packages via pip/pip3 is acceptable. Include a requirements.txt (generated via pip list > requirements.txt).

Resources

https://www.igvita.com/2014/05/05/minimum-viable-block-chain/
https://docs.python.org/3.5/library/venv.html
https://docs.python.org/3.7/library/threading.html
https://en.wikibooks.org/wiki/Python_Programming/Threading
https://docs.python.org/3.7/library/json.html
https://docs.python.org/3/library/hashlib.html
https://pynacl.readthedocs.io/en/stable/
This project was adapted from one developed by Professor Zachary Peterson.

Submission

Provide all code, requirements.txt, and instructions for running your driver program.