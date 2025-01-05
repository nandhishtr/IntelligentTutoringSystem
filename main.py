import os
import json
import re
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
    You are a German language quiz generator. Your task is to create a **single quiz question** based on the given context and in the requested Multiple Choice format.
    The question should be in **English** and designed to teach German effectively.

    Requirements for the question:
    - The question text must be in English, teaching a German concept.
    - Only generate **one** question in the requested format.
    - Include all required elements for the requested format.
    - Maintain clarity and consistency throughout the question.
    - Do not repeat the same question twice.
    - Do not have anything trailing to the question.

    Requested Question Format:
    - Question: Pose a question to the learner in English, teaching German.
    - Choices: Provide four answer options (labeled A, B, C, and D).
    - Correct Answer: Clearly specify the correct option.
    - Difficulty: Indicate whether the question is Easy, Medium, or Hard.
    - Topic: State the topic (e.g., Vocabulary, Verb Conjugation, Sentence Structure or anything else, just one topic).
    - Learning Objective: Specify the learning objective.

    Stick to the same exact format for every question. Do not deviate.

    Example:
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

    Context: {context}
    Generate a single quiz question based on the context and format:
    """

def parse_quiz_result(result_text):
    """Parse the generated quiz result text into structured JSON."""
    # Use regex to extract elements
    question_match = re.search(r"Question:\s*(.+)", result_text)
    choices_match = re.findall(r"([A-D])\.\s*(.+)", result_text)
    correct_answer_match = re.search(r"Correct Answer:\s*([A-D])", result_text)
    difficulty_match = re.search(r"Difficulty:\s*(.+)", result_text)
    topic_match = re.search(r"Topic:\s*(.+)", result_text)
    learning_objective_match = re.search(r"Learning Objective:\s*(.+)", result_text)

    if not (question_match and choices_match and correct_answer_match and difficulty_match and topic_match and learning_objective_match):
        raise ValueError("Failed to parse the quiz result properly. Check the result format.")

    question = question_match.group(1).strip()
    choices = [choice[1].strip() for choice in choices_match]
    correct_answer = correct_answer_match.group(1).strip()
    difficulty = difficulty_match.group(1).strip()
    topic = topic_match.group(1).strip()
    learning_objective = learning_objective_match.group(1).strip()

    # Safely map the correct answer, check if it's within the bounds of available choices
    try:
        correct_answer_text = choices[ord(correct_answer) - ord('A')]
    except IndexError:
        print(f"Error: Invalid correct answer choice '{correct_answer}' for question: {question}")
        return None  # Return None to indicate the question is invalid

    return {
        "Question": question,
        "Choices": choices,
        "CorrectAnswer": correct_answer_text,  # Map A-D to actual choice text
        "Difficulty": difficulty,
        "Topic": topic,
        "LearningObjective": learning_objective
    }

def save_quizzes_to_json(results, output_file):
    """Save quiz results to a JSON file."""
    print(f"Saving quizzes to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"Quizzes have been saved to {output_file}.")

def main():
    # Set Hugging Face token
    hf_token = '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'
    os.environ["HF_TOKEN"] = hf_token

    # Configuration
    pdf_path = "learnGerman.pdf"
    db_path = "vector_db"
    model_file_path = "Mistral-7B-Instruct-v0.3.Q4_K_S.gguf"
    output_file = "quizzes.json"

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
    num_quizzes = 100
    for i in range(num_quizzes):
        print(f"Generating Quiz {i + 1}...")
        result = qa_chain.invoke({"query": "Generate a helpful quiz question."})
        try:
            parsed_result = parse_quiz_result(result["result"])
            if parsed_result:  # Only append valid results
                results.append(parsed_result)
                print(f"Quiz {i + 1} generated successfully!")
            else:
                print(f"Quiz {i + 1} skipped due to parsing error.")
        except ValueError as e:
            print(f"Error parsing quiz {i + 1}: {e}")
            continue

    # Save results to JSON
    save_quizzes_to_json(results, output_file)

    print("All quizzes have been generated and saved.")

if __name__ == '__main__':
    main()
