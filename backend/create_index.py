"""
create_index.py

Creates or updates an Azure AI Search index used by the application.

This module:

1. Loads Azure Search configuration from environment variables.
2. Creates an authenticated SearchIndexClient.
3. Defines the schema for storing indexed documents.
4. Creates the index if it does not exist, or updates it if it already exists.

Required environment variables:
    AZURE_SEARCH_ENDPOINT : Azure AI Search service endpoint.
    AZURE_SEARCH_KEY      : Admin API key for the search service.
    SEARCH_INDEX_NAME     : Name of the index to create or update.
"""

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

# ---------------------------------------------------------------------------
# Load configuration from the .env file into environment variables.
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Read Azure AI Search settings from environment variables.
# ---------------------------------------------------------------------------
endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("SEARCH_INDEX_NAME")

# ---------------------------------------------------------------------------
# Create a client used to manage Azure AI Search indexes.
#
# The SearchIndexClient provides operations for creating, updating,
# retrieving, and deleting search indexes.
# ---------------------------------------------------------------------------
client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# ---------------------------------------------------------------------------
# Define the schema of the search index.
#
# Fields:
#     id:
#         Unique identifier for each indexed document.
#
#     user_id:
#         Identifier of the user associated with the document.
#         Filterable to enable user-specific queries.
#
#     content:
#         Main searchable text content.
#
#     source:
#         Metadata indicating the origin of the document.
#         Filterable for source-based searches.
# ---------------------------------------------------------------------------
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="user_id", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
]

# ---------------------------------------------------------------------------
# Create the SearchIndex object using the configured schema.
# ---------------------------------------------------------------------------
index = SearchIndex(name=index_name, fields=fields)

# ---------------------------------------------------------------------------
# Create the index if it does not exist, or update it if it already exists.
# ---------------------------------------------------------------------------
client.create_or_update_index(index)

# ---------------------------------------------------------------------------
# Display a confirmation message after successful completion.
# ---------------------------------------------------------------------------
print("Index created")
