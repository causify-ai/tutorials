import pandas as pd
from unittest import mock
import tutorial_class_project_instructions.generate_class_project_description as projdesc
import helpers.hunit_test as hunitest
import pytest

class TestProjectDescriptionWithCache(hunitest.TestCase):

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Can initialize dummy cache or files here
        yield
        # Avoid triggering _GLOBAL_CAPSYS in tearDown

    def test_read_google_sheet(self) -> None:
        if True:
            #Set to True for testing purposes
            url = "https://docs.google.com/fake-sheet-url"
        secret_path = "/fake/path/to/secret.json"
        mock_data = pd.DataFrame({"Tool": ["Kafka"], "Difficulty": ["2"]})

        with mock.patch("helpers_root.helpers.hgoogle_drive_api.get_credentials"), \
             mock.patch("helpers_root.helpers.hgoogle_drive_api.read_google_file", return_value=mock_data):
            df = projdesc._read_google_sheet(url, secret_path)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(df.shape[0], 1)

    def test_generate_class_project_description(self) -> None:
        tech = "Kafka"
        difficulty = "2"
        mock_output = "Title: Kafka Project\nDifficulty: 2\n..."

        with mock.patch("helpers_root.helpers.hopenai.get_completion", return_value=mock_output):
            desc = projdesc._generate_project_description(tech, difficulty)
            self.assertIn("Kafka", desc)
            self.assertIn("Difficulty", desc)

    def test_create_markdown_file(self) -> None:
        df = pd.DataFrame({"Tool": ["Kafka"], "Difficulty": ["2"]})
        markdown_path = "/tmp/test_projects.md"
        mock_output = "Title: Kafka Project\nDifficulty: 2\n..."

        with mock.patch("helpers_root.helpers.hopenai.get_completion", return_value=mock_output), \
             mock.patch("helpers_root.helpers.hio.to_file") as mock_to_file:
            projdesc.create_markdown_file(df, markdown_path, max_projects=1, sleep_sec=0)
            mock_to_file.assert_called_once()
            written_content = mock_to_file.call_args[0][1]
            self.assertIn("Kafka", written_content)
