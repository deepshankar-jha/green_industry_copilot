from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchableField,
    SimpleField,
    SearchFieldDataType,
)
import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("SEARCH_INDEX_NAME")

client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="user_id", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
]

index = SearchIndex(name=index_name, fields=fields)

client.create_or_update_index(index)

print("Index created")
