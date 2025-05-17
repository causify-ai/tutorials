# Secure Bitcoin Price Ingestion API Documentation

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Core Components](#core-components)
  * [Key Derivation](#key-derivation)
  * [Encryption and Decryption](#encryption-and-decryption)
  * [Data Fetching](#data-fetching)
  * [Data Storage](#data-storage)
- [API Reference](#api-reference)
  * [Key Management](#key-management)
  * [Data Operations](#data-operations)
  * [Bitcoin Price Fetching](#bitcoin-price-fetching)
- [Usage Examples](#usage-examples)
- [Security Considerations](#security-considerations)

## Overview

The Secure Bitcoin Price Ingestion API provides a secure way to fetch, encrypt, and store Bitcoin price data. It uses AES encryption in CBC mode for data security and implements PBKDF2 for key derivation. The system is designed to protect sensitive price data while maintaining accessibility for authorized users.

## Installation

```bash
pip install pycryptodome requests matplotlib pandas
```

## Core Components

### Key Derivation

The API uses PBKDF2 (Password-Based Key Derivation Function 2) for secure key generation:

```python
from Crypto.Protocol.KDF import PBKDF2

# Constants
SALT = b"some_salt_for_key_derivation"
ITERATIONS = 100_000

# Generate key from password
key = derive_key("your_password")
```

### Encryption and Decryption

Data encryption is performed using AES-CBC with secure padding:

```python
# Encrypt data
encrypted_data = encrypt_data({"price": 50000}, key)

# Decrypt data
decrypted_data = decrypt_data(encrypted_data, key)
```

### Data Fetching

Bitcoin price data is fetched from the CoinGecko API:

```python
# Fetch current price
price_data = fetch_bitcoin_price()

# Fetch historical data
historical_data = fetch_hourly_data(days=15)
```

### Data Storage

Data is stored in encrypted format with timestamps and signatures:

```python
{
    "ts": "2025-04-23T04:00:20.431373",
    "enc": "<encrypted_data>",
    "sig": "<signature>"
}
```

## API Reference

### Key Management

#### `derive_key(password: str) -> bytes`
- Generates a 32-byte key from a password using PBKDF2
- Parameters:
  * `password`: User password for key derivation
- Returns: 32-byte encryption key

### Data Operations

#### `encrypt_data(data: dict, key: bytes) -> str`
- Encrypts data using AES-CBC
- Parameters:
  * `data`: Dictionary containing data to encrypt
  * `key`: Encryption key from derive_key()
- Returns: Base64 encoded encrypted data

#### `decrypt_data(enc_data: str, key: bytes) -> dict`
- Decrypts AES-CBC encrypted data
- Parameters:
  * `enc_data`: Encrypted data string
  * `key`: Decryption key
- Returns: Decrypted data dictionary

#### `hash_data(data: dict) -> str`
- Creates SHA-256 hash of data
- Parameters:
  * `data`: Dictionary to hash
- Returns: Hexadecimal hash string

### Bitcoin Price Fetching

#### `fetch_bitcoin_price() -> dict`
- Fetches current Bitcoin price from CoinGecko
- Returns: Dictionary with timestamp and price
  ```python
  {
      "timestamp": "2025-05-16T16:28:05.882654",
      "price_usd": 104176
  }
  ```

#### `fetch_hourly_data(days: int = 15) -> list`
- Fetches historical hourly price data
- Parameters:
  * `days`: Number of days of historical data (default: 15)
- Returns: List of hourly price entries

## Usage Examples

Basic usage example:

```python
from SecureBitcoin_utils import *

# Initialize encryption key
password = "your_secure_password"
key = derive_key(password)

# Fetch and encrypt price data
price_data = fetch_bitcoin_price()
encrypted_data = encrypt_data(price_data, key)

# Decrypt data
decrypted_data = decrypt_data(encrypted_data, key)
```

## Security Considerations

1. Password Security
   - Use strong passwords
   - Never store passwords in plaintext
   - Change passwords periodically

2. Key Management
   - Protect encryption keys
   - Use secure key storage methods
   - Implement key rotation policies

3. Data Protection
   - All price data is encrypted at rest
   - Signatures prevent tampering
   - Secure communication channels required