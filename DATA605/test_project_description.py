import logging
from unittest import mock

import pandas as pd

import helpers_root.helpers.hunit_test as hunitest
import DATA605.project_description as projdesc

_LOG = logging.getLogger(__name__)

class TestProjectDescription1(hunitest.TestCase):
    def test_read_google_sheet1(self) -> None:
        """
        Test reading a Google Sheet returns a valid DataFrame.
        """
        url = "https://docs.google.com/fake-sheet-url"
        secret_path = "/fake/path/to/secret.json"

        mock_data = pd.DataFrame({
            "Tool": ["Kafka"],
            "Difficulty": ["2"]
        })

        with mock.patch("helpers_root.helpers.hgoogle_drive_api.get_credentials") as mock_creds, \
             mock.patch("helpers_root.helpers.hgoogle_drive_api.read_google_file", return_value=mock_data):
            df = projdesc.read_google_sheet(url, secret_path)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(df.shape[0], 1)
            _LOG.debug("read_google_sheet1 → %s", df)

    def test_generate_project_description1(self) -> None:
        """
        Test project description generation using mocked OpenAI.
        """
        tech = "Kafka"
        difficulty = "2"

        mock_output = "Title: Kafka Project\nDifficulty: 2\n..."

        with mock.patch("helpers_root.helpers.hopenai.get_completion", return_value=mock_output):
            desc = projdesc.generate_project_description(tech, difficulty)
            self.assertIn("Kafka", desc)
            self.assertIn("Difficulty", desc)
            _LOG.debug("generate_project_description1 → %s", desc)

    def test_create_markdown_file1(self) -> None:
        """
        Test the markdown creation process with mocked data and completion.
        """
        df = pd.DataFrame({
            "Tool": ["Kafka"],
            "Difficulty": ["2"]
        })
        markdown_path = "/tmp/test_projects.md"
        mock_output = "Title: Kafka Project\nDifficulty: 2\n..."

        with mock.patch("helpers_root.helpers.hopenai.get_completion", return_value=mock_output), \
             mock.patch("helpers_root.helpers.hio.to_file") as mock_to_file:
            projdesc.create_markdown_file(df, markdown_path, max_projects=1, sleep_sec=0)
            mock_to_file.assert_called_once()
            written_content = mock_to_file.call_args[0][1]
            self.assertIn("Kafka", written_content)
            _LOG.debug("create_markdown_file1 content →\n%s", written_content)
