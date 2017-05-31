from transaction import Transaction
from account import Account
from messages import TransactionMessage
import ecdsa,hashlib,struct
ref_txn_hash = "b93ba975d8cf7b71cfec5116f1ed83a187d2f3e840801fff6b57c119d0023d11"
ref_txn_index = 0
sender_address = "1N4MvxDTrAi7rPQP2bZgcidiapTf9iJdU5"

transfer_value = 80000
recipient_address = "3LZKm2PMEbv94kSboz5m1EGBW7sUDAhAFT"

t = Transaction()
t.add_input(sender_address,ref_txn_hash,ref_txn_index)
t.add_output(transfer_value,recipient_address)
t.add_op_return_output(raw="@bitaccess @iam5hravan Interested and I'm already liking it!")
#t.add_op_return_output(file_path="./main.py")
#t.add_op_return_output(data="this is getting better")
#t.add_output(transfer_value,recipient_address)

payload = t.get_real_transaction(Account("raw",create=True))
print "Raw-transaction:",payload.encode("hex")

tx_msg = TransactionMessage(payload)
print "Transaction on wire:",tx_msg.get_raw_msg().encode("hex")
