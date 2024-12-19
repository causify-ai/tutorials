import logging 
from types import SimpleNamespace

import unittest.mock as umock
import datetime
import openai 
import helpers.hunit_test as hunitest
import helpers.hopenai as hopenai
import helpers.hdbg as hdbg

_LOG = logging.getLogger(__name__)

class Test_response_to_txt(hunitest.TestCase):
    def test_chat_completion(self) -> None:
        """
        Test that response_to_txt correctly handles ChatCompletion response.
        """
        # Create a mock response with the expected structure.
        mock_response = umock.MagicMock(
            spec=openai.types.chat.chat_completion.ChatCompletion
        )
        # Set the mock response choices.
        mock_response.choices = [
            umock.MagicMock(message=umock.MagicMock(content="test message"))
        ]
        # Assert the response content is correctly extracted.
        self.assertEqual(hopenai.response_to_txt(mock_response), "test message")

    def test_invalid_type(self) -> None:
        """
        Test handling of invalid response type.
        """
        with self.assertRaises(ValueError):
            hopenai.response_to_txt(123)

class Test_get_edgar_example(hunitest.TestCase):
    @umock.patch("requests.get")
    def test_successful_download(self, mock_get) -> None:
        """
        Test successful download of a file from the given URL.
        """
        mock_response = umock.MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"PDF content"
        mock_get.return_value = mock_response

        with umock.patch("builtins.open", umock.mock_open()) as mock_file:
            hopenai.get_edgar_example()
            mock_file.assert_called_with("document.pdf", "wb")

class Test_extract(hunitest.TestCase):
    def test_extract_keys(self) -> None:
        """
        Test that specific keys are correctly extracted from an object with attributes.
        """
        # Create an object with attributes.
        obj = SimpleNamespace(a=1, b=2)
        # Define the keys to extract.
        keys = ["a"]
        # Validate that the extracted keys match the expected output.
        self.assertEqual(hopenai._extract(obj, keys), {"a": 1})



class Test_get_completion(hunitest.TestCase):
    @umock.patch("helpers.hopenai.OpenAI")
    def test_basic_completion(self, mock_openai) -> None:
        """
        Test that get_completion interacts with the OpenAI client correctly.
        """
        # Mock the OpenAI client.
        mock_client = umock.MagicMock()
        mock_openai.return_value = mock_client
        # Define the mock return value for the chat completion method.
        mock_client.chat.completions.create.return_value = umock.MagicMock(
            choices=[umock.MagicMock(message=umock.MagicMock(content="response"))]
        )
        # Call the function to get the completion.
        result = hopenai.get_completion(user="test query")
        # Assert that the result matches the expected response.
        self.assertEqual(result, "response")


class Test_delete_all_files(hunitest.TestCase):
    @umock.patch("helpers.hopenai.OpenAI")
    def test_delete_all_files(self, mock_openai) -> None:
        """
        Test that delete_all_files removes all files via the OpenAI client.
        """
        # Mock the OpenAI client.
        mock_client = umock.MagicMock()
        mock_openai.return_value = mock_client
        # Mock the file list returned by the client.
        mock_client.files.list.return_value = [umock.MagicMock(id="file_id")]
        # Trigger the deletion of all files.
        hopenai.delete_all_files(ask_for_confirmation=False)
        # Verify that the delete method was called with the correct file ID.
        mock_client.files.delete.assert_called_with("file_id")
class Test_get_coding_style_assistant(hunitest.TestCase):
    @umock.patch("helpers.hopenai.OpenAI")
    def test_get_coding_style_assistant(self, mock_openai) -> None:
        """
        Test creating a coding style assistant.
        """
        mock_client = umock.MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.assistants.create.return_value = umock.MagicMock(id="assistant_id")

        with umock.patch("builtins.open", umock.mock_open(read_data="dummy content")):
            assistant = hopenai.get_coding_style_assistant(
                "Coding Assistant", "Instructions", "vector_store", ["dummy_path"]
            )
        self.assertIsNotNone(assistant)

class Test_get_query_assistant(hunitest.TestCase):
    @umock.patch("helpers.hopenai.OpenAI")
    def test_get_query_assistant(self, mock_openai) -> None:
        """
        Test querying an assistant.
        """
        mock_client = umock.MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.threads.create.return_value = umock.MagicMock(id="thread_id")
        mock_client.beta.threads.runs.create_and_poll.return_value = umock.MagicMock(id="run_id")

        messages = hopenai.get_query_assistant(umock.MagicMock(), "What is AI?")
        self.assertIsNotNone(messages)


class Test_assistant_to_info(hunitest.TestCase):
    def test_assistant_metadata(self) -> None:
        """
        Test that assistant_to_info extracts metadata from an Assistant object.
        """
        # Create a mock Assistant object with attributes.
        assistant = SimpleNamespace(
            name="Assistant Name",
            created_at=1234567890,
            id="id",
            instructions="instructions",
            model="gpt-4",
        )
        # Define the expected metadata dictionary.
        expected = {
            "name": "Assistant Name",
            "created_at": datetime.datetime.fromtimestamp(1234567890),
            "id": "id",
            "instructions": "instructions",
            "model": "gpt-4",
        }
        # Assert that the extracted metadata matches the expected output.
        self.assertEqual(hopenai.assistant_to_info(assistant), expected)


class Test_assistants_to_str(hunitest.TestCase):
    def test_assistants_list(self) -> None:
        """
        Test that assistants_to_str generates a descriptive string for assistants.
        """
        # Create a mock Assistant object.
        assistant = SimpleNamespace(name="Assistant Name")
        # Generate a descriptive string for the list of assistants.
        result = hopenai.assistants_to_str([assistant])
        # Verify that the descriptive string contains the expected information.
        self.assertIn("Found 1 assistants", result)


class Test_delete_all_assistants(hunitest.TestCase):
    @umock.patch("helpers.hopenai.OpenAI")
    def test_delete_all_assistants(self, mock_openai) -> None:
        """
        Test that delete_all_assistants removes all assistants via the OpenAI client.
        """
        # Mock the OpenAI client.
        mock_client = umock.MagicMock()
        mock_openai.return_value = mock_client
        # Mock the list of assistants returned by the client.
        mock_client.beta.assistants.list.return_value = umock.MagicMock(
            data=[SimpleNamespace(id="assistant_id")]
        )
        # Trigger the deletion of all assistants.
        hopenai.delete_all_assistants(ask_for_confirmation=False)
        # Verify that the delete method was called with the correct assistant ID.
        mock_client.beta.assistants.delete.assert_called_with("assistant_id")
































