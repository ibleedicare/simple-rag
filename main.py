from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
import asyncio
import gradio as gr
import os
from dotenv import load_dotenv
load_dotenv()

# Define the base url for ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
# Create the LLM
llm = Ollama(model="phi3", base_url=OLLAMA_BASE_URL)

# Create the prompt template
prompt_template = """
"<|system|>Tu es un Assistant virtual A.I. Ton but est de répondre aux questions de l'utilisateur le mieux possible en te basant sur le context suivant

Context
===
{context}
===

Répond seulement basé sur le context ci-dessus. Écris une réponse courte et concise. Écris des détails seulement si l'utilisateur demande des détails
<|end|>
<|user|>Quel est la de france ?<|end|><|assistant|>
La captital est Paris<|end|>
<|user|>{question}<|end|><|assistant|>
"""

prompt = PromptTemplate.from_template(prompt_template)
chain = prompt | llm

# Document
markdown = "Phi.md"
loader = UnstructuredMarkdownLoader(markdown)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL))

retriever = vectorstore.as_retriever()

def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

async def ask_question(message, history):
    chunks = []
    async for chunk in rag_chain.astream(message):
        chunks.append(chunk)
        yield "".join(chunks)

demo = gr.ChatInterface(fn=ask_question, title="RAG Chatbot")
demo.launch()
