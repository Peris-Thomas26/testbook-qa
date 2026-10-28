# Textbook Q&A

Textbook Q&A is a question-answering app that helps people find and understand
information in a collection of PDF documents. Ask a question in everyday
language, get an answer generated from relevant passages, and see citations
pointing back to the source textbook and page.

## Why I built this

Long textbooks and reference documents can be difficult to search when you
already know what you need to learn but not which chapter or page contains it.
This project explores how to make that material easier to navigate: instead of
manually searching one PDF at a time, readers can ask a focused question and
get a concise, educational response grounded in the documents.

The project also provides a starting point for experimenting with retrieval-
augmented generation (RAG): documents are split into searchable pieces, those
pieces are indexed, and relevant passages are provided to a language model
when it answers.

## How it works

1. The app extracts text and page information from PDFs in `Textbooks/`.
2. It splits the text into overlapping chunks and creates vector embeddings
   locally with the `sentence-transformers/all-MiniLM-L6-v2` model.
3. Chroma stores the embeddings in a local vector database (`vector_db_minilm/`)
   so relevant passages can be retrieved for a question.
4. Gemini generates an answer using the retrieved passages. The app displays
   source citations with the textbook name and page.

The local embedding model is separate from Gemini: Gemini is used for answer
generation, not for creating the document embeddings.

## Why use RAG?

Retrieval-augmented generation (RAG) combines document search with a language
model. Before answering, the system retrieves passages that appear relevant to
the question and includes them in the model's prompt. This can make answers
more relevant to an organization's own materials than asking a general-purpose
model without those materials. It can also make answers easier to verify when
the chatbot points people to the source passages.

RAG does not train the model on the documents. It searches an index and supplies
selected content at answer time, which can make it practical to update the
knowledge base by re-indexing changed documents. The approach is useful for
knowledge discovery, but it does not guarantee that an answer is correct or
that every relevant passage will be retrieved.

## Context windows and RAG limitations

A language model has a finite context window: a limit on how much text it can
consider in one request. The prompt, question, retrieved passages, and generated
answer all use this capacity. Supplying an entire library is usually
impractical, so RAG searches for a smaller set of passages to fit into the
request. This helps focus the answer, but introduces trade-offs:

- **Retrieval can miss the right evidence.** Different wording, poor PDF text
  extraction, or an unsuitable chunk size can prevent the best passage from
  being found.
- **More context is not automatically better.** Too many or overly long
  passages can crowd the context window, add irrelevant details, and increase
  latency and model usage.
- **Important details can be split across chunks.** Chunk size and overlap
  affect whether a passage contains enough surrounding explanation. This
  project currently uses chunks of 1,000 characters, 200 characters of overlap,
  and retrieves up to five chunks; these are starting settings, not universal
  values.
- **Sources can disagree or become outdated.** A chatbot needs document
  ownership, versioning, and clear rules for handling conflicting guidance.
- **Answers still need verification.** A model can misunderstand the source,
  overstate what it says, or respond when the retrieved content is insufficient.
  Citations help people check an answer but do not prove it is correct.

## Potential organizational chatbot applications

The same RAG pattern could support chatbots for teams that need answers from
their own reference material:

| Team | Example knowledge base | Example chatbot task |
|---|---|---|
| Learning and development | Training manuals, course notes, study guides | Explain a concept and point to the lesson that covers it |
| Customer support | Product guides, troubleshooting manuals, approved FAQs | Suggest documented troubleshooting steps |
| Operations | Standard operating procedures, process handbooks | Find the required steps for a workflow |
| Human resources | Employee handbooks, benefits guides, policy documents | Locate relevant policy information and direct staff to the official source |
| Engineering | Architecture guides, technical manuals, runbooks | Find documented service procedures and relevant runbook sections |
| Sales and marketing | Product descriptions, approved messaging, research reports | Retrieve approved product details for a sales conversation |

These are illustrative scenarios, not reports of existing deployments. For
example:

