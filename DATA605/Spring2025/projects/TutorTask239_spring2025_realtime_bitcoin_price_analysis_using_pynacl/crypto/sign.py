from nacl.signing import SigningKey

sign_key = SigningKey.generate()
verify_key = sign_key.verify_key

def sign_data(data):
    return sign_key.sign(data.encode())

def verify_data(signed):
    return verify_key.verify(signed).decode()
