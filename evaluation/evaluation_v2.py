from pathlib import Path

from ragas import EvaluationDataset, evaluate

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate, RunConfig

# IMPORTANT:
# Use legacy metric API with evaluate() on Ragas 0.4.3
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)

from chat_with_doc.config.settings import Settings

# Ollama serves generations one at a time, so fan-out here just fills its queue
# and every queued sample burns its own timeout budget while waiting.
run_config = RunConfig(
    timeout=600,
    max_workers=1,
    max_retries=3,
)

DATASET_PATH = Path(
    r"C:\Users\NeelKamalSahu\Desktop\ChatWithDoc\evaluation\results\dataset.jsonl"
)

OUTPUT_PATH = Path(
    r"C:\Users\NeelKamalSahu\Desktop\ChatWithDoc\evaluation\results\final_result.csv"
)


# -------------------------------------------------------
# 1. Get evaluator LLM
# -------------------------------------------------------

base_llm = Settings.get_llm()

# Fail a stalled request fast instead of letting it consume the whole sample budget
base_llm.request_timeout = 120
base_llm.max_retries = 2

ragas_llm = LangchainLLMWrapper(
    base_llm
)


# -------------------------------------------------------
# 2. Get evaluator embeddings
# -------------------------------------------------------

base_embeddings = Settings.get_embeddings()


# AnswerRelevancy requires these methods
if not hasattr(base_embeddings, "embed_query"):
    raise TypeError(
        "Embedding model does not implement embed_query()"
    )

if not hasattr(base_embeddings, "embed_documents"):
    raise TypeError(
        "Embedding model does not implement embed_documents()"
    )


ragas_embeddings = LangchainEmbeddingsWrapper(
    base_embeddings
)


# -------------------------------------------------------
# 3. Load dataset
# -------------------------------------------------------

eval_dataset = EvaluationDataset.from_jsonl(
    DATASET_PATH
)


print("Dataset loaded successfully.")
print("Number of samples:", len(eval_dataset))


# -------------------------------------------------------
# 4. Initialize metrics
# -------------------------------------------------------

context_precision = ContextPrecision(
    llm=ragas_llm
)

context_recall = ContextRecall(
    llm=ragas_llm
)

faithfulness = Faithfulness(
    llm=ragas_llm
)

answer_relevancy = AnswerRelevancy(
    llm=ragas_llm,
    embeddings=ragas_embeddings,
)


# -------------------------------------------------------
# 5. Run Ragas
# -------------------------------------------------------

results = evaluate(
    dataset=eval_dataset,
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
    ],
    run_config=run_config,

    # Score what we can; failed rows come back as NaN instead of losing the whole run
    raise_exceptions=False,
)


# -------------------------------------------------------
# 6. Global scores
# -------------------------------------------------------

print("\nGlobal Scores:")
print(results)


# -------------------------------------------------------
# 7. Row-level scores
# -------------------------------------------------------

df_results = results.to_pandas()


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df_results.to_csv(
    OUTPUT_PATH,
    index=False,
)


print("\nRow-by-row breakdown:")

metric_columns = [
    column
    for column in (
        "user_input",
        "context_precision",
        "context_recall",
        "faithfulness",
        "answer_relevancy",
    )
    if column in df_results.columns
]

print(df_results[metric_columns])


print(f"\nResults saved to:\n{OUTPUT_PATH}")