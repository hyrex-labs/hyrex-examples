import random
import time
import os
from enum import Enum
from typing import Optional

from hyrex import HyrexRegistry
from dotenv import load_dotenv
from chatbot import ChatDatabase
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

hy = HyrexRegistry()

# Initialize clients once at module level
db = ChatDatabase()
client = OpenAI()


@hy.task
def test_task():
    """A simple test task that sleeps for a random duration."""
    sleep_duration = random.uniform(0, 2)
    time.sleep(sleep_duration)


@hy.task
def send_n_test_tasks(n: int):
    """Enqueue n test_task instances."""
    for i in range(n):
        test_task.send()
    return f"Enqueued {n} test tasks"


# Memory retrieval tasks
@hy.task
def search_semantic_memories(query_embedding: list, limit: int = 3):
    """Search for semantically similar memories."""
    memories = db.search_memories(query_embedding, conversation_id=None, limit=limit)
    return {"result": memories}


@hy.task  
def get_random_memories(limit: int = 2):
    """Get random memories from the global memory bank."""
    memories = db.get_random_memories(conversation_id=None, limit=limit)
    return {"result": memories}


# Chatbot tasks
@hy.task
def process_message(conversation_id: int, message: str):
    """Process a user message and generate a response."""
    try:
        
        # Generate embedding for the incoming message to search memories
        embedding_response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=message
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Launch parallel memory retrieval tasks
        semantic_task = search_semantic_memories.send(query_embedding, limit=3)
        random_task = get_random_memories.send(limit=2)
        
        # Wait for both tasks to complete
        semantic_task.wait()
        random_task.wait()
        
        # Get the actual results after waiting
        semantic_result = semantic_task.get_result()
        random_result = random_task.get_result()
        
        # Extract the actual memories from the dict wrapper
        relevant_memories = semantic_result.get("result", []) if semantic_result else []
        random_memories = random_result.get("result", []) if random_result else []
        
        # Get recent conversation history for context (limit at database level)
        # This prevents slow responses and reduces token usage
        MAX_HISTORY_MESSAGES = 10
        recent_history = db.get_conversation_history(conversation_id, limit=MAX_HISTORY_MESSAGES)
        
        # Build system prompt with memories
        system_content = "You are a helpful assistant. Prefer brief responses (1-3 sentences) unless the conversation benefits from more detail."
        
        # Add relevant memories if any
        if relevant_memories:
            relevant_text = "\n".join([f"- {mem['fact']}" for mem in relevant_memories])
            system_content += f"\n\nRelevant memories (semantically related to current topic):\n{relevant_text}"
        
        # Add random memories if any (excluding ones already in relevant)
        relevant_facts = {mem['fact'] for mem in relevant_memories}
        unique_random = [mem for mem in random_memories if mem['fact'] not in relevant_facts]
        
        if unique_random:
            random_text = "\n".join([f"- {mem['fact']}" for mem in unique_random])
            system_content += f"\n\nOther memories (random selection, may offer interesting connections):\n{random_text}"
        
        if relevant_memories or unique_random:
            system_content += "\n\nUse these memories to provide more personalized and contextual responses."
        
        # Build messages for ChatGPT
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        # Add recent conversation history (excluding the current message we just added)
        for msg in recent_history[:-1]:  # Skip the last message since it's the one we just added
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Call ChatGPT API
        completion = client.chat.completions.create(
            model="gpt-5",
            messages=messages
        )
        
        response = completion.choices[0].message.content
        
        # Check if response is empty or None
        if not response or not response.strip():
            response = "I apologize, but I'm having trouble generating a response right now. Please try again."
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        response = f"Sorry, I encountered an error: {str(e)}"
    
    # Add assistant response to database
    db.add_message(conversation_id, "assistant", response)
    
    print(f"Processed message for conversation {conversation_id}, response: {response[:100] if response else 'EMPTY'}")
    
    # Trigger memory extraction from just this exchange
    extract_memories_from_exchange.send(conversation_id, message, response)
    
    return response


