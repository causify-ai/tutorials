import os
from pathlib import Path
from dify_client import DifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DifyChatbot:
    def __init__(self):
        self.client = DifyClient(
            api_key=os.getenv("DIFY_API_KEY"),
            base_url=os.getenv("DIFY_BASE_URL", "http://localhost:5001")
        )
        self.dataset_id = os.getenv("DATASET_ID")
    
    def create_dataset(self, name: str) -> str:
        """
        Create a new knowledge base dataset.
        
        :param name: name of the dataset
        :return: dataset ID
        """
        response = self.client.datasets.create(name=name, type="knowledge")
        self.dataset_id = response.id
        return self.dataset_id

    def upload_document(self, file_path: Path):
        """
        Upload a document to the knowledge base.
        
        :param file_path: path to the document to upload
        :return: upload status
        """
        if not self.dataset_id:
            raise ValueError("Dataset ID not configured")
            
        return self.client.documents.create(
            dataset_id=self.dataset_id,
            file=open(file_path, "rb"),
            file_type="knowledge",
            process_rule={"mode": "automatic"}
        )

    def query(self, question: str) -> str:
        """
        Query the knowledge base.

        :param question: the question to ask
        :return: formatted response with sources
        """
        response = self.client.chat_messages.create(
            inputs={},
            query=question,
            response_mode="blocking",
            user="api_user",
            dataset_ids=[self.dataset_id]
        )
        return self._format_response(response)

    def _format_response(self, response: Any) -> str:
        """
        Format response with sources.

        :param response: the response object from the Dify API
        :return: formatted string with answer and sources
        """
        answer = response.answer
        sources = response.metadata.documents
        
        formatted = f"{answer}\n\nSources:\n"
        for idx, doc in enumerate(sources, 1):
            formatted += f"[{idx}] {doc.document_name} (pg {doc.page_number})\n"
        return formatted

# Usage example
if __name__ == "__main__":
    # Initialize chatbot.
    bot = DifyChatbot()
    # Create dataset.
    # dataset_id = bot.create_dataset("Production Documentation")
    # print(f"Created dataset: {dataset_id}")
    # Upload documents
    doc_path = Path("/helpers_root/docs/coding/all.code_design.how_to_guide.md")
    upload_result = bot.upload_document(doc_path)
    print(f"Upload status: {upload_result.status}")
    # Query the chatbot.
    response = bot.query("How do I reset a user password?")
    print(response)