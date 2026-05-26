# Fact-Check Agent

Fact-Check Agent is a simple web application built to help users review factual claims from PDF documents.

The app reads uploaded PDF files, identifies lines containing numbers, statistics, dates, or factual information, and checks related information using live web search results.

It can be useful for reviewing reports, articles, market research PDFs, or documents containing outdated or misleading statistics.

---

## Features

- Upload PDF documents
- Extract factual statements automatically
- Detect claims containing numbers and statistics
- Search live web results for reference
- Display matching source links
- Simple and clean interface
- Cloud deployed using Streamlit

---

## How It Works

1. Upload a PDF file
2. The application extracts text from the document
3. Claims containing numbers or factual data are detected
4. Web search is performed using Serper API
5. Matching sources are displayed for review

---

## Tech Stack

Frontend:
- Streamlit

Backend:
- Python

Libraries:
- pdfplumber
- requests
- python-dotenv

API:
- Serper Search API

Deployment:
- Streamlit Cloud

Version Control:
- GitHub

---

## Running the Project Locally

Install dependencies:

```bash
pip install -r requirements.txt
