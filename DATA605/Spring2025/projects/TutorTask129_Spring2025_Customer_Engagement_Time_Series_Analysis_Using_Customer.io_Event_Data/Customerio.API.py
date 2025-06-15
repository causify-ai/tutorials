"""
Customerio.API.py

This script demonstrates how to simulate users and events using the Customer.io API.
It uploads the data to the platform and prepares it for downstream time series analysis.

References:
- Customer.io API Docs: https://customer.io/docs/api/
- Faker Library: https://faker.readthedocs.io
- Style Guide: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md

Documentation:
- See `Customerio.API.md` for a complete tutorial on API setup and usage.
"""

from Customerio_utils import generate_users, simulate_events

if __name__ == "__main__":
    # Step 1: Create and upload simulated users
    user_ids = generate_users(num_users=1000)

    # Step 2: Simulate events and send them to Customer.io
    simulate_events(user_ids)

    print(" Customer.io API simulation completed.")