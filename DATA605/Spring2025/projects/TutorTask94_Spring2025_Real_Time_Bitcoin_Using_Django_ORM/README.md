
📘 Description
Django ORM (Object-Relational Mapping) is a powerful component of the Django web framework that allows developers to work with relational databases using Python objects instead of raw SQL. It simplifies common database operations like querying, updating, and filtering records by mapping database tables to Python classes.

In this API module, we encapsulate logic for fetching real-time Bitcoin prices and interacting with the database using Django ORM. We use helper functions to abstract away implementation details, enabling concise, readable, and reusable code.

📚 Describe Technology
Django ORM Capabilities:

Provides a high-level abstraction for SQL operations.

Maps database tables to Python classes via models.Model.

Offers database-agnostic support for SQLite, PostgreSQL, MySQL, etc.

Enables powerful data querying using a Pythonic, chainable syntax.

Supports model-level methods for business logic.

Enables easy schema migration with Django's built-in migration system.

API Layer (BTC_API_utils.py) Design:

fetch_bitcoin_price(): Hits the CoinGecko API and extracts the latest Bitcoin price in USD.

save_price(price): Persists a single price point into the BitcoinPrice model using ORM.

plot_price_trend(): Loads recent price records using ORM and visualizes the trend using matplotlib.

These functions separate the raw business logic from Jupyter notebooks and make the API reusable across views, commands, and scripts.

📄 BTC.example.md
🛠️ Describe the Project
Objective:
Demonstrate a complete real-world use case of Django ORM by building a simple web application that:

Fetches real-time Bitcoin prices from a public API

Saves them in a local database (SQLite)

Performs statistical and time series analysis

Visualizes the data on a web dashboard

📥 Data Ingestion
The app uses the CoinGecko API to fetch live Bitcoin prices in USD. The fetch_bitcoin_price() function wraps this logic, and the result is stored using Django’s ORM:

python
Copy
Edit
BitcoinPrice.objects.create(price_usd=price)
📊 Data Processing
We extended the Django model to include key business logic:

average_price(): Calculates mean price of all entries

price_volatility(): Measures standard deviation of price values

latest_prices(n): Retrieves the latest N entries in time order

These allow us to keep statistical logic encapsulated within the model, promoting maintainable code.

📈 Time Series Analysis
Using matplotlib, we plot the last 50 price points. The plotting function reads data directly using Django ORM and outputs a time series chart, which is saved and embedded into the dashboard.

🌐 Deployment: Web Visualization
We built a simple Django view and HTML template to serve as a dashboard. The user can view:

Latest Bitcoin price

Average price over time

Price volatility

A live trend chart

The view uses all the helper logic and makes it available through a clean, readable UI.

