import os
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import CTransformers
from langchain.prompts import PromptTemplate
import random
import json


class GermanQuizGenerator:
    def __init__(self, pdf_path, model_file_path):
        self.pdf_path = pdf_path
        self.model_file_path = model_file_path
        self.pages = []
        self.chunk_size = 1024
        self.chunk_overlap = 30

        # Keywords that indicate irrelevant content
        self.irrelevant_indicators = [
            'license', 'copyright', 'invariant', 'permission', 'acknowledgment',
            'cover text', 'warranty', 'disclaimer', 'contributors', 'front-cover',
            'back-cover', 'isbn', 'published', 'edition', 'rights reserved', 'undeveloped'
        ]

    def is_relevant_content(self, text):
        """
        Check if the content doesn't contain irrelevant metadata.
        Returns True if content doesn't contain any irrelevant indicators.
        """
        text_lower = text.lower()
        return not any(indicator in text_lower for indicator in self.irrelevant_indicators)

    def process_pdf(self):
        """Load and split the PDF into chunks, filtering out irrelevant content."""
        loader = PyPDFLoader(self.pdf_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        all_pages = loader.load_and_split(text_splitter)

        # Filter out irrelevant content
        self.pages = [page for page in all_pages if self.is_relevant_content(page.page_content)]

        print(f"Loaded {len(all_pages)} total chunks")
        print(f"Filtered to {len(self.pages)} relevant chunks")
        return self.pages

    def get_random_context(self):
        """Get a random chunk of text from the processed pages."""
        if not self.pages:
            raise ValueError("No relevant pages loaded. Call process_pdf() first.")
        return random.choice(self.pages).page_content

    def initialize_llm(self):
        """Initialize the language model."""
        return CTransformers(
            model="TheBloke/DiscoLM_German_7b_v1-GGUF",
            model_file=self.model_file_path,
            temperature=0.05,
            max_tokens=512,
            top_p=0.95,
            n_ctx=2048,
            config={'context_length': 4096}
        )

    def parse_quiz_output(self, quiz_output):
        """Parse the quiz output into a structured dictionary format."""
        lines = quiz_output.strip().split('\n')
        quiz_dict = {}
        choices = []

        for line in lines:
            if line.startswith('Topic:'):
                quiz_dict['Topic'] = line.replace('Topic:', '').strip()
            elif line.startswith('Difficulty:'):
                quiz_dict['Difficulty'] = line.replace('Difficulty:', '').strip()
            elif line.startswith('Question:'):
                quiz_dict['Question'] = line.replace('Question:', '').strip()
            elif any(line.startswith(f'{opt})') for opt in ['A', 'B', 'C', 'D']):
                option_text = line[3:].strip()
                choices.append(option_text)
            elif line.startswith('Correct Answer:'):
                answer_letter = line.replace('Correct Answer:', '').strip()
                letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                index = letter_to_index.get(answer_letter, 0)
                quiz_dict['CorrectAnswer'] = choices[index] if choices else ''
            elif line.startswith('Explanation:'):
                quiz_dict['Explanation'] = line.replace('Explanation:', '').strip()

        quiz_dict['Choices'] = choices
        return quiz_dict

    def generate_quiz(self, context):
        """Generate a multiple choice question with topic and difficulty level."""
        llm = self.initialize_llm()

        prompt = PromptTemplate(
            template="""TASK: Create one multiple-choice question based on this German text context.

REQUIRED FORMAT:
Topic: [Classify the main topic: Grammar/Vocabulary/Culture/History/Literature/Conversation]
Difficulty: [Easy/Medium/Hard]
Question: [Your English question about the German text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Single letter A, B, C, or D]
Explanation: [One sentence explaining why the answer is correct]

INSTRUCTIONS:
1. Questions MUST focus on German language elements such as:
   - Meanings of German words
   - German grammar rules
   - German word forms or conjugations
   - German sentence structure
   - German pronunciation
2. DO NOT create questions about:
   - Cultural facts or stereotypes
   - Historical information
   - General knowledge
   - Geography
3. All options must be complete phrases
4. Only one option can be correct
5. Question should test actual language knowledge
6. Only one topic and the it should reflect the main subject matter
7. Difficulty should be based on complexity of concept and language used
8. Do not add any other text or formatting
9. Follow the exact format shown above


Context: {context}

OUTPUT (use exact format):""",
            input_variables=["context"]
        )

        try:
            formatted_prompt = prompt.format(context=context)
            quiz_output = llm.invoke(formatted_prompt)

            # Basic format validation
            required_elements = [
                "Topic:",
                "Difficulty:",
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

    def save_quizzes_to_json(self, quizzes, output_file="german_quizzes.json"):
        """Save the generated quizzes to a JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(quizzes, f, ensure_ascii=False, indent=4)
            print(f"Successfully saved quizzes to {output_file}")
        except Exception as e:
            print(f"Error saving quizzes to JSON: {str(e)}")

    def generate_multiple_quizzes(self, count=3):
        """Generate multiple quizzes"""
        # Generate 3 quiz questions from random contexts
        quizzes = []
        for i in range(count):
            print(f"\nGenerating Quiz Question {i + 1}:")
            print("-" * 50)

            # Get random context
            context = self.get_random_context()
            print(f"Context:\n{context}\n")

            # Generate quiz with retry logic
            quiz = None
            max_attempts = 1
            attempt = 0

            while not quiz and attempt < max_attempts:
                attempt += 1
                if attempt > 1:
                    print(f"Attempt {attempt}...")
                quiz = self.generate_quiz(context)

            if quiz:
                print("Generated Quiz:")
                print(quiz)
                # Parse and store the quiz
                parsed_quiz = self.parse_quiz_output(quiz)
                quizzes.append(parsed_quiz)
            else:
                print("Failed to generate properly formatted quiz after maximum attempts")
            print("-" * 50)
        return quizzes


def main():
    quiz_generator = GermanQuizGenerator(
        pdf_path="germanLanguage.pdf",
        model_file_path="discolm_german_7b_v1.Q4_K_M.gguf"
    )

    # Process the PDF
    quiz_generator.process_pdf()

    # Store all generated quizzes
    all_quizzes = quiz_generator.generate_multiple_quizzes(100)

    # Save all generated quizzes to JSON file
    quiz_generator.save_quizzes_to_json(all_quizzes)


if __name__ == "__main__":
    main()