import base64
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher

max_plaintext_len = 200

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

# def encrypt_data_wth_client_key(msg, key):
#     client_key = RSA.importKey(key)
#     # print(1)
#     cipher = PKCS1_cipher.new(client_key)
#     # print(2)
#     encrypt_text = base64.b64encode(cipher.encrypt(bytes(msg.encode("utf8"))))
#     # print(3)
#     return encrypt_text.decode('utf-8')

def decrypt_data_chunk(encrypt_msg):
    private_key = get_key('assets/rsa_private_key.pem')
    cipher = PKCS1_cipher.new(private_key)
    back_text = cipher.decrypt(base64.b64decode(encrypt_msg), 0)
    return back_text.decode('utf-8')

def decrypt_data_Byte(encrypt_msg):
    private_key = get_key('assets/rsa_private_key.pem')
    cipher = PKCS1_cipher.new(private_key)
    back_text = cipher.decrypt(encrypt_msg, 0)
    return back_text

# def test_encrypt_decrypt():
#     msg = "coolpython.net"
#     encrypt_text = encrypt_data(msg)
#     decrypt_text = decrypt_data_chunk(encrypt_text)
#     print(msg == decrypt_text)
    
def encrypt_data_wth_client_key(msg, key):
    chunks = [msg[i:i+max_plaintext_len] for i in range(0, len(msg), max_plaintext_len)]

    # Encrypt each chunk using PKCS1_v1_5 encryption with the generated RSA key
    ciphertexts = []
    for chunk in chunks:
        client_key = RSA.importKey(key)
        cipher = PKCS1_cipher.new(client_key)
        ciphertext = base64.b64encode(cipher.encrypt(bytes(chunk.encode("utf8"))))
        ciphertexts.append(ciphertext)

    # Concatenate the ciphertexts to form the final ciphertext
    final_ciphertext = b' '.join(ciphertexts)

    # Return the final ciphertext and the RSA public key (for decryption)
    return final_ciphertext.decode('utf-8')
# test_encrypt_decrypt()     # True

def decrypt_data(encrypt_msg):
    substrings = list(filter(lambda s: s != '', encrypt_msg.split(' ')))
    mergedtext = ''
    # print(substrings)
    for i in substrings:
        mergedtext += decrypt_data_chunk(i) #decrypt_data_Byte(base64.b64decode(i)).decode('utf-8')
    # print('done')
    return mergedtext

