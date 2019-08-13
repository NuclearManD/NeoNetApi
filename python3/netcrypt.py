import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
    
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
backend = default_backend()

def encrypt1(plaintext, password):
    password=password.zfill(32)
    if type(plaintext)==str:
        plaintext=plaintext.encode()
    plaintext = (str(len(plaintext))+' ').encode()+plaintext
    plaintext = plaintext.zfill(len(plaintext)-(len(plaintext)%32)+32)
    if type(password)==str:
        password=password.encode()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(password), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ct = encryptor.update(plaintext)
    ct +=encryptor.finalize()
    return iv+ct
def decrypt1(cyphertext, password):
    password=password.zfill(32)
    if type(password)==str:
        password=password.encode()
    iv=cyphertext[:16]
    ct=cyphertext[16:]
    cipher = Cipher(algorithms.AES(password), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    text=decryptor.update(ct) + decryptor.finalize()
    return text[-int(text[:text.index(b' ')].decode()):]
def sha512(data):
    if type(data)==str:
        data=data.encode()
    digest = hashes.Hash(hashes.SHA512(), backend=default_backend())
    digest.update(data)
    return digest.finalize()
def hexsha512(data):
    data=sha512(data)
    out=""
    for i in data:
        out+=hex(i)[2:].zfill(2)
    return out
def strhash(data):
    data=sha512(data)
    out=""
    ls=0
    cnt=0
    for i in data:
        num = i&0x3F
        ls = (ls<<2) | (i>>6)
        cnt+=1

        if num<10:
            out+=chr(num+48)
        elif num<36:
            out+=chr(num+65-10)
        elif num<62:
            out+=chr(num+97-36)
        elif num==62:
            out+=' '
        else:
            out+='_'
        if cnt==3:
            num=ls
            if num<10:
                out+=chr(num+48)
            elif num<36:
                out+=chr(num+65-10)
            elif num<62:
                out+=chr(num+97-36)
            elif num==62:
                out+=' '
            else:
                out+='_'
            ls=0
            cnt=0
    return out
def shortstrhash(data, minlen = 12, maxlen=32):
    data=strhash(data)
    length = ord(data[0])%(maxlen-minlen) + minlen
    return data[-length:]
