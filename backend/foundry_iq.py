"""
Foundry IQ manager module.

This module provides a wrapper around Azure AI Search operations used to
store, retrieve, and manage process graph data for individual users.
It supports:
- Uploading process graph data from JSON files.
- Removing previously indexed documents for a user.
- Retrieving relevant knowledge snippets using Azure Search.
"""

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

import uuid
import json
import os


class FoundryIQManager:
    """
    Manage user-specific knowledge stored in Azure AI Search.

    The manager encapsulates document indexing, cleanup, and retrieval
    operations so that process graphs can be maintained independently
    for each user.
    """

    def __init__(self):
        """
        Initialize the Azure Search client.

        Environment variables:
            AZURE_SEARCH_ENDPOINT: Azure Search endpoint URL.
            AZURE_SEARCH_KEY: API key used for authentication.
            SEARCH_INDEX_NAME: Name of the search index.
        """
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = os.getenv("SEARCH_INDEX_NAME")

        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.key),
        )

    def clear_user_documents(self, user_id):
        """
        Remove all indexed documents associated with a specific user.

        Args:
            user_id: Unique identifier of the user whose documents
                should be deleted.
        """
        results = self.client.search(
            search_text="*", filter=f"user_id eq '{user_id}'", top=1000
        )

        docs = [{"id": doc["id"]} for doc in results]

        if docs:
            self.client.delete_documents(docs)

    def upload_graph(self, filepath: str, user_id: str, graph_type: str):
        """
        Upload process graph data into Azure Search.

        Existing documents belonging to the user are removed before the
        new graph is indexed.

        Args:
            filepath: Path to a JSON file containing process definitions.
            user_id: Unique identifier of the target user.
        """

        # Load process definitions from disk.
        with open(filepath, "r", encoding="utf-8") as f:
            processes = json.load(f)

        docs = []

        # Convert each process entry into an indexable document.
        for process in processes:
            text = json.dumps(process, ensure_ascii=False)

            docs.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "graph_type": graph_type,
                    "content": text,
                    "source": process["process_name"],
                }
            )
        # Upload all generated documents.
        result = self.client.upload_documents(documents=docs)

        # Display upload status for each document.
        for r in result:
            print(r.succeeded, r.key, r.error_message)

    def retrieve(self, query: str, user_id: str, top_k: int = 5):
        """
        Retrieve the most relevant documents for a query.

        Args:
            query: Search text used for semantic retrieval.
            user_id: Identifier used to restrict results to a user.
            top_k: Maximum number of documents to return.

        Returns:
            A string containing concatenated document contents separated
            by blank lines.
        """
        results = self.client.search(
            search_text=query, filter=f"user_id eq '{user_id}'", top=top_k
        )

        knowledge = []

        for doc in results:
            knowledge.append(doc["content"])

        return "\n\n".join(knowledge)

    def retrieve_graph(self, user_id: str, graph_type: str):
        results = self.client.search(
            search_text="*",
            filter=(f"user_id eq '{user_id}' " f"and graph_type eq '{graph_type}'"),
            top=1000,
        )

        knowledge = []

        for doc in results:
            knowledge.append(doc["content"])

        return "\n\n".join(knowledge)
