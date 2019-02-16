from Crypto.Cipher import AES
from binascii import hexlify


class Crypto_Message:
    def __init__(self):
        self.key = b'Super Secret Key'

    def _encrypt(self, msg):
        cipher = AES.new(self.key, AES.MODE_CFB)
        cipher_text = cipher.iv + cipher.encrypt(msg)
        return cipher_text

    def _decrypt(self, cipher_text):
        cipher = AES.new(self.key, AES.MODE_CFB, iv=cipher_text[:16])
        message = cipher.decrypt(cipher_text[16:])
        return message
