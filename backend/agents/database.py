from typing import Dict, Any, Optional
from supabase import create_client
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def _has_client() -> bool:
	return supabase is not None


async def create_result(pr_name: str, pr_link: str, overall_result: Dict[str, Any], run_status: str) -> Optional[int]:
	"""Insert a new row into results and return its id."""
	try:
		if not _has_client():
			print("[db] Skipping create_result: SUPABASE not configured")
			return None
		payload = {
			"pr_name": pr_name,
			"pr_link": pr_link,
			"overall_result": overall_result,
			"run_status": run_status,
		}
		resp = supabase.table('results').insert(payload).execute()
		row = (resp.data or [{}])[0]
		print(f"[db] Created result id={row.get('id')} status={run_status}")
		return row.get('id')
	except Exception as e:
		print(f"[db] ❌ create_result error: {str(e)}")
		return None


async def set_suite_result_id(suite_id: int, result_id: int) -> None:
	"""Link a suite to a result by setting suites.result_id."""
	try:
		if not _has_client():
			print(f"[db] Skipping set_suite_result_id for suite {suite_id}: no client")
			return
		supabase.table('suites').update({"result_id": result_id}).eq('id', suite_id).execute()
		print(f"[db] Linked suite {suite_id} -> result {result_id}")
	except Exception as e:
		print(f"[db] ❌ set_suite_result_id error: {str(e)}")


async def get_or_create_test(suite_id: int, name: str) -> Optional[int]:
	"""Find a test row by (suite_id, name) or create it. Returns test id."""
	try:
		if not _has_client():
			print(f"[db] Skipping get_or_create_test for suite {suite_id}, name '{name}': no client")
			return None
		# Try find existing
		resp = supabase.table('tests').select('id').eq('suite_id', suite_id).eq('name', name).limit(1).execute()
		if resp.data:
			return resp.data[0]['id']
		# Create new
		payload = {
			"suite_id": suite_id,
			"name": name,
			"steps": [],
			"run_status": "RUNNING",
		}
		ins = supabase.table('tests').insert(payload).execute()
		row = (ins.data or [{}])[0]
		print(f"[db] Created test id={row.get('id')} for suite {suite_id}, name '{name}'")
		return row.get('id')
	except Exception as e:
		print(f"[db] ❌ get_or_create_test error: {str(e)}")
		return None


async def append_test_step(test_id: int, step: Any) -> None:
	"""Append a single step to tests.steps immediately (read-modify-write)."""
	try:
		if not _has_client():
			return
		res = supabase.table('tests').select('steps').eq('id', test_id).limit(1).execute()
		steps = []
		if res.data:
			curr = res.data[0].get('steps')
			if isinstance(curr, list):
				steps = curr
		steps.append(step)
		supabase.table('tests').update({"steps": steps}).eq('id', test_id).execute()
	except Exception as e:
		print(f"[db] ❌ append_test_step error: {str(e)}")


async def update_test_fields(test_id: int, fields: Dict[str, Any]) -> None:
	"""Generic update of tests row."""
	try:
		if not _has_client():
			return
		supabase.table('tests').update(fields).eq('id', test_id).execute()
	except Exception as e:
		print(f"[db] ❌ update_test_fields error: {str(e)}")


async def get_result_id_for_suite(suite_id: int) -> Optional[int]:
	"""Return result_id for a given suite_id from suites table."""
	try:
		if not _has_client():
			return None
		resp = supabase.table('suites').select('result_id').eq('id', suite_id).limit(1).execute()
		if resp.data:
			return resp.data[0].get('result_id')
		return None
	except Exception as e:
		print(f"[db] ❌ get_result_id_for_suite error: {str(e)}")
		return None
