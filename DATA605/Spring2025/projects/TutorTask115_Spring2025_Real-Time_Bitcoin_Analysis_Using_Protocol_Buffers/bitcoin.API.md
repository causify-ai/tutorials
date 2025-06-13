
# 📘 bitcoin.API.md

This markdown explains the logic and reasoning behind the API demonstration in `bitcoin.API.ipynb`.

---

## Objective

Demonstrate how to:
- Connect to a real-time cryptocurrency API (CoinGecko)
- Fetch Bitcoin market data
- Convert the raw JSON response into a structured Python dictionary
- Serialize the data into binary format using Protocol Buffers (`bitcoin_full.proto`)
- Save the serialized data to disk and deserialize it back for use

---

## API Description

We use the CoinGecko `/coins/markets` endpoint with `vs_currency=usd` and `ids=bitcoin` to fetch real-time Bitcoin data. The response includes current price, volume, market cap, supply, all-time high/low, and other fields.

---

## Protobuf Schema

The data is serialized using `bitcoin_full.proto`, which defines the schema `BitcoinFullData`. Each field from the API response is mapped to a corresponding field in the schema.

---

## Serialization Logic

We:
- Instantiate a `BitcoinFullData` object
- Use `.SerializeToString()` to convert it to binary
- Save it to a `.pb` file with a 4-byte prefix indicating the message length

---

## Deserialization Logic

To verify, we:
- Open the `.pb` file
- Read the first 4 bytes to get message size
- Read and parse the next `size` bytes using `ParseFromString`

This provides a compact and efficient way to store structured API data for downstream processing.
