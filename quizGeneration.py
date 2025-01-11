import os
import json
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers


class OptimizedHybridRAG:
    def __init__(self, pdf_path, db_path, model_file_path):
        self.pdf_path = pdf_path
        self.db_path = db_path
        self.model_file_path = model_file_path
        self.chunk_size = 1000
        self.chunk_overlap = 20
        self.db = None
        self.llm = None
        self.pages = None  # Store pages for context reference

    def initialize_embeddings(self):
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            encode_kwargs={'normalize_embeddings': True}
        )

    def initialize_llm(self):
        if not self.llm:
            self.llm = CTransformers(
                model="TheBloke/DiscoLM_German_7b_v1-GGUF",
                model_file=self.model_file_path,
                temperature=0.8,
                max_tokens=1024,
                top_p=0.9,
                config={'context_length': 2048}
            )
        return self.llm

    def process_pdf(self):
        print(f"\nLoading PDF from: {self.pdf_path}")
        loader = PyPDFLoader(self.pdf_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.pages = loader.load_and_split(text_splitter)

        # Add page numbers and chunk IDs to metadata
        for i, page in enumerate(self.pages):
            page.metadata.update({
                'chunk_id': i,
                'page_number': page.metadata.get('page', 'Unknown'),
                'chunk_text': page.page_content[:100] + "..."  # Store preview of chunk content
            })

        self.db = Chroma.from_documents(
            self.pages,
            self.initialize_embeddings(),
            persist_directory=self.db_path
        )
        print(f"Processed {len(self.pages)} document chunks")
        return self.pages

    def get_quiz_prompt_template(self):
        """Simplified and optimized quiz prompt template."""
        return """
        Context: {context}

        Generate a single German language quiz question in English with:
        - Question about the context
        - **must** have only Four choices (A-D)
        - Correct answer
        - Difficulty (Easy/Medium/Hard)
        - Topic
        - Learning goal

        Format:
        Question: [question]
        A) [choice]
        B) [choice]
        C) [choice]
        D) [choice]
        Correct Answer: [A/B/C/D]
        Difficulty: [level]
        Topic: [topic]
        Learning Objective: [objective]
        """

    def parse_quiz_result(self, result_text):
        """Optimized quiz result parser."""
        patterns = {
            'question': r"Question:\s*(.+?)(?=\n|$)",
            'choices': r"([A-D])[.)]\s*(.+?)(?=\n|[A-D]|Correct|$)",
            'correct': r"Correct Answer:\s*([A-D])",
            'difficulty': r"Difficulty:\s*(\w+)",
            'topic': r"Topic:\s*(.+?)(?=\n|$)",
            'objective': r"Learning Objective:\s*(.+?)(?=\n|$)"
        }

        try:
            matches = {
                key: re.search(pattern, result_text, re.DOTALL)
                for key, pattern in patterns.items()
            }

            if not all(matches.values()):
                return None

            choices = re.findall(patterns['choices'], result_text)
            correct_answer = matches['correct'].group(1)

            return {
                "Question": matches['question'].group(1).strip(),
                "Choices": [choice[1].strip() for choice in choices],
                "CorrectAnswer": next(choice[1].strip() for choice in choices
                                      if choice[0] == correct_answer),
                "Difficulty": matches['difficulty'].group(1).strip(),
                "Topic": matches['topic'].group(1).strip(),
                "LearningObjective": matches['objective'].group(1).strip()
            }

        except Exception as e:
            print(f"Parse error: {str(e)}")
            return None

    def generate_quiz(self, topic_keywords):
        """Generate quiz with context information."""
        try:
            if not self.db:
                raise ValueError("Database not initialized. Run process_pdf first.")

            # Get context with document reference
            docs = self.db.similarity_search(topic_keywords, k=1)

            if not docs:
                return None

            context = docs[0]
            llm = self.initialize_llm()

            prompt = PromptTemplate(
                template=self.get_quiz_prompt_template(),
                input_variables=["context"]
            ).format(context=context.page_content)

            result = llm.invoke(prompt)
            parsed_quiz = self.parse_quiz_result(result)

            if parsed_quiz:
                # Add context information to quiz
                parsed_quiz["SourceContext"] = {
                    "ChunkID": context.metadata.get('chunk_id', 'Unknown'),
                    "PageNumber": context.metadata.get('page_number', 'Unknown'),
                    "ContextPreview": context.metadata.get('chunk_text', 'Not available')
                }

            return parsed_quiz

        except Exception as e:
            print(f"Quiz generation error: {str(e)}")
            return None

    def generate_multiple_quizzes(self, num_quizzes=5):
        """Generate multiple quizzes with context tracking."""
        topics = [
            "German grammar rules",
            "German vocabulary",
            "German sentence structure",
            "German pronunciation",
            "German verb conjugation",
            "German articles",
            "German cases",
            "German tenses",
            "German adjectives",
            "German prepositions",
            "German pronouns",
            "German negations",
            "German culture"
        ]

        results = []
        for i in range(num_quizzes):
            topic = topics[i % len(topics)]
            quiz = self.generate_quiz(topic)
            if quiz:
                results.append(quiz)
                print(f"\nGenerated quiz {len(results)} on {quiz['Topic']}")
                print(f"Source Context:")
                print(f"- Chunk ID: {quiz['SourceContext']['ChunkID']}")
                print(f"- Page Number: {quiz['SourceContext']['PageNumber']}")
                print(f"- Context Preview: {quiz['SourceContext']['ContextPreview']}")

        return results


def main():
    config = {
        "pdf_path": "germanLanguage.pdf",
        "db_path": "vector_db",
        "model_file_path": "discolm_german_7b_v1.Q5_K_M.gguf"
    }

    rag = OptimizedHybridRAG(**config)
    rag.process_pdf()
    quizzes = rag.generate_multiple_quizzes(5)

    # Save quizzes with context information
    with open("quizzes.json", "w", encoding="utf-8") as f:
        json.dump(quizzes, f, ensure_ascii=False, indent=2)

    print(f"\nGenerated {len(quizzes)} quizzes")

    # Print summary of contexts used
    print("\nContext Usage Summary:")
    contexts_used = {}
    for quiz in quizzes:
        chunk_id = quiz['SourceContext']['ChunkID']
        if chunk_id in contexts_used:
            contexts_used[chunk_id] += 1
        else:
            contexts_used[chunk_id] = 1

    for chunk_id, count in contexts_used.items():
        print(f"Chunk {chunk_id} was used {count} times")


if __name__ == '__main__':
    main()