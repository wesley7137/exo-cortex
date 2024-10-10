# security/encryption.py
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/encryption.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class EncryptionManager:
    def __init__(self, key=None):
        self.key = key or self.generate_key()
        self.aesgcm = AESGCM(self.key)

    def generate_key(self):
        key = AESGCM.generate_key(bit_length=256)
        logger.info("Encryption key generated.")
        return key

    def encrypt(self, data, nonce=None):
        try:
            nonce = nonce or os.urandom(12)
            encrypted = self.aesgcm.encrypt(nonce, data.encode(), None)
            logger.debug("Data encrypted.")
            return nonce, encrypted
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise

    def decrypt(self, nonce, encrypted_data):
        try:
            decrypted = self.aesgcm.decrypt(nonce, encrypted_data, None)
            logger.debug("Data decrypted.")
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
