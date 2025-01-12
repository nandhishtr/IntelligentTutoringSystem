import os
import json
import re
import random
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA

class QuizGenerator:
    def __init__(self, pdf_path, db_path, model_file_path):
        self.pdf_path = pdf_path
        self.db_path = db_path
        self.model_file_path = model_file_path
        self.used_chunks = set()
        self.used_topics = set()
        self.chunk_size = 512
        self.chunk_overlap = 30

    def initialize_embeddings(self):
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def process_pdf(self):
        loader = PyPDFLoader(self.pdf_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.pages = loader.load_and_split(text_splitter)
        print(f"Loaded {len(self.pages)} document chunks")
        return self.pages

    def get_random_context(self):
        available_chunks = [i for i in range(len(self.pages)) if i not in self.used_chunks]
        print ("Available chunks:", len(available_chunks))
        if not available_chunks:
            self.used_chunks.clear()
            available_chunks = range(len(self.pages))
        chunk_idx = random.choice(available_chunks)
        print("Random context chunk:", chunk_idx)
        self.used_chunks.add(chunk_idx)
        return self.pages[chunk_idx].page_content

    def get_quiz_prompt_template(self):
        """Return the improved quiz generation prompt template."""
        return """
        You are a German language quiz generator. Your task is to create a **single quiz question** based on the given context and in the requested Multiple Choice format.
        The question should be in **English** and designed to teach German effectively.

        Use the given context: {context}
        If the given context is helpful to teach german language, use the context. Else generate question from your knowledge.
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
        - Topic: Choose a single diverse topic relevant to learning German, such as:
          - Vocabulary
          - Verb Conjugation
          - Sentence Structure
          - Articles and Genderv
          - Prepositions
          - Word Order
          - Idiomatic Expressions
          - Cultural References
          - Numbers and Counting
          - Dates and Time
          - Pronunciation
          - Cases (Nominative, Accusative, Dative, Genitive)
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

        Generate a single quiz question based on the context and format:
        """

    def initialize_qa_chain(self):
        llm = CTransformers(
            model="TheBloke/DiscoLM_German_7b_v1-GGUF",
            model_file=self.model_file_path,
            temperature=0.1,
            max_tokens=512,
            top_p=0.9,
            n_ctx=2048,
            config={'context_length': 4096}
        )

        embeddings = self.initialize_embeddings()
        db = Chroma.from_documents(self.pages, embeddings, persist_directory=self.db_path)
        retriever = db.as_retriever(search_kwargs={"k": 2})

        prompt = PromptTemplate(
            template=self.get_quiz_prompt_template(),
            input_variables=["context"]
        )

        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={
                "prompt": prompt,
            }
        )

    def generate_quizzes(self, num_quizzes=5):
        qa_chain = self.initialize_qa_chain()
        results = []

        for i in range(num_quizzes):
            try:
                # Get random context directly
                context = self.get_random_context()
                # Debug: Print the chunk context used for generation
                print(f"\nQuiz {i + 1} Context:\n{context}\n")
                # Generate question
                result = qa_chain.invoke({
                    "query": "Generate a helpful quiz question.",
                    "context": context
                })

                print(f"\nQuiz {i + 1} Raw Output:")
                print(result["result"])
                print("\n")

                # Parse result
                parsed = self.parse_quiz_result(result["result"])
                if parsed:
                    results.append(parsed)
                    print(f"Successfully parsed quiz {i + 1} on topic: {parsed['Topic']}")
                else:
                    print(f"Failed to parse quiz {i + 1}")

            except Exception as e:
                print(f"Error generating quiz {i + 1}: {str(e)}")
                continue

        return results

    def parse_quiz_result(self, result_text):
        """Simplified parser for quiz results."""
        try:
            # Basic patterns for required fields
            question_pattern = r"Question:\s*(.+)"
            choices_pattern = r"([A-D])[.)]\s*(.+)"
            correct_pattern = r"Correct Answer:\s*([A-D])"
            difficulty_pattern = r"Difficulty:\s*(\w+)"
            topic_pattern = r"Topic:\s*(.+?)(?=\n|$)"
            objective_pattern = r"Learning Objective:\s*(.+?)(?=\n|$)"

            # Extract components
            question = re.search(question_pattern, result_text)
            choices = re.findall(choices_pattern, result_text)
            correct = re.search(correct_pattern, result_text)
            difficulty = re.search(difficulty_pattern, result_text)
            topic = re.search(topic_pattern, result_text)
            objective = re.search(objective_pattern, result_text)

            if not all([question, choices, correct, difficulty, topic, objective]):
                print("Missing required components in quiz:")
                print(f"Question found: {bool(question)}")
                print(f"Choices found: {len(choices)}")
                print(f"Correct answer found: {bool(correct)}")
                print(f"Difficulty found: {bool(difficulty)}")
                print(f"Topic found: {bool(topic)}")
                print(f"Objective found: {bool(objective)}")
                return None

            # Create structured output
            parsed_result = {
                "Question": question.group(1).strip(),
                "Choices": [choice[1].strip() for choice in choices],
                "CorrectAnswer": next(choice[1].strip() for choice in choices
                                      if choice[0] == correct.group(1)),
                "Difficulty": difficulty.group(1).strip(),
                "Topic": topic.group(1).strip(),
                "LearningObjective": objective.group(1).strip()
            }

            return parsed_result

        except Exception as e:
            print(f"Error parsing quiz: {str(e)}")
            print("Raw text:")
            print(result_text)
            return None


def main():
    config = {
        "pdf_path": "germanLanguage.pdf",
        "db_path": "vector_db",
        "model_file_path": "discolm_german_7b_v1.Q4_K_M.gguf"
    }

    generator = QuizGenerator(**config)
    generator.process_pdf()
    results = generator.generate_quizzes(3)

    with open("quizzes.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Generated {len(results)} quizzes successfully")


if __name__ == '__main__':
    main()