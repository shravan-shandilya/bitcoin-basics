import struct,base58,hashlib,ecdsa
from opcodes import opcodes

class Transaction(object):
	def __init__(self):
		self.version = struct.pack("<L",1)
		self.txn_inputs_count = struct.pack("<B",0)
		self.txn_inputs = []
		self.txn_outputs_count = 0
		self.txn_outputs = []
		self.locktime = struct.pack("<L",0)

	def add_input(self,sender_address,prv_output_hash,index):
		self.txn_inputs_count = struct.pack("<B",struct.unpack("<B",self.txn_inputs_count)[0]+1)
		txn_input = {}
		txn_input["output_hash"] = self.flip_byte_order(prv_output_hash).decode("hex")
		txn_input["output_index"] = struct.pack("<L",index)
		txn_input["script"] = self.generate_redeem_script(sender_address).decode("hex")
		txn_input["script_bytes"] = struct.pack("<B",len(txn_input["script"]))
		txn_input["scriptSig"] = ""
		txn_input["scriptSigBytes"] = struct.pack("<B",len(txn_input["scriptSig"]))
		txn_input["sequence"] = "FFFFFFFF".decode("hex")
		self.txn_inputs.append(txn_input)

	def add_output(self,value,recipient_public_key):
		self.txn_outputs_count += 1
		txn_output = {}
		txn_output["value"] = struct.pack("<Q",value)
		txn_output["scriptPubKey"] = self.generate_redeem_script(recipient_public_key).decode("hex")
		txn_output["scriptPubKeyBytes"] = struct.pack("<B",len(txn_output["scriptPubKey"]))
		self.txn_outputs.append(txn_output)

	def add_op_return_output(self,data=None,file_path=None,raw=None):
		self.txn_outputs_count += 1
		if not data and file_path:
			data = file(file_path,"r").read()
		txn_output = {}
		txn_output["value"] = struct.pack("<Q",0)
		if raw:
			txn_output["scriptPubKey"] = (opcodes["OP_RETURN"] + hex(len(raw)).split("x")[1] + raw.encode("hex")).decode("hex")
		else:
			txn_output["scriptPubKey"] = self.generate_op_return_script(data).decode("hex")
		txn_output["scriptPubKeyBytes"] = struct.pack("<B",len(txn_output["scriptPubKey"]))
		self.txn_outputs.append(txn_output)

	def flip_byte_order(self,string):
		flipped = "".join(reversed([string[i:i+2] for i in range(0, len(string), 2)]))
		return flipped

	def generate_redeem_script(self,recipient_public_key):
		scriptPubKey = ""
		pubKeyHash = base58.b58decode_check(recipient_public_key)[1:].encode("hex")
		scriptPubKey = opcodes["OP_DUP"] + opcodes["OP_HASH160"] + "14" + pubKeyHash + opcodes["OP_EQUALVERIFY"] + opcodes["OP_CHECKSIG"]
		return scriptPubKey

	def generate_op_return_script(self,data):
		hashed_data = hashlib.sha256(hashlib.sha256(data).digest()).digest().encode("hex")
		return opcodes["OP_RETURN"] +"28" + "DOCPROOF".encode("hex") + hashed_data

	def get_raw_transaction(self):
		self.raw_transaction = ""
		self.raw_transaction = (
					self.version
					+ self.txn_inputs_count
					+ self.txn_inputs[0]["output_hash"]
					+ self.txn_inputs[0]["output_index"]
					+ self.txn_inputs[0]["script_bytes"]
					+ self.txn_inputs[0]["script"]
					+ self.txn_inputs[0]["sequence"]
				)

		print self.txn_outputs_count,len(self.txn_outputs)
		assert self.txn_outputs_count == len(self.txn_outputs)
		self.raw_transaction += struct.pack("<B",self.txn_outputs_count)
		for i in range(len(self.txn_outputs)):
			self.raw_transaction = (
						self.raw_transaction
						+ self.txn_outputs[i]["value"]
						+ self.txn_outputs[i]["scriptPubKeyBytes"]
						+ self.txn_outputs[i]["scriptPubKey"]
					)
		self.raw_transaction += self.locktime
		self.raw_transaction += struct.pack("<L",1)
		return self.raw_transaction

	def generate_sig_script(self,account):
		raw_tx = self.get_raw_transaction()
		hashed_tx = hashlib.sha256(hashlib.sha256(raw_tx).digest()).digest()
		signing_key = ecdsa.SigningKey.from_string(account.get_bitcoin_private_key().decode("hex"),curve = ecdsa.SECP256k1)
		verifying_key = signing_key.verifying_key
		public_key = ('\04'+verifying_key.to_string()).encode("hex")
		signature = signing_key.sign_digest(hashed_tx,sigencode = ecdsa.util.sigencode_der)+'\01' #'\01' is a part of signature
		self.txn_inputs[0]["signature"] = signature
		sigscript = (struct.pack("<B",len(signature))+signature + struct.pack("<B",len(public_key.decode("hex"))) + public_key.decode("hex"))
		self.txn_inputs[0]["sigScript"] = sigscript
		self.txn_inputs[0]["sigScriptBytes"] = struct.pack("<B",len(sigscript))
		return sigscript

	def get_real_transaction(self,account):
		sigscript = self.generate_sig_script(account)
		self.real_transaction = ""
		self.real_transaction = (
					self.version
					+ self.txn_inputs_count
					+ self.txn_inputs[0]["output_hash"]
					+ self.txn_inputs[0]["output_index"]
					+ self.txn_inputs[0]["sigScriptBytes"]
					+ self.txn_inputs[0]["sigScript"]
					+ self.txn_inputs[0]["sequence"]
				)
		self.real_transaction += struct.pack("<B",self.txn_outputs_count)
		for i in range(self.txn_outputs_count):
			self.real_transaction = (
				self.real_transaction
				+ self.txn_outputs[i]["value"]
				+ self.txn_outputs[i]["scriptPubKeyBytes"]
				+ self.txn_outputs[i]["scriptPubKey"]
			)
		self.real_transaction += self.locktime
		return self.real_transaction
