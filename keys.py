#!/usr/bin/python
import os,ecdsa,hashlib,base58

def generate_key_pair(private_key):
    if not private_key:
        priv_key = os.urandom(32)
    else:
        priv_key = private_key.decode("hex")
    signing_key = ecdsa.SigningKey.from_string(priv_key,ecdsa.SECP256k1)
    verifying_key = signing_key.verifying_key.to_string()
    intermediate1 = "\04"+verifying_key
    ripemd160 = hashlib.new("ripemd160")
    temp1 = hashlib.sha256(intermediate1).digest()
    ripemd160.update(temp1)
    intermediate2 = ripemd160.digest()
    intermediate3 = "\00"+intermediate2
    temp2 = hashlib.sha256(intermediate3).digest()
    intermediate4 = hashlib.sha256(temp2).digest()
    checksum = intermediate4[:4]
    intermediate5 = intermediate3+checksum
    bitcoin_address = base58.b58encode(intermediate5)
    return priv_key.encode("hex"),bitcoin_address
