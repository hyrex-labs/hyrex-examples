"""
Search provider implementations using free APIs.
"""
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
import wikipediaapi
import arxiv
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDuckGoSearch:
    """Free web search using DuckDuckGo."""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, body, and href
        """
        import time
        
        # Try with increasing delays if rate-limited
        for delay in [2, 5, 10]:
            time.sleep(delay)
            
            try:
                # Reinitialize DDGS for each attempt
                self.ddgs = DDGS()
                results = list(self.ddgs.text(query, max_results=max_results))
                formatted_results = []
                
                for result in results:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "url": result.get("href", ""),
                        "source": "duckduckgo"
                    })
                
                logger.info(f"DuckDuckGo search for '{query}' returned {len(formatted_results)} results")
                return formatted_results
                
            except Exception as e:
                error_str = str(e)
                if "202" in error_str or "Ratelimit" in error_str:
                    logger.warning(f"DuckDuckGo rate limit, retrying with {delay}s delay: {e}")
                    continue
                else:
                    logger.error(f"DuckDuckGo search error: {e}")
                    return []
        
        # All retries failed
        logger.error(f"DuckDuckGo search failed after retries for: {query}")
        return []
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for news articles using DuckDuckGo."""
        import time
        time.sleep(1)  # Add delay to avoid rate limiting
        
        try:
            results = list(self.ddgs.news(query, max_results=max_results))
            formatted_results = []
            
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),
                    "url": result.get("url", ""),
                    "date": result.get("date", ""),
                    "source": "duckduckgo_news"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"DuckDuckGo news search error: {e}")
            return []


class WikipediaSearch:
    """Free Wikipedia search and content retrieval."""
    
    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='DeepResearch/1.0 (https://github.com/example/deep-research)'
        )
    
    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search Wikipedia for relevant articles.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Wikipedia article summaries
        """
        try:
            # Get the page directly
            page = self.wiki.page(query)
            results = []
            
            if page.exists():
                # Get main article
                summary = page.summary[:500] if len(page.summary) > 500 else page.summary
                results.append({
                    "title": page.title,
                    "snippet": summary + "...",
                    "url": page.fullurl,
                    "source": "wikipedia"
                })
                
                # Get related pages from links
                links = list(page.links.keys())[:max_results-1]
                for link_title in links:
                    link_page = self.wiki.page(link_title)
                    if link_page.exists():
                        link_summary = link_page.summary[:300] if len(link_page.summary) > 300 else link_page.summary
                        results.append({
                            "title": link_page.title,
                            "snippet": link_summary + "...",
                            "url": link_page.fullurl,
                            "source": "wikipedia"
                        })
            
            logger.info(f"Wikipedia search for '{query}' returned {len(results)} results")
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return []
    
    def get_full_content(self, title: str) -> Optional[str]:
        """Get full content of a Wikipedia article."""
        try:
            page = self.wiki.page(title)
            if page.exists():
                return page.text
            return None
        except Exception as e:
            logger.error(f"Wikipedia content retrieval error: {e}")
            return None


class ArxivSearch:
    """Free academic paper search using arXiv."""
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search arXiv for academic papers.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of academic paper metadata
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in search.results():
                results.append({
                    "title": paper.title,
                    "snippet": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
                    "url": paper.entry_id,
                    "authors": [author.name for author in paper.authors],
                    "published": paper.published.strftime("%Y-%m-%d") if paper.published else "",
                    "source": "arxiv"
                })
            
            logger.info(f"arXiv search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return []


class SearchAggregator:
    """Aggregates results from multiple search providers."""
    
    def __init__(self):
        self.duckduckgo = DuckDuckGoSearch()
        self.wikipedia = WikipediaSearch()
        self.arxiv = ArxivSearch()
    
    def search_all(self, query: str, include_academic: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all available providers.
        
        Args:
            query: Search query string
            include_academic: Whether to include arXiv academic search
            
        Returns:
            Dictionary with results from each provider
        """
        results = {
            "web": self.duckduckgo.search(query, max_results=5),
            "news": self.duckduckgo.search_news(query, max_results=3),
            "wikipedia": self.wikipedia.search(query, max_results=2)
        }
        
        if include_academic:
            # Only search arXiv if the query seems academic/technical
            academic_keywords = ["research", "study", "algorithm", "model", "theory", "analysis", 
                               "science", "technology", "engineering", "mathematics", "physics",
                               "computer", "AI", "machine learning", "neural", "quantum"]
            
            if any(keyword.lower() in query.lower() for keyword in academic_keywords):
                results["academic"] = self.arxiv.search(query, max_results=3)
            else:
                results["academic"] = []
        
        total_results = sum(len(r) for r in results.values())
        logger.info(f"Aggregated search for '{query}' returned {total_results} total results")
        
        return results


if __name__ == "__main__":
    # Test the search providers
    aggregator = SearchAggregator()
    results = aggregator.search_all("renewable energy latest developments")
    
    for source, items in results.items():
        print(f"\n{source.upper()} Results:")
        for item in items:
            print(f"  - {item['title']}")
            print(f"    {item['snippet'][:100]}...")