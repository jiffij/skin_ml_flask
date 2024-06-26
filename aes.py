import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode())).decode("utf-8")
        # return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        # enc = enc.encode("utf-8")
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
    
    def encrypt_json(self, enc):
        # print("before", enc)
        for i in enc:
            if isinstance(enc[i], dict):
                enc[i] = self.encrypt_json(enc[i])
            else:
                enc[i] = self.encrypt(enc[i])
        # print("after enc: ", enc)
        return enc

    def decrypt_json(self, enc):
        # my_dictionary = {k: self.decrypt(v) for k, v in enc.items()}
        my_dictionary = {}
        for i in enc:
            if isinstance(enc[i], dict):
                my_dictionary[i] = self.decrypt_json(enc[i])
            else:
                my_dictionary[i] = self.decrypt(enc[i])
        # print(my_dictionary)
        return my_dictionary
