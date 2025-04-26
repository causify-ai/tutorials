from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/bitcoin-price")
async def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
