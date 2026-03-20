# Place your PDF documents here

This directory stores company documents for RAG (Retrieval-Augmented Generation).

## Supported File Types
- `.pdf` - PDF files
- `.txt` - Text files

## Usage

1. Copy your company PDFs/documents here
2. Run: `python -m app.ai.rag.management index ./`
3. Documents will be indexed and searchable

## Example Structure

```
documents/
  ├── handbook.pdf          # Employee handbook
  ├── policies.pdf          # Company policies
  ├── procedures.txt        # Operational procedures
  └── benefits.pdf          # Benefits information
```

## Indexing

After adding documents, index them:

```bash
cd agent-service
python -m app.ai.rag.management index ./data/documents/
```

See `RAG_QUICKSTART.md` for more details.
