from nacl.public import PrivateKey, Box

with open("keys/sender_private.key", "rb") as f:
    sender_private = PrivateKey(f.read())

with open("keys/recipient_private.key", "rb") as f:
    recipient_private = PrivateKey(f.read())

recipient_public = recipient_private.public_key

def encrypt_data(data, sender_private, recipient_public):
    box = Box(sender_private, recipient_public)
    return box.encrypt(data.encode())

def decrypt_data(encrypted, sender_public, recipient_private):
    box = Box(recipient_private, sender_public)
    return box.decrypt(encrypted).decode()
