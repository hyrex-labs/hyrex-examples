"""
Hyrex task definitions for deep research system.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from hyrex import HyrexRegistry
from search_providers import SearchAggregator, DuckDuckGoSearch, WikipediaSearch, ArxivSearch
from openai import OpenAI

load_dotenv()

hy = HyrexRegistry()

# Initialize search providers
search_aggregator = SearchAggregator()
duckduckgo = DuckDuckGoSearch()
wikipedia = WikipediaSearch()
arxiv = ArxivSearch()

# OpenAI client (required)
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")
client = OpenAI()


@hy.task
def decompose_question(question: str, depth: str = "standard") -> Dict[str, Any]:
    """
    Break down a complex question into sub-questions for parallel research.
    """
    print(f"📝 Decomposing question: {question}")
    
    # Determine number of sub-questions based on depth
    num_subquestions = {
        "quick": 2,
        "standard": 4,
        "deep": 6
    }.get(depth, 4)
    
    # Use GPT to decompose the question
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are a research assistant that breaks down complex questions into specific sub-questions for thorough investigation."},
            {"role": "user", "content": f"""Break down this question into {num_subquestions} specific sub-questions that would help answer it comprehensively:
                
Question: {question}

Provide exactly {num_subquestions} sub-questions, one per line, without numbering."""}
        ]
    )
    
    sub_questions = response.choices[0].message.content.strip().split('\n')
    sub_questions = [q.strip() for q in sub_questions if q.strip()][:num_subquestions]
    
    return {
        "original_question": question,
        "sub_questions": sub_questions,
        "depth": depth,
        "timestamp": datetime.now().isoformat()
    }


def generate_mock_subquestions(question: str, num: int) -> List[str]:
    """Generate mock sub-questions when OpenAI is not available."""
    base_questions = [
        f"What is the current state of {question}?",
        f"What are the key challenges in {question}?",
        f"What are recent developments in {question}?",
        f"Who are the main players in {question}?",
        f"What is the future outlook for {question}?",
        f"What are the practical applications of {question}?"
    ]
    return base_questions[:num]


@hy.task
def search_web(query: str, search_type: str = "general") -> Dict[str, Any]:
    """
    Perform web search using specified search type.
    """
    print(f"🔍 Searching {search_type}: {query}")
    
    results = []
    
    if search_type == "general":
        results = duckduckgo.search(query, max_results=5)
    elif search_type == "news":
        results = duckduckgo.search_news(query, max_results=5)
    elif search_type == "wikipedia":
        results = wikipedia.search(query, max_results=3)
    elif search_type == "academic":
        results = arxiv.search(query, max_results=3)
    else:
        results = duckduckgo.search(query, max_results=5)
    
    return {
        "query": query,
        "search_type": search_type,
        "results": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat()
    }


@hy.task
def analyze_results(search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze and extract key insights from search results.
    """
    print(f"🔬 Analyzing {len(search_results)} search result sets")
    
    # Aggregate all results
    all_results = []
    for result_set in search_results:
        if "results" in result_set:
            all_results.extend(result_set["results"])
    
    # Extract key themes (simplified without LLM)
    themes = extract_themes(all_results)
    
    # Find most relevant sources
    top_sources = sorted(all_results, key=lambda x: len(x.get("snippet", "")), reverse=True)[:10]
    
    analysis = {
        "total_results": len(all_results),
        "sources_analyzed": len(search_results),
        "key_themes": themes,
        "top_sources": top_sources,
        "timestamp": datetime.now().isoformat()
    }
    
    if all_results:
        # Use GPT to generate insights
        combined_text = "\n".join([f"- {r.get('title', '')}: {r.get('snippet', '')[:200]}" for r in all_results[:15]])
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a research analyst. Extract key insights from search results."},
                {"role": "user", "content": f"""Analyze these search results and provide 3-5 key insights:

{combined_text}

Provide insights as bullet points."""}
            ]
        )
        
        insights = response.choices[0].message.content.strip().split('\n')
        analysis["key_insights"] = [i.strip().lstrip('- •') for i in insights if i.strip()]
    else:
        analysis["key_insights"] = []
    
    return analysis


