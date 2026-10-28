# Textbook Q&A

Ask questions about your PDF textbooks and get answers with citations (textbook + page).

## How it works

1. Extracts text from PDFs in `Textbooks/`
2. Splits it into chunks (1,000 chars, 200 overlap) and embeds them locally with `all-MiniLM-L6-v2`
3. Stores embeddings in Chroma (`vector_db_minilm/`)
4. Retrieves the top 5 chunks for a question and passes them to Gemini to write the answer

## Setup

```bash
pip install -r requirements.txt
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey) and add it to `.env`:

```
GEMINI_KEY=your_api_key
```

Put PDFs in `Textbooks/`, then index them (type `quit` when the prompt appears):

```bash
python main.py
```

Run the app:

```bash
streamlit run app.py
```

To re-index after changing PDFs, delete `vector_db_minilm/` and run `python main.py` again.

## Limitations

- Local prototype: PDFs only, one folder, no auth or per-user permissions
- Doesn't detect changed PDFs automatically
- Answers can be wrong or miss relevant passages, so check the cited page
- Chapter labels are guessed from page text and may show "Unknown Chapter"
- Don't commit `.env`
