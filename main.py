import os
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA

def initialize_embeddings():
    """Initialize and return the embeddings model."""
    # Using a more reliable model that's commonly used
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def process_pdf(pdf_path, text_splitter):
    """Load and process the PDF document."""
    print("Loading and processing the PDF...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    print(f"{len(docs)} document elements loaded.")
    return loader.load_and_split(text_splitter)

def create_vector_db(pages, embeddings, db_path):
    """Create and persist the vector database."""
    print("Creating and saving the vector database...")
    return Chroma.from_documents(pages, embeddings, persist_directory=db_path)

def initialize_llm(model_file_path):
    """Initialize the language model."""
    print("Loading the language model...")
    return CTransformers(
        model="MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF",
        model_file=model_file_path,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        n_ctx=2048,
        config={'context_length': 2048}
    )

def get_quiz_prompt_template():
    """Return the improved quiz generation prompt template."""
    return """
    You are a German language quiz generator. Your task is to create a **single quiz question** based on the given context and in the requested format (Multiple Choice, True/False, or Fill-in-the-Blank). 
    The question should be in **English** and designed to teach German effectively. 

    Requirements for the question:
    - The question text must be in English, teaching a German concept.
    - Only generate **one** question in the requested format.
    - Include all required elements for the requested format.
    - Maintain clarity and consistency throughout the question.

    Requested Question Formats:

    1. **Multiple Choice Question (MCQ)**:
    - Context: Explain the relevant concept in German.
    - Question: Pose a question to the learner in English, teaching German.
    - Choices: Provide four answer options (labeled A, B, C, and D).
    - Correct Answer: Clearly specify the correct option.
    - Difficulty: Indicate whether the question is Easy, Medium, or Hard.
    - Topic: State the topic (e.g., Vocabulary, Verb Conjugation, Sentence Structure).
    - Learning Objective: Specify the learning objective.

    Example:
    Context: The German word "Haus" means "house" in English.
    Question: What does the German word "Haus" mean in English?
    Choices:
    A. Tree
    B. House
    C. Car
    D. Dog
    Correct Answer: B
    Difficulty: Easy
    Topic: Vocabulary
    Learning Objective: Learn basic German vocabulary.

    2. **True/False Question**:
    - Context: Explain the relevant concept in German.
    - Question: Pose a true/false statement in English.
    - Choices: A. True, B. False.
    - Correct Answer: Clearly specify the correct option.
    - Difficulty: Indicate whether the question is Easy, Medium, or Hard.
    - Topic: State the topic.
    - Learning Objective: Specify the learning objective.

    Example:
    Context: The verb "gehen" in German means "to go."
    Question: The verb "gehen" means "to eat."
    Choices:
    A. True
    B. False
    Correct Answer: B
    Difficulty: Medium
    Topic: Verb Conjugation
    Learning Objective: Understand the meaning of common German verbs.

    3. **Fill-in-the-Blank Question**:
    - Context: Explain the relevant concept in German.
    - Question: Provide a sentence with a blank for the learner to fill in.
    - Correct Answer: Provide the correct word or phrase.
    - Difficulty: Indicate whether the question is Easy, Medium, or Hard.
    - Topic: State the topic.
    - Learning Objective: Specify the learning objective.

    Example:
    Context: In German, "Ich bin" means "I am."
    Question: "______ bin müde." (I am tired.)
    Correct Answer: Ich
    Difficulty: Easy
    Topic: Sentence Structure
    Learning Objective: Use basic German sentence structure.

    Context: {context}
    Generate a single quiz question based on the context and format:
    """


def main():
    # Set Hugging Face token
    hf_token = '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'
    os.environ["HF_TOKEN"] = hf_token

    # Configuration
    pdf_path = "learnGerman.pdf"
    db_path = "vector_db"
    model_file_path = "Mistral-7B-Instruct-v0.3.Q4_K_S.gguf"

    # Initialize components
    embeddings = initialize_embeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=70)

    # Process PDF and create vector database
    pages = process_pdf(pdf_path, text_splitter)
    db = create_vector_db(pages, embeddings, db_path)
    print("Setup completed! The vector database has been saved.")

    # Initialize LLM and create QA chain
    llm = initialize_llm(model_file_path)
    quiz_prompt = PromptTemplate(
        input_variables=['context'],
        template=get_quiz_prompt_template()
    )

    # Create retriever and QA chain
    retriever = db.as_retriever(search_kwargs={"k": 2})
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": quiz_prompt}
    )

    print("Bot: Hello! I am here to help you create quizzes from your Basic German document.")

    # Generate quizzes and save to a JSON file
    results = []
    num_quizzes = 10
    for i in range(num_quizzes):
        result = qa_chain.invoke({"query": "Generate a helpful quiz question."})
        results.append({"Quiz": i + 1, "Question": result["result"]})
        print(f"Quiz {i + 1}:")
        print(result["result"])

    # Save results to a JSON file
    output_file = "quizzes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Quizzes have been saved to {output_file}.")

if __name__ == '__main__':
    main()
