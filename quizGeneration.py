import os
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import CTransformers
from langchain.prompts import PromptTemplate
import random


class GermanQuizGenerator:
    def __init__(self, pdf_path, model_file_path):
        self.pdf_path = pdf_path
        self.model_file_path = model_file_path
        self.pages = []
        self.chunk_size = 512
        self.chunk_overlap = 30

    def process_pdf(self):
        """Load and split the PDF into chunks."""
        loader = PyPDFLoader(self.pdf_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.pages = loader.load_and_split(text_splitter)
        print(f"Loaded {len(self.pages)} document chunks")
        return self.pages

    def get_random_context(self):
        """Get a random chunk of text from the processed pages."""
        if not self.pages:
            raise ValueError("No pages loaded. Call process_pdf() first.")
        return random.choice(self.pages).page_content

    def initialize_llm(self):
        """Initialize the language model."""
        return CTransformers(
            model="TheBloke/DiscoLM_German_7b_v1-GGUF",
            model_file=self.model_file_path,
            temperature=0.05,  # Reduced temperature for more consistent output
            max_tokens=512,
            top_p=0.95,
            n_ctx=2048,
            config={'context_length': 4096}
        )

    def generate_quiz(self, context):
        """Generate a multiple choice question with 4 options."""
        llm = self.initialize_llm()

        prompt = PromptTemplate(
            template="""TASK: Create one multiple-choice question based on this German text context.

REQUIRED FORMAT:
Question: [Your English question about the German text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Single letter A, B, C, or D]
Explanation: [One sentence explaining why the answer is correct]

INSTRUCTIONS:
1. Question must be about the main concept in the text
2. All options must be complete phrases
3. Only one option can be correct
4. Do not add any other text or formatting
5. Follow the exact format shown above

Context: {context}

OUTPUT (use exact format):""",
            input_variables=["context"]
        )

        try:
            formatted_prompt = prompt.format(context=context)
            quiz_output = llm.invoke(formatted_prompt)

            # Basic format validation
            required_elements = [
                "Question:",
                "A)", "B)", "C)", "D)",
                "Correct Answer:",
                "Explanation:"
            ]

            if all(element in quiz_output for element in required_elements):
                return quiz_output.strip()
            else:
                print("Output missing required elements")
                return None

        except Exception as e:
            print(f"Error generating quiz: {str(e)}")
            return None


def main():
    quiz_generator = GermanQuizGenerator(
        pdf_path="germanLanguage.pdf",
        model_file_path="discolm_german_7b_v1.Q4_K_M.gguf"
    )

    # Process the PDF
    quiz_generator.process_pdf()

    # Generate 3 quiz questions from random contexts
    for i in range(3):
        print(f"\nGenerating Quiz Question {i + 1}:")
        print("-" * 50)

        # Get random context
        context = quiz_generator.get_random_context()
        print(f"Context:\n{context}\n")

        # Generate quiz with retry logic
        quiz = None
        max_attempts = 1  # Increased max attempts
        attempt = 0

        while not quiz and attempt < max_attempts:
            attempt += 1
            if attempt > 1:
                print(f"Attempt {attempt}...")
            quiz = quiz_generator.generate_quiz(context)

        if quiz:
            print("Generated Quiz:")
            print(quiz)
        else:
            print("Failed to generate properly formatted quiz after maximum attempts")
        print("-" * 50)


if __name__ == "__main__":
    main()