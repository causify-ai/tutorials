import unittest
from unittest.mock import patch
from DoWhy_API import fetch_and_alert

class TestBitcoinAlert(unittest.TestCase):

    @patch('DoWhy_API.send_alert')
    @patch('DoWhy_API.get_bitcoin_price')
    def test_alert_triggered_above_threshold(self, mock_get_price, mock_send_alert):
        mock_get_price.return_value = 35000  
        fetch_and_alert("dummy_url", threshold=30000, direction="above")

        mock_send_alert.assert_called_once_with("Bitcoin price is above $30000!")

    @patch('DoWhy_API.send_alert')
    @patch('DoWhy_API.get_bitcoin_price')
    def test_alert_not_triggered_below_threshold(self, mock_get_price, mock_send_alert):
        mock_get_price.return_value = 25000  
        fetch_and_alert("dummy_url", threshold=30000, direction="above")

        mock_send_alert.assert_not_called()

if __name__ == '__main__':
    unittest.main()
