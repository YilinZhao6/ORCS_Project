# 🧠 ORCS 4201 Final Project – Privacy-Preserving Decision Tool

This project helps organizations determine the most suitable **Privacy-Enhancing Technologies (PETs)** for their use-case through a guided chat, RAG-based retrieval, and recommendation engine.

---

## 🗂 Project Structure

```
.
├── chat_openai.py                      # Interactive assistant to collect use-case details
├── generate_embedding.py              # Converts source.txt into vectorized chunks
├── rag_openai.py                      # Summarize use-case + perform RAG + recommend PETs
├── vector_search.py                   # Supports vector-based retrieval
├── readme.md                          # This file :)
├── source_files/
│   ├── conversation_history.json      # User/assistant conversation logs
│   ├── source.txt                     # Documentation to embed (replace this!)
│   └── vector_search_results.txt      # Top-10 results from vector search
├── vectors/
│   ├── text.npy                       # Array of embedded text chunks
│   └── embeddings.npy                 # Corresponding embedding vectors
```

---

## 🚀 How to Use

### 1. 📄 Prepare Your Documentation
Edit or replace:
```
source_files/source.txt
```
This file should contain any internal documentation, guidance, or background text you want the system to use when recommending privacy tools.

---

### 2. 🔍 Generate Embeddings

```bash
python generate_embedding.py
```

This script will:
- Tokenize and split `source.txt` into ~1000-token chunks with overlap
- Generate vector embeddings for each chunk using OpenAI `text-embedding-3-large`
- Save the outputs to `vectors/text.npy` and `vectors/embeddings.npy`

**Terminal Output Example:**
```
Split text into 45 chunks
Generating embeddings: 100%|████████████████████| 45/45 [00:07<00:00, 6.32it/s, ETA=0.00s]
Saved 45 chunks and embeddings to vectors/text.npy and vectors/embeddings.npy
Embedding dimensions: 3072
```

---

### 3. 💬 Chat with the Assistant

```bash
python chat_openai.py
```

Edit or replace the prompt in chat_openai.py, now the prompt is pretty simple, we can instruct it simulate the **decision tree**.

Here is the current prompt (more like a placeholder):

```bash
"You are a privacy engineering assistant designed to help organizations decide which privacy-preserving technologies (PETs) are appropriate for their specific use-case. Your goal is to collect complete context about the user's application before recommending any PETs. \
You must ask questions **one at a time**, and base each next question on what has already been collected. \
Start by asking the user about their project — for example:\n\
- What is the nature of the project? (e.g., health tech, finance, ML model training, social platform, etc.)\n\
- What types of data are involved? (e.g., personal data, sensitive health info, anonymized data, etc.)\n\
- What is the geographic scope? (e.g., Europe, U.S., global?)\n\
- Is the data shared with external partners or kept internal?\n\
- Is the organization under compliance obligations (e.g., GDPR, HIPAA)?\n\
- What kind of processing is performed on the data? (e.g., centralized, federated, encrypted compute?)\n\
- Are real-time decisions made, or is this for batch analysis or training?\n\
Ask questions **one at a time**, and be brief and precise. Wait for the user to respond before proceeding. \
Once you have enough information to suggest a suitable PET approach, set `continue_asking` to false and stop asking questions. \
Do not make recommendations. Only collect information."
```



This will:
- Ask you structured questions one at a time (e.g. project type, data sensitivity)
- Save the dialogue history to `source_files/conversation_history.json`

**Terminal Output Example:**
```
🧑 You: We're building a fintech app for EU and US users.
🤖 ORCS AI: Thank you. What types of data will you be processing in this app?
...
✅ Info collection complete. You can now make a recommendation based on this context.
```

---

### 4. 🤖 Run RAG + Generate Recommendations

```bash
python rag_openai.py
```

This does:
- Load the chat history
- Use GPT-4o-mini to summarize the project in one sentence
- Perform a vector similarity search on the embedded documentation
- Generate a PET recommendation using GPT-4o
- Save retrieved chunks to `source_files/vector_search_results.txt`

**Terminal Output Example:**
```
🔍 Loading conversation history...
🧠 Summarizing project context...
✅ Summary: A fintech platform for EU/US customers processing sensitive personal and financial data with real-time analytics, under GDPR and US financial compliance.

📚 Retrieving relevant documents...
Saved top 10 chunks to source_files/vector_search_results.txt

🤖 Generating recommendations...

📌 Final Recommendation:

- Use Differential Privacy in the analytics pipeline to ensure data minimization...
- Adopt Homomorphic Encryption for computation on sensitive attributes...
- Comply with GDPR's data localization rules by partitioning your compute zones...
```

---

## 📁 Key File Formats

| File                             | Type         | Description                                            |
|----------------------------------|--------------|--------------------------------------------------------|
| `source.txt`                     | `.txt`       | Input document to be embedded                         |
| `text.npy` / `embeddings.npy`    | `.npy`       | Chunks and embeddings saved in NumPy format           |
| `conversation_history.json`      | `.json`      | List of chat turns: `{user, assistant}`               |
| `vector_search_results.txt`      | `.txt`       | Top-10 relevant docs used in RAG                      |

---

## 🧠 Behind the Scenes

- Uses [OpenAI GPT-4o](https://openai.com) + `text-embedding-3-large`
- Chunking done using `tiktoken` (OpenAI tokenizer)
- Vector search is based on cosine similarity with `sklearn`
- Structured output handled via `pydantic` for consistent parsing

---

