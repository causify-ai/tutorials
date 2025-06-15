# SecureBitcoin_utils.py

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
import hashlib
import json
import requests
from datetime import datetime

# Constants
SALT = b"some_salt_for_key_derivation"
ITERATIONS = 100_000
BLOCK_SIZE = AES.block_size

# Derive AES key from password
def derive_key(password: str) -> bytes:
    return PBKDF2(password, SALT, dkLen=32, count=ITERATIONS)

# Padding for AES
def pad(data: bytes) -> bytes:
    padding_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([padding_len]) * padding_len

def unpad(data: bytes) -> bytes:
    return data[:-data[-1]]

# Encrypt using AES CBC
def encrypt_data(data: dict, key: bytes) -> str:
    raw = pad(json.dumps(data).encode('utf-8'))
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(raw)
    return base64.b64encode(iv + encrypted).decode('utf-8')

# Decrypt AES CBC
def decrypt_data(enc_data: str, key: bytes) -> dict:
    enc = base64.b64decode(enc_data)
    iv, ciphertext = enc[:BLOCK_SIZE], enc[BLOCK_SIZE:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw = unpad(cipher.decrypt(ciphertext))
    return json.loads(raw)

# Hashing
def hash_data(data: dict) -> str:
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

# Fetch Bitcoin price
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        price = response.json()['bitcoin']['usd']
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "price_usd": price
        }
    else:
        raise Exception("Failed to fetch data from CoinGecko")


from datetime import datetime, timezone
import requests

def fetch_hourly_data(days=15):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": str(days)
    }

    response = requests.get(url, params=params)
    
    try:
        response.raise_for_status()
        json_data = response.json()

        if "prices" not in json_data:
            raise ValueError("Missing 'prices' in response")

        raw = json_data["prices"]
        hourly_data = [{
            "timestamp": datetime.fromtimestamp(t / 1000, tz=timezone.utc).isoformat(),
            "price_usd": price
        } for t, price in raw]

        return hourly_data

    except Exception as e:
        print("Error fetching data:", e)
        print("Response:", response.text)
        return []

