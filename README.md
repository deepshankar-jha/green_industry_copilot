# 🌿 Green Industry Copilot

**AI-Powered Sustainability Intelligence for Industrial Operations**

Green Industry Copilot is an intelligent sustainability platform built for the **Microsoft Agent League Hackathon**. It transforms unstructured industrial documents into structured process knowledge, optimizes manufacturing systems for environmental performance, and enables interactive AI-driven analysis through a conversational assistant.

The platform combines:

* **Azure AI Foundry**
* **Foundry IQ**
* **Azure OpenAI Models**
* **Azure AI Search**
* **FastAPI**
* **Socket.IO**
* **Retrieval-Augmented Generation (RAG)**

to create an industrial sustainability copilot capable of helping organizations reduce emissions, improve efficiency, and promote circular economy practices.

---

# Demo Video

https://youtu.be/JeLZ5HWo-rQ

---

# Problem Statement

Industrial organizations possess valuable process information buried inside:

* PDF documents
* Word files
* Technical reports
* Operating procedures

Extracting actionable sustainability insights from these documents is difficult because:

* Process knowledge is fragmented.
* Environmental impacts are difficult to quantify.
* Waste reuse opportunities are often missed.
* Process analysis requires domain experts.
* Follow-up investigations are largely manual.

Green Industry Copilot converts these static documents into structured process graphs and redesigns them into greener and more sustainable systems.

---

# Features

## AI-Powered Process Extraction

Supported document formats:

* PDF
* DOCX
* TXT
* Markdown

The system automatically extracts:

* Inputs
* Outputs
* By-products
* Energy consumption
* Water usage
* Emissions
* Operating costs
* Process dependencies

Extraction uses Azure OpenAI structured outputs and Pydantic schemas to ensure consistency and minimize hallucinations.

---

## Sustainability Optimization

The optimization engine redesigns process chains to maximize:

* Carbon reduction
* Energy efficiency
* Water conservation
* Waste minimization
* Heat recovery
* Circular economy principles
* Renewable energy adoption
* By-product reuse
* Reduced operating costs

Graph consistency is preserved while introducing greener alternatives and recycling loops.

---

## Conversational AI Assistant

Users can ask questions about:

* Original processes
* Optimized processes
* Resource consumption
* Emissions
* Operating costs
* Sustainability improvements

Conversation history is maintained for contextual follow-up interactions.

---

# Azure AI Foundry IQ

Foundry IQ acts as the knowledge backbone of the platform.

## Semantic Process Memory

Extracted process graphs are indexed and stored as searchable knowledge.

---

## Retrieval-Augmented Generation (RAG)

Relevant process information is retrieved before generating answers.

This provides:

* Context-aware responses
* Reduced hallucinations
* Better sustainability recommendations

---

## User Isolation

Each user's knowledge is stored independently.

Search results are filtered using user identifiers to support secure multi-user operation.

---

## Dynamic Knowledge Updates

Whenever processes are optimized, the updated graphs are automatically uploaded so the assistant always reasons over the latest process configuration.

---

# Architecture

```text
Industrial Documents
          ↓
     Azure AI Models
          ↓
Structured Process Graphs
          ↓
       Foundry IQ
          ↓
 Azure AI Search Index
          ↓
Retrieval-Augmented Generation
          ↓
Azure AI Models
          ↓
Sustainability Optimization
          ↓
Interactive Green Industry Copilot
```

---

# Technology Stack

## AI Layer

* Azure AI Foundry
* Foundry IQ
* Azure OpenAI
* LangChain
* RAG
* Pydantic Structured Outputs

## Knowledge Layer

* Azure AI Search
* Semantic Retrieval
* User-specific indexing

## Backend

* FastAPI
* Python
* Socket.IO
* ASGI

## Document Processing

* PyPDF
* python-docx

## Data Modeling

* Pydantic
* JSON Process Graphs

## Frontend

* HTML
* CSS
* JavaScript

---

# Repository Structure

```text
backend/

├── main.py
├── process_extractor.py
├── process_optimizer.py
├── foundry_iq.py
├── chat_manager.py
├── socket_server.py
├── schemas.py
├── create_index.py
└── requirements.txt

frontend/

├── index.html
├── js/
├── css/

uploads/

└── <socket_id>/
      original_graph.json
      optimized_graph.json
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/green-industry-copilot.git

cd green-industry-copilot
```

---

## 2. Create a Virtual Environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```cmd
python -m venv .venv

.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file:

```env
AZURE_OPENAI_API_KEY=

AZURE_OPENAI_ENDPOINT=

AZURE_OPENAI_DEPLOYMENT=

AZURE_SEARCH_ENDPOINT=

AZURE_SEARCH_KEY=

SEARCH_INDEX_NAME=
```

---

# Create Azure AI Search Index

Run:

```bash
python create_index.py
```

This creates the Azure AI Search index used by Foundry IQ.

---

# Running the Application

Start the FastAPI server:

```bash
uvicorn main:socket_app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

---

# How It Works

## Step 1: Upload Documents

Users upload:

* PDF
* DOCX
* TXT
* Markdown

---

## Step 2: Process Extraction

Azure AI models convert documents into structured process graphs.

Information extracted includes:

* Inputs
* Outputs
* Emissions
* Water consumption
* Energy usage
* By-products
* Process dependencies

---

## Step 3: Knowledge Indexing

Graphs are uploaded into:

* Foundry IQ
* Azure AI Search

and become searchable knowledge.

---

## Step 4: Sustainability Optimization

The optimizer redesigns processes to:

* Reduce emissions
* Improve efficiency
* Promote recycling
* Recover waste heat
* Reduce costs

---

## Step 5: Conversational AI

Users can ask:

### Example Questions

```text
Which process emits the most CO2?

How much water does the plant consume?

What improvements were introduced?

Which by-products can be reused?

How much energy was saved?

Which process contributes most to operating cost?
```

---

# Real-Time Experience

Socket.IO provides:

* Upload progress notifications
* Process extraction status
* Optimization updates
* Interactive chat responses

---

# Supported File Formats

| Format   | Supported |
| -------- | --------- |
| PDF      | ✅         |
| DOCX     | ✅         |
| TXT      | ✅         |
| Markdown | ✅         |

---

# Future Improvements

* Redis-backed session storage
* Persistent chat memory
* Graph visualization with Cytoscape
* Multi-document ingestion
* Multi-agent orchestration
* Carbon footprint analytics
* Life Cycle Assessment (LCA)
* Digital twin integration

---

# Impact

Green Industry Copilot transforms static industrial documents into an intelligent sustainability knowledge system.

By combining **Azure AI Foundry IQ**, **Azure OpenAI models**, and **Azure AI Search**, the platform enables manufacturers to:

* Discover efficiency opportunities.
* Reduce emissions.
* Improve resource utilization.
* Promote circular economy practices.
* Interact with processes using conversational AI.

bringing industrial sustainability intelligence into a practical, scalable, and user-friendly form.

---

## Built for

### Microsoft Agent League Hackathon

Using:

* Azure AI Foundry
* Foundry IQ
* Azure OpenAI
* Azure AI Search
* FastAPI
* Socket.IO

🌿 *AI for a greener industrial future.*

