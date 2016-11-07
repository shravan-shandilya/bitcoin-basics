import struct,time,random,hashlib


class Message(object):
    def __init__(self,net,command):
        if net == "main":
	    self.magic = "F9BEB4D9".decode("hex")
	elif net == "test":
	    self.magic = "FABFB5DA".decode("hex")
	elif net == "test3":
	    self.magic = "0B110907".decode("hex")
	elif net == "namecoin":
	    self.magic = "F9BEB4FE".decode("hex")
	else:
	    print "Magic not found! Available [main,test,test3,namecoin]"
        self.command = command + (12-len(command))*"\00" #Null padding
    def add_payload(self,payload):
        self.payload = payload
        self.checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        self.payload_size = struct.pack("I",len(payload))
    def get_raw_msg(self):
        self.raw = self.magic + self.command + self.payload_size + self.checksum + self.payload
        return self.raw
    def load_header(self,raw):
        self.magic = raw[:4]
	self.command = raw[4:16]
        self.payload_size = struct.unpack(">I",raw[16:20])[0]
	self.checksum = raw[20:24]
	self.payload = raw[24:24+self.payload_size]
	if not self.verify_checksum(self.payload,self.checksum):
            print "Checksum failed"

    def verify_checksum(self,payload,checksum):
        return checksum == hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

class VersionMessage(Message):
   def __init__(self):
       self.protocol_version = struct.pack("i",70014)
       self.services = struct.pack("Q",0)
       self.timestamp = struct.pack("q",time.time())
       self.addr_recv_services = struct.pack("Q",0)
       self.addr_recv_ip = struct.pack(">16s","127.0.0.1")
       self.addr_recv_port = struct.pack(">H",8333)
       self.addr_trans_services = struct.pack("Q",0)
       self.addr_trans_ip = struct.pack(">16s","127.0.0.1")
       self.addr_trans_port = struct.pack(">H",8333)
       self.nonce = struct.pack("Q",random.getrandbits(64))
       self.user_agent_bytes = struct.pack("B",0)
       self.starting_height = struct.pack("i",437419)
       self.relay = struct.pack("?",False)
       
       payload = self.protocol_version + self.services + self.timestamp + self.addr_recv_services + self.addr_recv_ip + self.addr_recv_port + self.addr_trans_services + self.addr_trans_ip + self.addr_trans_port + self.nonce + self.user_agent_bytes + self.starting_height + self.relay
       
       super(VersionMessage,self).__init__("main","version")
       self.add_payload(payload)
   def load(self,raw):
       self.load_header(raw)

class TransactionMessage(Message):
   def __init__(self,raw_tx):
       self.add_payload(raw_tx)
       super(TransactionMessage,self).__init__("main","tx")
