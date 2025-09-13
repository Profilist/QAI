from typing import Dict, Any
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

async def save_agent_results_to_db(agent_result: Dict[str, Any], suite_id: int):
	"""Save suite-level result to database per simplified schema"""
	try:
		print(f"[{agent_result['persona_slug']}] Saving suite results to database for suite {suite_id}")

		# Update suite with status and result JSON
		suite_update = {
			"suite_status": agent_result.get("suite_status"),
			"suite_result": agent_result.get("suite_result"),
		}
		response = supabase.table('suites').update(suite_update).eq('id', suite_id).execute()
		if response.data:
			print(f"[{agent_result['persona_slug']}] ✅ Updated suite {suite_id}")
		else:
			print(f"[{agent_result['persona_slug']}] ❌ Failed to update suite {suite_id}")

		# Update tests table: set test_result per name match
		tests = agent_result.get("tests", [])
		tests_db = supabase.table('tests').select('id,name').eq('suite_id', suite_id).execute()
		name_to_id = {}
		if tests_db.data:
			for row in tests_db.data:
				name_to_id[str(row.get('name'))] = row.get('id')
		for t in tests:
			row_id = name_to_id.get(str(t.get('name')))
			if not row_id:
				continue
			upd = {
				"test_result": t.get("status") == "passed",
				"steps": t.get("steps"),
				"recording_file_url": t.get("recording_file_url"),
			}
			supabase.table('tests').update(upd).eq('id', row_id).execute()
			print(f"[{agent_result['persona_slug']}] Updated test {row_id} ({t.get('name')})")

	except Exception as e:
		print(f"[{agent_result.get('persona_slug','agent')}] ❌ Database save error: {str(e)}")