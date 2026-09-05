"""One-off script: snapshot a web fixture's extracted text for the golden set."""

from src.chat_with_doc.document_processing.handlers.web import WebHandler

URL = "https://en.wikipedia.org/wiki/Python_(programming_language)"
OUTPUT_PATH = "evaluation/fixtures/python_wikipedia.txt"

handler = WebHandler()
result = handler.process(URL)
print(result)  # status, title, word_count, etc.

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(f"Source: {URL}\n\n")
    f.write(handler.get_content())

print(f"Saved snapshot to {OUTPUT_PATH}")
