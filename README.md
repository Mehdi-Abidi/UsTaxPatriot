# UsTaxPatriot
An interactive Streamlit app that helps taxpayers ask questions about U.S. tax rules using text or voice input.
Answers are powered by GPT-4 with retrieval from IRS documentation (via vector search).

✨ Features

🎙️ Voice Input — Ask tax questions using your microphone.

💬 Text Input — Type questions like a normal chatbot.

🎨 Custom UI Theme — Clean white cards, deep navy icons (#00072D), and modern chat bubbles.

⚡ Streaming Responses (optional) with fast retrieval-based answers.

🛠️ Tech Stack

Streamlit
 — web UI

OpenAI GPT-4
 — LLM reasoning

LangChain
 — retrieval pipeline

PineconeDB
 — vector storage for IRS docs

PyPDF2
 — PDF ingestion

Getting Started
1. Clone repo
git clone https://github.com/Mehdi-Abidi/UsTaxPatriot.git
cd UsTaxPatriot

2. Create environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

3. Install dependencies
pip install -r requirements.txt


(create requirements.txt if not already should include streamlit, openai, langchain, chromadb, PyPDF2)

4. Add OpenAI API key

Create .streamlit/secrets.toml:

OPENAI_API_KEY="your_api_key_here"

5. Prepare IRS Document Index (Pinecone)
from langchain.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader

# Example to build vectorstore
loader = PyPDFLoader("irs-publication.pdf")
docs = loader.load()

embedding = OpenAIEmbeddings()
db = Chroma.from_documents(docs, embedding, persist_directory="db")

db.persist()


Now update retriever = db.as_retriever(search_kwargs={"k": 4}) in app.py.

6. Run the app
streamlit run app.py

🖼️ UI Preview

User messages appear in white cards with taxpayer icon 👤.

Assistant messages appear in light gray cards with courthouse icon 🏛️.

Voice recorder is styled as a clean white box with navy mic/playback controls.

📚 Example Questions

"What are the standard deductions for 2023?"

"Can I deduct student loan interest if I file jointly?"

"How does the child tax credit work?"

🎙️ Voice: "Do I need to report Venmo transactions to the IRS?"