def extract_themes(results: List[Dict[str, Any]]) -> List[str]:
    """Extract common themes from search results."""
    # Simple keyword extraction
    text = " ".join([r.get("title", "") + " " + r.get("snippet", "") for r in results])
    words = text.lower().split()
    
    # Common words to ignore
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                  "of", "with", "by", "from", "is", "are", "was", "were", "been", "be",
                  "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
    
    # Count word frequency
    word_freq = {}
    for word in words:
        word = word.strip('.,!?";')
        if len(word) > 4 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top themes
    themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    return [theme[0] for theme in themes]


@hy.task
def synthesize_findings(decomposition: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize all findings into a coherent research report.
    """
    print("📊 Synthesizing findings into report")
    
    report = {
        "question": decomposition["original_question"],
        "research_depth": decomposition["depth"],
        "sub_questions_explored": decomposition["sub_questions"],
        "total_sources_analyzed": analysis["total_results"],
        "key_themes": analysis["key_themes"],
        "key_insights": analysis.get("key_insights", []),
        "top_sources": analysis["top_sources"][:5],
        "timestamp": datetime.now().isoformat()
    }
    
    # Generate executive summary
    insights_text = "\n".join(analysis.get("key_insights", []))
    themes_text = ", ".join(analysis["key_themes"])
    
    if insights_text and themes_text:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a research report writer. Create concise executive summaries."},
                {"role": "user", "content": f"""Create a brief executive summary for this research:

Question: {decomposition['original_question']}
Key Themes: {themes_text}
Key Insights: {insights_text}

Write a 2-3 sentence executive summary."""}
            ]
        )
        
        report["executive_summary"] = response.choices[0].message.content.strip()
    else:
        report["executive_summary"] = "No search results were found for this query."
    
    return report


@hy.task
def research_question(question: str, depth: str = "standard") -> Dict[str, Any]:
    """
    Main research workflow that orchestrates all research tasks.
    """
    print(f"\n🚀 Starting {depth} research for: {question}\n")
    
    # Step 1: Launch ALL tasks in parallel first
    decomposition_task = decompose_question.send(question, depth)
    
    # Launch initial searches on the main question (parallel with decomposition)
    initial_search_tasks = []
    initial_search_tasks.append(search_web.send(question, "general"))
    initial_search_tasks.append(search_web.send(question, "news"))
    initial_search_tasks.append(search_web.send(question, "wikipedia"))
    
    # Add academic search if depth is deep
    if depth == "deep":
        initial_search_tasks.append(search_web.send(question, "academic"))
    
    # Step 2: Wait for decomposition and get sub-questions
    decomposition_task.wait()
    decomposition = decomposition_task.get_result()
    
    # Step 3: Launch searches for sub-questions
    sub_search_tasks = []
    for sub_q in decomposition["sub_questions"]:
        sub_search_tasks.append(search_web.send(sub_q, "general"))
    
    # Add academic searches for sub-questions if depth is deep
    if depth == "deep":
        for sub_q in decomposition["sub_questions"][:2]:  # First 2 sub-questions
            sub_search_tasks.append(search_web.send(sub_q, "academic"))
    
    # Step 4: Wait for ALL search tasks to complete
    all_search_tasks = initial_search_tasks + sub_search_tasks
    search_results = []
    for task in all_search_tasks:
        task.wait()
        search_results.append(task.get_result())
    
    # Step 5: Analyze all results
    analysis_task = analyze_results.send(search_results)
    analysis_task.wait()
    analysis = analysis_task.get_result()
    
    # Step 6: Synthesize findings
    synthesis_task = synthesize_findings.send(decomposition, analysis)
    synthesis_task.wait()
    final_report = synthesis_task.get_result()
    
    print(f"\n✅ Research completed for: {question}\n")
    
    return final_report


# Storage for research results (in production, use a database)
research_cache = {}


@hy.task
def get_research_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a research task.
    """
    # In a real implementation, this would check Hyrex task status
    # For now, return from cache if available
    if task_id in research_cache:
        return {
            "task_id": task_id,
            "status": "completed",
            "result": research_cache[task_id]
        }
    else:
        return {
            "task_id": task_id,
            "status": "processing",
            "result": None
        }


@hy.task
def store_research_result(task_id: str, result: Dict[str, Any]) -> None:
    """
    Store research result in cache.
    """
    research_cache[task_id] = result
    print(f"📁 Stored research result for task {task_id}")


if __name__ == "__main__":
    # Test the research workflow
    result = research_question("What are the latest developments in renewable energy?", "quick")
    print(json.dumps(result, indent=2))