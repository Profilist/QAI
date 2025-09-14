from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from runner import run_agents, run_qai_tests, run_suites_for_result
from database import (
    _has_client
)

load_dotenv()

app = FastAPI(
    title="QAI Agent Runner API", 
    version="1.0.0",
    description="FastAPI server for QAI autonomous testing agents"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models matching API.md specification

class CreateResultRequest(BaseModel):
    prLink: str
    prName: str

class UpdateResultRequest(BaseModel):
    resSuccess: bool

class CreateSuiteRequest(BaseModel):
    resultId: int
    name: str
    s3Link: Optional[str] = None
    suitesSuccess: Optional[bool] = False

class UpdateSuiteRequest(BaseModel):
    suitesSuccess: Optional[bool] = None
    s3Link: Optional[str] = None

class CreateTestRequest(BaseModel):
    suiteId: int
    name: str
    summary: Optional[str] = None
    testSuccess: Optional[bool] = False

class UpdateTestRequest(BaseModel):
    testSuccess: Optional[bool] = None
    summary: Optional[str] = None

class RunSuiteRequest(BaseModel):
    suite_id: int

class AgentRunRequest(BaseModel):
    spec: Dict[str, Any]

class MultiAgentRunRequest(BaseModel):
    test_specs: List[Dict[str, Any]]
    pr_name: str
    pr_link: str

class RunResultRequest(BaseModel):
    result_id: int

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_connected = _has_client()
    print(f"[API] Health check requested - Database connected: {db_connected}")
    
    response = {
        "status": "healthy",
        "database_connected": db_connected,
        "version": "1.0.0"
    }
    print(f"[API] Health check response: {response}")
    return response

# Agent execution endpoints

@app.post("/run-suite")
async def run_suite_endpoint(request: RunSuiteRequest):
    """
    Run a test suite by ID - This is the main endpoint called by the CICD pipeline
    """
    suite_id = request.suite_id
    print(f"[API] Starting suite execution for suite_id: {suite_id}")
    print(f"[API] Request received at: {__import__('datetime').datetime.now().isoformat()}")
    
    try:
        print(f"[API] Calling run_qai_tests for suite_id: {suite_id}")
        result = await run_qai_tests(suite_id)
        print(f"[API] run_qai_tests completed for suite_id: {suite_id}")
        print(f"[API] Result status: {result.get('agent_result', {}).get('status', 'unknown')}")
        
        if result['agent_result']['status'] == 'success':
            print(f"[API] Suite {suite_id} executed successfully")
            print(f"[API] Tests run: {result['agent_result'].get('tests_run', 0)}")
            
            response = {
                "status": "success",
                "message": f"Suite {suite_id} executed successfully",
                "data": result
            }
            print(f"[API] Returning success response for suite_id: {suite_id}")
            return response
        else:
            error_msg = result['agent_result'].get('error', 'Unknown error')
            print(f"[API] Suite execution failed for suite_id: {suite_id}")
            print(f"[API] Error: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Suite execution failed: {error_msg}"
            )
    except HTTPException as he:
        print(f"[API] HTTPException raised for suite_id: {suite_id}")
        print(f"[API] HTTPException detail: {he.detail}")
        print(f"[API] HTTPException status_code: {he.status_code}")
        raise
    except Exception as e:
        print(f"[API] Unexpected error for suite_id: {suite_id}")
        print(f"[API] Exception type: {type(e).__name__}")
        print(f"[API] Exception message: {str(e)}")
        print(f"[API] Exception details: {e}")
        raise HTTPException(status_code=500, detail=f"Suite execution failed: {str(e)}")
    finally:
        print(f"[API] Request completed for suite_id: {suite_id}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QAI Agent Runner API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "run_suite": "/run-suite",
            "run_result": "/run-result",
            "run_agents": "/run-agents"
        }
    }


@app.post("/run-result")
async def run_result_endpoint(request: RunResultRequest):
    """Run all suites and tests for a given result_id."""
    result_id = request.result_id
    print(f"[API] Starting result execution for result_id: {result_id}")
    try:
        summary = await run_suites_for_result(result_id)
        status = summary.get("run_status")
        if status == "PASSED" or status == "FAILED":
            return {
                "status": "success",
                "message": f"Result {result_id} executed",
                "data": summary,
            }
        return {
            "status": "success",
            "message": f"Result {result_id} executed",
            "data": summary,
        }
    except Exception as e:
        print(f"[API] run_result failed: {e}")
        raise HTTPException(status_code=500, detail=f"Result execution failed: {str(e)}")


@app.post("/run-agents")
async def run_agents_endpoint(request: MultiAgentRunRequest):
    """Run multiple agent suites provided directly as test_specs along with PR metadata."""
    try:
        summary = await run_agents(request.test_specs, request.pr_name, request.pr_link)
        return {
            "status": "success",
            "message": "Agents executed",
            "data": summary,
        }
    except Exception as e:
        print(f"[API] run_agents failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agents execution failed: {str(e)}")

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"[API] Starting QAI Agent Runner API on port {port}")
    print(f"[API] Database connection status: {_has_client()}")
    print(f"[API] Environment loaded from .env: {os.getenv('CUA_API_KEY', 'Not set')[:10]}...")
    uvicorn.run(app, host="0.0.0.0", port=port)