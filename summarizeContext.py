import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import CTransformers
from langchain.prompts import PromptTemplate
import random


class GermanSummarizer:
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
            temperature=0.1,
            max_tokens=512,
            top_p=0.9,
            n_ctx=2048,
            config={'context_length': 4096}
        )

    def generate_summary(self, context):
        """Generate a summary for the given context."""
        llm = self.initialize_llm()

        prompt = PromptTemplate(
            template="""
            You are a German language summary generator. Your task is to create a single summary 
            based on the given context. The summary should be in English explaining what is in 
            the particular context.

            Context: {context}

            Summary:""",
            input_variables=["context"]
        )

        try:
            formatted_prompt = prompt.format(context=context)
            summary = llm.invoke(formatted_prompt)
            return summary
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return None


def main():
    summarizer = GermanSummarizer(
        pdf_path="germanLanguage.pdf",
        model_file_path="discolm_german_7b_v1.Q4_K_M.gguf"
    )

    # Process the PDF
    summarizer.process_pdf()

    # Generate 3 summaries from random contexts
    for i in range(3):
        print(f"\nGenerating summary {i + 1}:")
        print("-" * 50)

        # Get random context
        context = summarizer.get_random_context()
        print(f"Context:\n{context}\n")

        # Generate and print summary
        summary = summarizer.generate_summary(context)
        print(f"Summary:\n{summary}")
        print("-" * 50)


if __name__ == "__main__":
    main()