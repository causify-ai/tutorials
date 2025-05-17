from nacl.public import PrivateKey

sender_private = PrivateKey.generate()
recipient_private = PrivateKey.generate()

with open("keys/sender_private.key", "wb") as f:
    f.write(bytes(sender_private))

with open("keys/recipient_private.key", "wb") as f:
    f.write(bytes(recipient_private))