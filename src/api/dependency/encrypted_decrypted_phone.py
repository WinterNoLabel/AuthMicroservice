from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from core.settings import settings

key = base64.b64decode(settings.fernet_settings.fernet_key)
IV = base64.b64decode(settings.fernet_settings.fernet_IV)


async def encrypt(data: str) -> str:
    cipher = AES.new(key, AES.MODE_CBC, IV)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted).decode('utf-8')


async def decrypt(data: str) -> str:
    encrypted_data = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_CBC, IV)
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted.decode('utf-8')
