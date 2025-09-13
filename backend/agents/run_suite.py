#!/usr/bin/env python3
"""
Bridge script to run agent suites from Node.js CICD pipeline
This script is called by qai-pipeline.js to execute individual test suites
"""
import sys
import asyncio
import os
from pathlib import Path

# Add the agents directory to the Python path
sys.path.append(str(Path(__file__).parent))

from runner import run_qai_tests

async def main():
    if len(sys.argv) != 2:
        print("Usage: python run_suite.py <suite_id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        suite_id = int(sys.argv[1])
        print(f"🚀 Starting agent execution for suite {suite_id}")
        
        # Run the agent with the database-backed suite
        result = await run_qai_tests(suite_id=suite_id)
        
        print(f"✅ Agent execution completed for suite {suite_id}")
        print(f"📊 Agent status: {result['agent_result']['status']}")
        
        # Exit with appropriate code
        if result['agent_result']['status'] == 'success':
            sys.exit(0)
        else:
            print(f"❌ Agent failed: {result['agent_result'].get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
            
    except ValueError:
        print(f"Error: Invalid suite_id '{sys.argv[1]}'. Must be an integer.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Agent execution failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())