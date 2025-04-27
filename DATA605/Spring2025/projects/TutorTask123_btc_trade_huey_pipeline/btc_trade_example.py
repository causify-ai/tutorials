"""
btc_trade_example.py

Simple example demonstrating how to use the Bitcoin Trade Processing API.

This script:
- Starts the Prometheus monitoring server.
- Simulates a Bitcoin trade.
- Processes the trade using the process_trade API.

References:
- Core API functions defined in btc_trade_API.py
- Documentation provided in btc_trade_API.md

Make sure Redis and Huey worker are running before executing this script.
"""

import logging
from btc_trade_API import start_monitoring, process_trade

# -----------------------------------------------------------------------------
# Setup Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Start Prometheus Monitoring
    start_monitoring(port=8000)
    _LOG.info("Monitoring server started.")

    # Simulate an example Bitcoin trade
    example_trade = {
        "price": 50423.15,
        "time": "2025-04-26T20:00:00Z"
    }
    _LOG.info("Processing trade: %s", example_trade)

    # Process the trade
    process_trade(example_trade)
    _LOG.info("Trade processing complete.")
