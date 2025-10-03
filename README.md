# 🇺🇸 UsTaxPatriot

An interactive **Streamlit app** that helps taxpayers ask questions about U.S. tax rules using **text or voice input**.  
Answers are powered by **GPT-4** with retrieval from IRS documentation (via vector search).  

---

## ✨ Features

- 🎙️ **Voice Input** — Ask tax questions using your microphone.  
- 💬 **Text Input** — Type questions like a normal chatbot.  
- 🎨 **Custom UI Theme** — Clean white cards, deep navy icons (`#00072D`), and modern chat bubbles.  
- ⚡ **Streaming Responses** (optional) with fast retrieval-based answers.  

---

## 🛠️ Tech Stack

- Streamlit — Web UI  
- OpenAI GPT-4 — LLM reasoning  
- LangChain — Retrieval pipeline  
- Pinecone — Vector storage for IRS docs  
- PyPDF2 — PDF ingestion  

---

## 🚀 Getting Started

### 1. Clone repo
    git clone https://github.com/Mehdi-Abidi/UsTaxPatriot.git
    cd UsTaxPatriot

### 2. Create environment
    python -m venv venv
    source venv/bin/activate  # Mac/Linux
    venv\Scripts\activate     # Windows

### 3. Install dependencies
    pip install -r requirements.txt

*(If `requirements.txt` does not exist, create one — should include `streamlit`, `openai`, `langchain`, `pinecone-client`, `PyPDF2`)*

### 4. Add OpenAI & Pinecone API keys
Create a file `.streamlit/secrets.toml` with:
    OPENAI_API_KEY="your_api_key_here"
    PINECONE_API_KEY="your_pinecone_api_key_here"

### 5. Prepare IRS Document Index (Pinecone)
Example Python snippet to load IRS docs and push to Pinecone:

    from langchain.vectorstores import Pinecone
    from langchain_openai import OpenAIEmbeddings
    from langchain.document_loaders import PyPDFLoader

    # Load IRS PDF
    loader = PyPDFLoader("irs-publication.pdf")
    docs = loader.load()

    # Embed and push to Pinecone
    embedding = OpenAIEmbeddings()
    # Example Pinecone usage (make sure Pinecone API is configured)
    # db = Pinecone.from_documents(docs, embedding, index_name="irs-index")

Then update your `app.py` with:
    retriever = db.as_retriever(search_kwargs={"k": 4})

### 6. Run the app
    streamlit run app.py

---

## 🖼️ UI Preview

- User messages appear in **white cards** with taxpayer icon 👤.  
- Assistant messages appear in **light gray cards** with courthouse icon 🏛️.  
- Voice recorder is styled as a **clean white box** with navy mic/playback controls.  

---

## 📚 Example Questions

- "What are the standard deductions for 2023?"  
- "Can I deduct student loan interest if I file jointly?"  
- "How does the child tax credit work?"  
- 🎙️ Voice: "Do I need to report Venmo transactions to the IRS?"  

---

## ⚖️ Disclaimer

This tool is for **educational purposes only** and should **not be considered official tax advice**.  
Always consult the [IRS website](https://www.irs.gov) or a certified tax professional for official guidance.  

---

## 📜 License

MIT License © 2025 — Mehdi Abidi
