import json
from pathlib import Path

from ragas import EvaluationDataset

from chat_with_doc.api.documents import doc_engine


DOCUMENT_PATH = Path(
    r"C:\Users\NeelKamalSahu\Desktop\ChatWithDoc\evaluation\fixtures\udhr.pdf"
)

GOLDEN_DATASET_PATH = Path(
    r"C:\Users\NeelKamalSahu\Desktop\ChatWithDoc\evaluation\datasets\golden_dataset_generated.json"
)

OUTPUT_PATH = Path(
    r"C:\Users\NeelKamalSahu\Desktop\ChatWithDoc\evaluation\results\dataset.jsonl"
)


# -------------------------------------------------------
# 1. Process document
# -------------------------------------------------------

doc = doc_engine.process_document(
    str(DOCUMENT_PATH),
    "application/pdf"
)

print("Document processing:")
print(doc)


# -------------------------------------------------------
# 2. Load golden dataset
# -------------------------------------------------------

with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as file:
    golden_dataset = json.load(file)


samples = []


# -------------------------------------------------------
# 3. Query RAG system
# -------------------------------------------------------

for item in golden_dataset:

    # Validate golden dataset
    if "question" not in item:
        raise KeyError("Golden dataset item missing 'question'")

    if "reference" not in item:
        raise KeyError("Golden dataset item missing 'reference'")

    result = doc_engine.query_documents(item["question"])

    print(result)


    # Validate RAG output
    if "answer" not in result:
        raise KeyError(
            f"Missing 'answer' for question: {item['question']}"
        )

    if "context" not in result:
        raise KeyError(
            f"Missing 'context' for question: {item['question']}"
        )


    contexts = result["context"]


    # ---------------------------------------------------
    # Normalize contexts into list[str]
    # ---------------------------------------------------

    if not isinstance(contexts, list):
        raise TypeError(
            f"result['context'] must be a list, got {type(contexts)}"
        )


    # Case 1:
    # [["chunk 1"], ["chunk 2"]]
    if contexts and isinstance(contexts[0], list):

        contexts = [
            text
            for context_list in contexts
            for text in context_list
        ]


    # Final validation
    if not all(isinstance(context, str) for context in contexts):
        raise TypeError(
            "Every item in retrieved_contexts must be a string."
        )


    samples.append(
        {
            "user_input": item["question"],
            "retrieved_contexts": contexts,
            "response": result["answer"],
            "reference": item["reference"],
        }
    )


# -------------------------------------------------------
# 4. Let Ragas validate schema
# -------------------------------------------------------

dataset = EvaluationDataset.from_list(samples)


print("\nDataset features:")
print(dataset.features())


# -------------------------------------------------------
# 5. Save as JSONL, NOT CSV
# -------------------------------------------------------

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

dataset.to_jsonl(OUTPUT_PATH)

print(f"\nSaved dataset to:\n{OUTPUT_PATH}")