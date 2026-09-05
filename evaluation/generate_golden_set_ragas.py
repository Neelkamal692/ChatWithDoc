"""Bootstrap a draft golden set from the fixture documents using ragas'
TestsetGenerator.

This is a *starting point*, not a finished golden set: an LLM invents both
the questions and the "reference" answers by reading the fixture documents,
so every row must be read and corrected by a human before it's trustworthy
as ground truth. Treat the output file as a first draft to edit, not
something to merge into evaluation/datasets/golden_dataset.json as-is.

Compatibility note: ragas 0.4.3 (the latest release on PyPI at the time of
writing) hard-imports `langchain_community.chat_models.vertexai.ChatVertexAI`,
a module that was removed from langchain-community starting in 0.4.0. This
project doesn't use Vertex AI anywhere (it talks to Gemini through
langchain-google-genai), so the shim below just registers a stand-in module
to satisfy that import without needing the real class.
"""

import json
import sys
import types
from pathlib import Path

# Make the project root importable regardless of the current working
# directory or how this script is invoked (`python evaluation/foo.py` only
# puts this file's own folder on sys.path, not the repo root).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if "langchain_community.chat_models.vertexai" not in sys.modules:
    _vertexai_stub = types.ModuleType("langchain_community.chat_models.vertexai")

    class ChatVertexAI:  # pragma: no cover - unused compatibility stub
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "ChatVertexAI is a compatibility stub; this project does not use Vertex AI."
            )

    _vertexai_stub.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _vertexai_stub

from langchain_community.document_loaders import Docx2txtLoader, PyMuPDFLoader, TextLoader
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.testset import TestsetGenerator

from src.chat_with_doc.config.settings import settings
from src.chat_with_doc.embeddings.embedding_service import EmbeddingService

FIXTURES_DIR = PROJECT_ROOT / "evaluation" / "fixtures"
OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "datasets" / "golden_dataset_generated2.json"
TESTSET_SIZE = 12  # roughly 4 questions per fixture document


def load_fixture_documents():
    """Load the three fixture documents as LangChain Document objects."""
    pdf_docs = PyMuPDFLoader(str(FIXTURES_DIR / "udhr.pdf")).load()
    docx_docs = Docx2txtLoader(str(FIXTURES_DIR / "remote_work_policy.docx")).load()
    web_docs = TextLoader(str(FIXTURES_DIR / "python_wikipedia.txt"), encoding="utf-8").load()
    return pdf_docs + docx_docs + web_docs


def main():
    documents = load_fixture_documents()
    print(f"Loaded {len(documents)} source document(s) from {FIXTURES_DIR}")

    generator = TestsetGenerator(
        llm=LangchainLLMWrapper(settings.get_llm()),
        embedding_model=LangchainEmbeddingsWrapper(EmbeddingService.create()),
    )

    testset = generator.generate_with_langchain_docs(documents, testset_size=TESTSET_SIZE)

    draft = [
        {
            "question": sample.eval_sample.user_input,
            "reference": sample.eval_sample.reference,
            "reference_contexts": sample.eval_sample.reference_contexts,
            "synthesizer": sample.synthesizer_name,
        }
        for sample in testset.samples
    ]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(draft)} draft golden-set candidates to {OUTPUT_PATH}")
    print("Review and correct every row by hand before merging into golden_dataset.json.")


if __name__ == "__main__":
    main()
