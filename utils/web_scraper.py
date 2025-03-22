import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import logging
from config import SERPER_API_KEY, USER_AGENT, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        self.serper_headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
    
    def search_google(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search Google using the Serper API and return results.
        """
        try:
            payload = json.dumps({
                "q": query,
                "num": num_results
            })
            
            response = requests.post(
                'https://google.serper.dev/search',
                headers=self.serper_headers,
                data=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Search API error: {response.status_code}, {response.text}")
                return []
                
            search_results = response.json()
            
            # Extract and format relevant information
            formatted_results = []
            if 'organic' in search_results:
                for result in search_results['organic']:
                    formatted_results.append({
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('snippet', '')
                    })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error during Google search: {str(e)}")
            return []
    
    def fetch_page_content(self, url: str) -> str:
        """
        Fetch and extract the main content from a webpage.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Remove script and style elements
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit to a reasonable length
            return text[:8000]  # Limit to first 8000 chars
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""
    
    def research_topic(self, topic: str) -> Dict[str, Any]:
        """
        Research a specific AI topic by searching and compiling information.
        """
        search_results = self.search_google(f"{topic} artificial intelligence latest developments", 5)
        
        compiled_research = {
            "topic": topic,
            "search_results": search_results,
            "content": []
        }
        
        # Fetch content from top 3 results
        for i, result in enumerate(search_results[:3]):
            url = result.get('link')
            if url:
                content = self.fetch_page_content(url)
                if content:
                    compiled_research["content"].append({
                        "source": url,
                        "title": result.get('title', ''),
                        "text": content
                    })
                # Be gentle with servers
                if i < len(search_results) - 1:
                    time.sleep(1)
        
        return compiled_research