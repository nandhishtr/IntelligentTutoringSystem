import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA

# Set Hugging Face token (replace with your token or use environment variables securely)
hf_token = 'xyz'
os.environ["HF_TOKEN"] = hf_token

# Path to the PDF file
pdf_path = "notesLA12122.pdf"

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

# Initialize the LLM model
print("Loading the language model...")
model_file_path = r"D:\Studies@OVGU\Semester-3\HCAT\IntelligentTutoringSystem\Mistral-7B-Instruct-v0.3.Q4_K_S.gguf"
llm = CTransformers(model="MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF",
                    model_file=model_file_path,
                    temperature=0.7,
                    max_tokens=2048,
                    top_p=1,
                    n_ctx=2048,
                    config={'context_length': 2048})

# Define the quiz generation prompt template
quiz_prompt_template = """
Use the following information to generate a quiz question in the requested format (Multiple Choice, True/False, or Fill-in-the-Blank).

Each question should include the following:
- The question text.
- The answer choices (for MCQs).
- The correct answer.
- The difficulty level (Easy, Medium, Hard).
- The topic of the question.
- The learning objective of the question.

Question Format Examples:

1. **Multiple Choice Question (MCQ)**:
Context: A matrix is a rectangular array of numbers arranged in rows and columns.
Question: What is a matrix?
Choices:
A. A single number.
B. A rectangular array of numbers arranged in rows and columns.
C. A complex number.
D. A type of polynomial.
Correct Answer: B
Difficulty: Medium
Topic: Matrices
Learning Objective: Define a matrix.

2. **True/False Question**:
Context: The square of any real number is always positive.
Question: Is the square of any real number always positive?
Choices:
A. True
B. False
Correct Answer: A
Difficulty: Easy
Topic: Numbers
Learning Objective: Understand the properties of real numbers.

3. **Fill-in-the-Blank Question**:
Context: The derivative of a constant is zero.
Question: The derivative of a constant is ________.
Correct Answer: zero
Difficulty: Easy
Topic: Calculus
Learning Objective: Apply basic derivative rules.

Context: {context}
Generate a helpful quiz question:
"""

# Create a prompt template for quiz generation
quiz_prompt = PromptTemplate(input_variables=['context'], template=quiz_prompt_template)

# Create a retriever from the vector database
retriever = db.as_retriever(search_kwargs={"k": 2})

# Create a QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm, retriever=retriever, chain_type_kwargs={"prompt": quiz_prompt}
)

print("Bot: Hello! I am here to help you create quizzes from your Linear Algebra document.")

# Generate quizzes
num_quizzes = 5  # Specify the number of quiz questions to generate
for i in range(num_quizzes):
    result = qa_chain.invoke({"query": "Generate a helpful quiz question."})
    print(f"Quiz {i + 1}:")
    print(result["result"])
    print("\n")
