#!/usr/bin/python
import os,ecdsa,hashlib,base58

priv_key = os.urandom(32)
print "Priv_key(hex): ",priv_key.encode("hex")," Length:",len(priv_key),"bytes"

signing_key = ecdsa.SigningKey.from_string(priv_key,ecdsa.SECP256k1)

verifying_key = signing_key.verifying_key.to_string()
print "Pub_key(hex): ",verifying_key.encode("hex")," Length:",len(verifying_key),"bytes"

intermediate1 = "\04"+verifying_key
print "Pub_key(hex) [added 0x04]: ",intermediate1.encode("hex")," Length:",len(intermediate1),"bytes"

ripemd160 = hashlib.new("ripemd160")

temp1 = hashlib.sha256(intermediate1).digest()

ripemd160.update(temp1)
intermediate2 = ripemd160.digest()
print "Pub_key(hex) [ripemd160(sha256(previous_key))]: ",intermediate2.encode("hex")," Length:",len(intermediate2),"bytes"

intermediate3 = "\00"+intermediate2
print "Pub_key(hex) [added network byte 0x00]: ",intermediate3.encode("hex")," Length:",len(intermediate3),"bytes"


temp2 = hashlib.sha256(intermediate3).digest()
intermediate4 = hashlib.sha256(temp2).digest()
checksum = intermediate4[:4]

intermediate5 = intermediate3+checksum
print "Pub_key(hex) [added checksum]: ",intermediate5.encode("hex")," Length:",len(intermediate5),"bytes","Checksum: ",checksum.encode("hex")

bitcoin_address = base58.b58encode(intermediate5)
print "Bitcoin address: [converted to base58]",bitcoin_address," Length:",len(bitcoin_address),"bytes"
