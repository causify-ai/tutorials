import unittest
import os
import docker_sdk_utils as utils
import pandas as pd

class TestDockerSDKUtils(unittest.TestCase):
    def test_list_docker_images(self):
        images = utils.list_docker_images()
        self.assertIsInstance(images, list)

    def test_list_docker_containers(self):
        containers = utils.list_docker_containers()
        self.assertIsInstance(containers, list)

    def test_pull_docker_image(self):
        result = utils.pull_docker_image('hello-world')
        self.assertIsNotNone(result)

    def test_time_series_analysis(self):
        fetcher = utils.CryptoDataFetcher('http://localhost:8086', 'token', 'org', 'bucket')
        df = pd.DataFrame({'time': pd.date_range('2023-01-01', periods=10, freq='T'), 'value': range(10)})
        result = fetcher.time_series_analysis(df, order=(1,1,1), window=3)
        self.assertIn('moving_avg', result.columns)
        self.assertIn('arima_forecast', result.columns)

if __name__ == "__main__":
    unittest.main()
