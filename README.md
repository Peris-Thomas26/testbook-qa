# Textbook Q&A

Ask questions about PDFs in `Textbooks/` and receive answers from Gemini with
textbook citations. Gemini is used for both answer generation and embeddings.

## Setup

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/apikey)
   and put it in a `.env` file in the project directory:

   ```dotenv
   GEMINI_KEY=your_api_key
   ```

3. Add PDF textbooks to `Textbooks/` and create the vector database:

   ```bash
   python main.py
   ```

On the first run, this reads the PDFs and creates a Gemini-embedded vector
database. When the interactive prompt appears, type `quit`. Then launch the
Streamlit app:

   ```bash
   streamlit run app.py
   ```

Gemini API requests are subject to the free-tier availability and usage limits
on your Google account. Keep your API key private and do not commit it.