# BitcoinNewsQA.API.md

## Native API: CryptoPanic

The native API used in this project is [CryptoPanic](https://cryptopanic.com/developers/api/), which provides real-time news headlines and posts related to cryptocurrency.

### Base URL: https://cryptopanic.com/api/v1/posts/


### Required Parameters:
- `auth_token`: Your API key (we used: `f2b5f828c73705d7c2f8a681e5dbc53a3357af38`)
- `currencies`: e.g., `BTC` or `ETH`
- `filter`: e.g., `news`, `sentiment`

### Sample Query:
```python
GET /api/v1/posts/?auth_token=YOUR_TOKEN&currencies=BTC&filter=news