- **Exam revision assistant:** A student asks for an explanation of a topic,
  requests a short summary, then generates practice questions from the course
  material. They can use the citations to revisit the relevant textbook pages.
- **New employee policy assistant:** A new hire asks where to find information
  about a workplace policy. The chatbot summarizes the relevant handbook
  passage and links them to the official policy section. Sensitive questions
  can be referred to HR rather than treated as authoritative advice.
- **Customer troubleshooting assistant:** A support agent or customer describes
  a product issue. The chatbot retrieves relevant troubleshooting steps and
  identifies the guide and section so the user can confirm the instructions.
- **Operations procedure assistant:** A staff member asks what checks are
  required before completing a process. The chatbot surfaces the relevant
  procedure and flags when the source does not cover the question.
- **Engineering runbook assistant:** An engineer searches approved runbooks for
  a documented diagnostic or recovery procedure. Production actions should
  remain subject to the organization's review and approval process.

For revision, the chatbot can make long reading lists easier to study by
summarizing retrieved material, explaining difficult ideas in simpler language,
comparing concepts found in the sources, and generating practice questions.
Students should use it as a study aid, verify important details against the
course material, and follow their institution's rules for AI use.

## What it would take to use this for an organization

This repository is a local prototype, not a production-ready, multi-team
chatbot. A team-oriented deployment would typically need:

1. **Curated sources:** Agree which documents are trusted, who owns them, and
   how outdated or conflicting versions are handled.
2. **Ingestion and refresh:** Support the team's actual document sources and
   formats, extract their text reliably, and re-index updates on a schedule or
   when content changes.
3. **Access control:** Authenticate users and ensure retrieval only returns
   documents each user is permitted to see. Separate teams' indexes or enforce
   document-level permissions where needed.
4. **Safe answer behavior:** Show citations, say when evidence is insufficient,
   and route high-impact or sensitive questions to a qualified person.
5. **Evaluation and operations:** Test representative questions and citations,
   monitor quality, latency, and cost, and provide a way to report incorrect
   answers and remove content.
6. **Privacy and governance:** Review the chosen model provider, data handling,
   retention, regulatory needs, and organizational policies before sending
   internal content to an external API.

The current app reads PDF files from one local `Textbooks/` directory and uses
a local vector database. It does not provide user authentication, per-document
permissions, team separation, document synchronization, or production
monitoring. Those capabilities must be designed and implemented before using
it with confidential organizational content or as an authoritative source.

## Current scope and limitations

- Input is PDF files placed directly in `Textbooks/`.
- The vector database is local to this project; it is not a shared team service.
- Answers depend on the quality and coverage of the PDF text and retrieved
  passages. Check the cited source before relying on an answer.
- Citations include textbook and page information. Chapter labels are inferred
  from page text and may be reported as "Unknown Chapter."
- The app does not currently enforce organizational identity or document-level
  access permissions.
- Gemini API access, latency, and usage limits depend on your Google account
  and network connection.

## Setup

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a Gemini API key in
   [Google AI Studio](https://aistudio.google.com/apikey) and put it in a
   `.env` file in the project directory:

   ```dotenv
   GEMINI_KEY=your_api_key
   ```

3. Add PDF files to `Textbooks/`. On the first run, start the program to
   extract, embed, and index them:

   ```bash
   python main.py
   ```

   The first indexing run can take time, especially with large PDFs. When the
   interactive prompt appears, type `quit`.

4. Start the web app:

   ```bash
   streamlit run app.py
   ```

The app loads the existing local vector database on startup and does not
automatically detect changed PDFs. To index a changed collection, remove the
local `vector_db_minilm/` database directory and run `python main.py` again;
this rebuilds the index from the PDFs currently in `Textbooks/`.

## Keeping credentials safe

Keep your Gemini API key private. Store it in `.env`, do not commit that file,
and do not share it in screenshots or logs. Gemini requests are subject to
Google AI Studio availability and usage limits.
