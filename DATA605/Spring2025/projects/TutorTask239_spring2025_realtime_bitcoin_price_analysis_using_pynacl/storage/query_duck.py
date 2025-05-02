from crypto.encrypt import decrypt_data, sender_private, recipient_public

def query_last_n_prices(n=60):
    rows = conn.execute(f"""
        SELECT timestamp, encrypted_price FROM btc_price
        ORDER BY timestamp DESC
        LIMIT {n}
    """).fetchall()
    
    decrypted = []
    for ts, enc in reversed(rows):
        try:
            value = float(decrypt_data(enc, sender_private.public_key, recipient_private))
            decrypted.append((ts, value))
        except Exception as e:
            print(f"Decryption error: {e}")
    return decrypted