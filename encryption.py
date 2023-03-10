import base64
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher

def get_key(key_file, str_format = False):
    with open(key_file) as f:
        data = f.read()
        key = RSA.importKey(data)
    if(str_format):
        return data
    return key

def encrypt_data(msg):
    public_key = get_key('assets/rsa_public_key.pem')
    cipher = PKCS1_cipher.new(public_key)
    encrypt_text = base64.b64encode(cipher.encrypt(bytes(msg.encode("utf8"))))
    return encrypt_text.decode('utf-8')

def encrypt_data_wth_client_key(msg, key):
    client_key = RSA.importKey(key)
    cipher = PKCS1_cipher.new(client_key)
    encrypt_text = base64.b64encode(cipher.encrypt(bytes(msg.encode("utf8"))))
    return encrypt_text.decode('utf-8')

def decrypt_data(encrypt_msg):
    private_key = get_key('assets/rsa_private_key.pem')
    cipher = PKCS1_cipher.new(private_key)
    back_text = cipher.decrypt(base64.b64decode(encrypt_msg), 0)
    return back_text.decode('utf-8')

def test_encrypt_decrypt():
    msg = "coolpython.net"
    encrypt_text = encrypt_data(msg)
    decrypt_text = decrypt_data(encrypt_text)
    print(msg == decrypt_text)

test_encrypt_decrypt()     # True