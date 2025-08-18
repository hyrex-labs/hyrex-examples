"""
FastAPI backend for deep research system.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import uuid
from pathlib import Path
from datetime import datetime

from tasks import research_question, get_research_status, store_research_result, hy

app = FastAPI(title="Deep Research System")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ResearchRequest(BaseModel):
    question: str
    depth: Optional[str] = "standard"  # quick, standard, deep

class ResearchResponse(BaseModel):
    task_id: str
    status: str
    message: str

class ResearchStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface."""
    html_file = Path("static/index.html")
    if html_file.exists():
        return FileResponse(html_file)
    else:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>Deep Research System</h1>
                <p>HTML interface not found. Please create static/index.html</p>
            </body>
        </html>
        """)


# Store active tasks (in production, use a database)
active_tasks = {}

@app.post("/api/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """
    Start a new research task.
    """
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")
    
    # Validate depth parameter
    if request.depth not in ["quick", "standard", "deep"]:
        request.depth = "standard"
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Send research task to Hyrex
    try:
        # Launch the workflow
        task = research_question.send(request.question, request.depth)
        
        # Store the task for later status checking
        active_tasks[task_id] = {
            "task": task,
            "question": request.question,
            "depth": request.depth,
            "started_at": datetime.now()
        }
        
        return ResearchResponse(
            task_id=task_id,
            status="processing",
            message=f"Research started for: {request.question}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start research: {str(e)}")


@app.get("/api/research/{task_id}", response_model=ResearchStatus)
async def get_research_status_endpoint(task_id: str):
    """
    Check the status of a research task.
    """
    # Check if we have this task
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = active_tasks[task_id]
    hyrex_task = task_info["task"]
    
    try:
        # Check if task is complete
        hyrex_task.refresh()
        
        # Get the latest task run to check status
        if hyrex_task.task_runs:
            latest_run = hyrex_task.task_runs[-1]
            
            if latest_run.status == "SUCCESS":
                # Get the result
                result = hyrex_task.get_result()
                
                # Clean up from active tasks
                del active_tasks[task_id]
                
                return ResearchStatus(
                    task_id=task_id,
                    status="completed",
                    result=result
                )
            elif latest_run.status == "FAILED":
                # Task failed
                del active_tasks[task_id]
                
                return ResearchStatus(
                    task_id=task_id,
                    status="failed",
                    result=None
                )
            else:
                # Still processing
                return ResearchStatus(
                    task_id=task_id,
                    status="processing",
                    result=None
                )
        else:
            # No task runs yet, still queued
            return ResearchStatus(
                task_id=task_id,
                status="processing",
                result=None
            )
            
    except Exception as e:
        print(f"Error checking task status: {e}")
        return ResearchStatus(
            task_id=task_id,
            status="processing",
            result=None
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "deep-research"}


# For testing - run a sample research
@app.post("/api/test")
async def test_research():
    """
    Run a test research query.
    """
    test_question = "What are the latest developments in renewable energy?"
    
    try:
        # Run the research workflow using Hyrex
        task = research_question.send(test_question, "quick")
        task.wait(timeout=60)  # Wait up to 60 seconds
        result = task.get_result()
        
        return {
            "status": "success",
            "question": test_question,
            "result": result
        }
    except Exception as e:
        import traceback
        error_detail = f"Test failed: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Create static directory if it doesn't exist
    Path("static").mkdir(exist_ok=True)
    
    print("🚀 Starting Deep Research API server...")
    print("📍 API: http://localhost:8000")
    print("📍 Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)