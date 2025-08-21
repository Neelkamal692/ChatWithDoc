import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

class WebProcessor:
    def __init__(self):
        self.content = ""
        self.url = ""

    def process_url(self, url: str) -> Dict[str, Any]:
        """Process a web page URL"""
        try:
            # Set headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            # Fetch the webpage
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()

            # Extract text content
            text_content = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)

            if not text_content.strip():
                return {"status": "error", "message": "No text content could be extracted from the webpage"}

            # Extract title
            title = soup.find('title')
            page_title = title.get_text().strip() if title else "Untitled"

            self.content = text_content.strip()
            self.url = url

            return {
                "status": "success",
                "message": "Web page processed successfully",
                "title": page_title,
                "num_pages": 1,
                "num_chunks": len(text_content.split()) // 100 + 1,
                "word_count": len(text_content.split())
            }

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Failed to fetch webpage: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Error processing webpage: {str(e)}"}

    def query_response(self, query: str) -> Dict[str, Any]:
        """Answer a query about the web content"""
        if not self.content:
            return {"status": "error", "message": "No web content available"}
        
        try:
            # Simple keyword-based search
            answer = self._search_content(query, self.content)
            return {
                "status": "success",
                "answer": answer
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_content(self) -> str:
        """Get the extracted content"""
        return self.content

    def _search_content(self, query: str, content: str) -> str:
        """Simple keyword-based search"""
        query_words = query.lower().split()
        
        # Split content into sentences
        sentences = []
        for sentence in content.split('.'):
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short fragments
                sentences.append(sentence)
        
        # Find relevant sentences
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = sum(1 for word in query_words if word in sentence_lower)
            if score > 0:
                relevant_sentences.append((sentence, score))
        
        if not relevant_sentences:
            return "I couldn't find information related to your query on this webpage."
        
        # Sort by relevance and return top sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [sent[0] for sent in relevant_sentences[:3]]
        
        return ". ".join(top_sentences)