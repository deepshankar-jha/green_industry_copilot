from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

import uuid
import json
import os


class FoundryIQManager:

    def __init__(self):

        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = os.getenv("SEARCH_INDEX_NAME")

        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.key),
        )

    def clear_user_documents(self, user_id):
        results = self.client.search(
            search_text="*", filter=f"user_id eq '{user_id}'", top=1000
        )

        docs = [{"id": doc["id"]} for doc in results]

        if docs:
            self.client.delete_documents(docs)

    def upload_graph(self, filepath: str, user_id: str):

        self.clear_user_documents(user_id)

        with open(filepath, "r", encoding="utf-8") as f:
            processes = json.load(f)

        docs = []

        for process in processes:

            text = json.dumps(process, ensure_ascii=False)

            docs.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "content": text,
                    "source": process["process_name"],
                }
            )

        result = self.client.upload_documents(documents=docs)

        for r in result:
            print(r.succeeded, r.key, r.error_message)

    def retrieve(self, query: str, user_id: str, top_k: int = 5):

        results = self.client.search(
            search_text=query, filter=f"user_id eq '{user_id}'", top=top_k
        )

        knowledge = []

        for doc in results:
            knowledge.append(doc["content"])

        return "\n\n".join(knowledge)
