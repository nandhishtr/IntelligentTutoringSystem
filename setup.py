import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Set Hugging Face token (replace with your token or use environment variables securely)
hf_token = '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'
os.environ["HF_TOKEN"] = hf_token

# Path to the PDF file
pdf_path = "abc.pdf"

# Initialize the embeddings model
embeddings = HuggingFaceEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")

# Load and process the PDF document
print("Loading and processing the PDF...")
loader = PyPDFLoader(pdf_path)
docs = loader.load()

print(len(docs), "document elements loaded.")

# Split the content into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=70)
pages = loader.load_and_split(text_splitter)

# Create a vector database and persist it
db_path = "vector_db"  # Path to the persistent database
print("Creating and saving the vector database...")
db = Chroma.from_documents(pages, embeddings, persist_directory=db_path)

print("Setup completed! The vector database has been saved.")
