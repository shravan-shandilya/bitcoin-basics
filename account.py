import os
from keys import generate_key_pair

class Account(object):
    def __init__(self,nickname,private_key=None,store=True):
        self.nickname = nickname
        self.bitcoin_private,self.bitcoin_public = generate_key_pair(private_key)
	if store:
            self.store()
	
    def store(self):
        if not os.path.exists("./wallet/"+self.nickname):
            os.makedirs("./.wallet/"+self.nickname)
	if not self.bitcoin_private or not self.bitcoin_public:
            print "You need to create bitcoin address before storing it"
	    exit(-1)
        priv_file = file("./.wallet/"+self.nickname+"/bitcoin_private","w+")
        priv_file.write(self.bitcoin_private)
        priv_file.close()

	pub_file = file("./.wallet/"+self.nickname+"/bitcoin_public","w+")
	pub_file.write(self.bitcoin_public)
	pub_file.close()

    def get_bitcoin_public_key():
        return self.bitcoin_public

    def get_bitcoin_private_key():
        return self.bitcoin_private
