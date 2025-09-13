from agent import ComputerAgent
import asyncio

agent = ComputerAgent(
    model="anthropic/claude-3-5-sonnet-20241022",
    tools=[computer],
    max_trajectory_budget=5.0
)

messages = [{"role": "user", "content": "Take a screenshot and tell me what you see"}]
async def run_agent():
    async for result in agent.run(messages):
        for item in result["output"]:
                if item["type"] == "message":
                    print(item["content"][0]["text"])

asyncio.run(run_agent())