@hy.task
def extract_memories_from_exchange(conversation_id: int, user_message: str, assistant_response: str):
    """Extract important facts from the user's message and store as memories."""
    try:
        # Use GPT to extract important facts from the user's message
        extraction_prompt = f"""Extract ONLY significant, long-term facts about the USER that would be valuable to remember across many future conversations.

IMPORTANT CRITERIA - Only extract facts that are:
1. About the user as a person (not about the current task or conversation)
2. Likely to remain true for weeks or months
3. Useful for personalizing future interactions

GOOD examples to extract:
- "My name is John"
- "I work as a software engineer"
- "I prefer Python over JavaScript"
- "I'm building a chatbot for my company"
- "I live in San Francisco"
- "I'm interested in machine learning"

BAD examples (DO NOT extract):
- Formatting preferences in current message
- Temporary conversation context
- What the user wants right now
- Minor preferences about output format
- Debugging issues or error fixes
- Trivial adjustments or corrections

User message:
{user_message}

List 1-3 SIGNIFICANT facts about the user as a person (one per line, NO NUMBERING or bullet points - just the plain fact). If there are no significant long-term facts about the user, respond with 'NONE'.

Example of correct format:
The user works as a software engineer
The user lives in San Francisco
The user prefers Python over JavaScript

Example of INCORRECT format (do not do this):
1. The user works as a software engineer
2. The user lives in San Francisco
- The user prefers Python over JavaScript"""
        
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You extract key facts from conversations."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        facts_text = completion.choices[0].message.content.strip()
        
        if facts_text and facts_text != "NONE":
            facts = [f.strip() for f in facts_text.split('\n') if f.strip()]
            
            # Generate embeddings and store each fact
            for fact in facts[:3]:  # Limit to 3 facts per extraction
                # Generate embedding for the fact
                embedding_response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=fact
                )
                embedding = embedding_response.data[0].embedding
                
                # Store the memory
                db.add_memory(conversation_id, fact, embedding)
                print(f"Stored memory: {fact[:100]}")
        
    except Exception as e:
        print(f"Error extracting memories: {e}")


class MemoryAction(str, Enum):
    KEEP_BOTH = "keep_both"
    CONSOLIDATE = "consolidate"
    DELETE_FIRST = "delete_first"
    DELETE_SECOND = "delete_second"


class MemoryAnalysis(BaseModel):
    action: MemoryAction
    reason: str
    consolidated_memory: Optional[str] = None


@hy.task(cron="*/10 * * * *", backfill=False)  # Run every 10 minutes
def consolidate_memories():
    """Periodically review and consolidate similar or redundant memories."""
    print("Starting memory consolidation...")
    
    # Get a small sample of memories to review
    memories = db.get_random_memories(limit=5)
    
    if len(memories) < 2:
        print("Not enough memories to consolidate")
        return
    
    # Compare all pairs for potential duplicates/consolidation
    for i in range(len(memories)):
        for j in range(i + 1, len(memories)):
            mem1 = memories[i]
            mem2 = memories[j]
            
            try:
                completion = client.beta.chat.completions.parse(
                    model="gpt-5",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze pairs of user memories to identify duplicates or opportunities for consolidation."
                        },
                        {
                            "role": "user",
                            "content": f"""Analyze these two memories:

Memory 1: {mem1['fact']}
Memory 2: {mem2['fact']}

Determine if they contain duplicate information or can be consolidated. If consolidating, provide a single improved memory that captures both facts."""
                        }
                    ],
                    response_format=MemoryAnalysis
                )
                
                analysis = completion.choices[0].message.parsed
                
                if analysis.action == MemoryAction.DELETE_FIRST:
                    db.delete_memory(mem1['id'])
                    print(f"Deleted redundant memory: {mem1['fact'][:50]}...")
                    break  # mem1 is deleted, skip remaining comparisons with it
                    
                elif analysis.action == MemoryAction.DELETE_SECOND:
                    db.delete_memory(mem2['id'])
                    print(f"Deleted redundant memory: {mem2['fact'][:50]}...")
                    
                elif analysis.action == MemoryAction.CONSOLIDATE and analysis.consolidated_memory:
                    # Delete both old memories
                    db.delete_memory(mem1['id'])
                    db.delete_memory(mem2['id'])
                    
                    # Create consolidated memory with embedding
                    embedding_response = client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=analysis.consolidated_memory
                    )
                    embedding = embedding_response.data[0].embedding
                    
                    # Use conversation_id from first memory
                    db.add_memory(mem1.get('conversation_id', 1), analysis.consolidated_memory, embedding)
                    print(f"Consolidated into: {analysis.consolidated_memory[:50]}...")
                    break  # Both memories handled, skip remaining comparisons
                    
            except Exception as e:
                print(f"Error comparing memories: {e}")
                continue
    
    print("Memory consolidation complete")
