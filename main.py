from transaction import Transaction
from account import Account
import ecdsa,hashlib,struct
ref_txn_hash = "6c2896fdb7d026baf5283da722b95b6ad271219b1aeeab4b5cbcd089085780f5"
ref_txn_index = 2
sender_address = "1Dsj6zAuZjeszLuhsM26vaNUkiSw2rDwfH"

transfer_value = 80000
recipient_address = "1513wD3VQiqkqYUkeL1w8o6BPxE62d6N1g"

t = Transaction()
t.add_input(sender_address,ref_txn_hash,ref_txn_index)
t.add_output(transfer_value,recipient_address)
print t.get_real_transaction(Account("raw")).encode("hex")
print t.get_raw_transaction().encode("hex")
