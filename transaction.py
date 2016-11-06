import struct,base58,hashlib,ecdsa
from opcodes import opcodes

class Transaction(object):
	def __init__(self):
		self.version = struct.pack("<L",1)
		self.txn_inputs_count = struct.pack("<B",0)
		self.txn_inputs = []
		self.txn_outputs_count = struct.pack("<B",0)
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
		self.txn_outputs_count = struct.pack("<B",struct.unpack("<B",self.txn_outputs_count)[0]+1)
		txn_output = {}
		txn_output["value"] = struct.pack("<Q",value)
		txn_output["scriptPubKey"] = self.generate_redeem_script(recipient_public_key).decode("hex")
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
					+ self.txn_outputs_count
					+ self.txn_outputs[0]["value"]
					+ self.txn_outputs[0]["scriptPubKeyBytes"]
					+ self.txn_outputs[0]["scriptPubKey"]
					+ self.locktime
					+ struct.pack("<L",1)
				)
		return self.raw_transaction

	def generate_sig_script(self,account):
		raw_tx = self.get_raw_transaction()
		hashed_tx = hashlib.sha256(hashlib.sha256(raw_tx).digest()).digest()
		signing_key = ecdsa.SigningKey.from_string(account.get_bitcoin_private_key().decode("hex"),curve = ecdsa.SECP256k1)
		verifying_key = signing_key.verifying_key
		public_key = ('\04'+verifying_key.to_string()).encode("hex")
		signature = signing_key.sign_digest(hashed_tx,sigencode = ecdsa.util.sigencode_der)
		self.txn_inputs[0]["signature"] = signature
		sigscript = (signature + "\01" + struct.pack("<B",len(public_key.decode("hex"))) + public_key.decode("hex"))
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
					+ self.txn_outputs_count
					+ self.txn_outputs[0]["value"]
					+ self.txn_outputs[0]["scriptPubKeyBytes"]
					+ self.txn_outputs[0]["scriptPubKey"]
					+ self.locktime
				)
		return self.real_transaction
