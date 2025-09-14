from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from dotenv import load_dotenv
load_dotenv()

try:
    from runner import run_single_agent, run_agents, run_qai_tests
    from database import (
        get_or_create_test,
        create_result,
        set_suite_result_id,
        get_suite_with_tests,
        update_test_fields,
        append_test_step,
        _has_client
    )
except ImportError as e:
    # Fallback for when running on Vercel with different import paths
    print(f"Import error: {e}")
    # Define stub functions to prevent startup errors
    async def run_qai_tests(suite_id): 
        return {"agent_result": {"status": "failed", "error": "Agent runner not available"}}
    async def run_single_agent(spec): 
        return []
    async def run_agents(specs, pr_name, pr_link): 
        return {}
    def _has_client(): 
        return False

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_connected": _has_client(),
        "version": "1.0.0",
        "environment": "vercel" if os.getenv("VERCEL") else "local"
    }

# Results endpoints (matching API.md)

@app.post("/results")
async def create_result_endpoint(request: CreateResultRequest):
    """Create a new result (PR test run)"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        result_id = await create_result(request.prName, request.prLink, {}, "PENDING")
        if result_id is None:
            raise HTTPException(status_code=500, detail="Failed to create result")
        
        return {
            "success": True,
            "message": "Result created successfully",
            "data": {
                "id": result_id,
                "pr-link": request.prLink,
                "pr-name": request.prName,
                "res-success": False
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create result: {str(e)}")

@app.patch("/results/{result_id}")
async def update_result_endpoint(result_id: int, request: UpdateResultRequest):
    """Update result success status"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        # Import here to handle Vercel deployment issues
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        response = supabase.table('results').update({
            'res-success': request.resSuccess
        }).eq('id', result_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return {
            "success": True,
            "message": "Result updated successfully",
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update result: {str(e)}")

@app.get("/results")
async def get_all_results():
    """Get all results"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        response = supabase.table('results').select('*').order('created_at', desc=True).execute()
        
        return {
            "success": True,
            "data": response.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")

# Suite endpoints

@app.post("/suites")
async def create_suite_endpoint(request: CreateSuiteRequest):
    """Create a new test suite"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        suite_data = {
            'result_id': request.resultId,
            'name': request.name,
            'suites-success': request.suitesSuccess
        }
        if request.s3Link:
            suite_data['s3-link'] = request.s3Link
        
        response = supabase.table('suites').insert([suite_data]).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create suite")
        
        return {
            "success": True,
            "message": "Suite created successfully",
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create suite: {str(e)}")

@app.patch("/suites/{suite_id}")
async def update_suite_endpoint(suite_id: int, request: UpdateSuiteRequest):
    """Update suite success status and/or S3 link"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        update_data = {}
        if request.suitesSuccess is not None:
            update_data['suites-success'] = request.suitesSuccess
        if request.s3Link is not None:
            update_data['s3-link'] = request.s3Link
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        response = supabase.table('suites').update(update_data).eq('id', suite_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Suite not found")
        
        return {
            "success": True,
            "message": "Suite updated successfully",
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update suite: {str(e)}")

@app.get("/results/{result_id}/suites")
async def get_suites_for_result(result_id: int):
    """Get suites for a specific result"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        response = supabase.table('suites').select('*').eq('result_id', result_id).order('created_at', desc=True).execute()
        
        return {
            "success": True,
            "data": response.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch suites: {str(e)}")

# Test endpoints

@app.post("/tests")
async def create_test_endpoint(request: CreateTestRequest):
    """Create a new individual test"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        test_data = {
            'suite_id': request.suiteId,
            'name': request.name,
            'summary': request.summary,
            'test-success': request.testSuccess
        }
        
        response = supabase.table('tests').insert([test_data]).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create test")
        
        return {
            "success": True,
            "message": "Test created successfully",
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create test: {str(e)}")

@app.patch("/tests/{test_id}")
async def update_test_endpoint(test_id: int, request: UpdateTestRequest):
    """Update test success status and/or summary"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        update_data = {}
        if request.testSuccess is not None:
            update_data['test-success'] = request.testSuccess
        if request.summary is not None:
            update_data['summary'] = request.summary
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        response = supabase.table('tests').update(update_data).eq('id', test_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Test not found")
        
        return {
            "success": True,
            "message": "Test updated successfully",
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update test: {str(e)}")

@app.get("/suites/{suite_id}/tests")
async def get_tests_for_suite(suite_id: int):
    """Get tests for a specific suite"""
    try:
        if not _has_client():
            raise HTTPException(status_code=500, detail="Database not configured")
        
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        response = supabase.table('tests').select('*').eq('suite_id', suite_id).order('created_at', desc=True).execute()
        
        return {
            "success": True,
            "data": response.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tests: {str(e)}")

# Agent execution endpoints

@app.post("/run-suite")
async def run_suite_endpoint(request: RunSuiteRequest):
    """
    Run a test suite by ID - This is the main endpoint called by the CICD pipeline
    """
    try:
        result = await run_qai_tests(request.suite_id)
        
        if result['agent_result']['status'] == 'success':
            return {
                "status": "success",
                "message": f"Suite {request.suite_id} executed successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Suite execution failed: {result['agent_result'].get('error', 'Unknown error')}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suite execution failed: {str(e)}")

@app.post("/run-agent")
async def run_agent_endpoint(request: AgentRunRequest):
    """Run a single agent test (legacy endpoint)"""
    try:
        result = await run_single_agent(request.spec)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.post("/run-agents")
async def run_agents_endpoint(request: MultiAgentRunRequest):
    """Run multiple agent tests (legacy endpoint)"""
    try:
        result = await run_agents(request.test_specs, request.pr_name, request.pr_link)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agents execution failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QAI Agent Runner API",
        "version": "1.0.0",
        "deployment": "vercel" if os.getenv("VERCEL") else "local",
        "endpoints": {
            "health": "/health",
            "results": "/results",
            "suites": "/suites", 
            "tests": "/tests",
            "run_suite": "/run-suite"
        }
    }

# Export the FastAPI app for Vercel
from mangum import Mangum
handler = Mangum(app)