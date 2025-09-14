from computer import Computer
import os
from dotenv import load_dotenv, find_dotenv
from ..agents.record import start_recording, stop_recording
import asyncio

load_dotenv(find_dotenv())

os_type = "linux"
provider_type = "cloud"
container_name = os.getenv("CUA_CONTAINER_NAME")
api_key = os.getenv("CUA_API_KEY")

async def main():
    async with Computer(
        os_type=os_type,
        provider_type=provider_type,
        name=container_name,
        api_key=api_key
    ) as computer:
        await computer.venv_install("demo_venv", [])
        await computer.venv_exec("demo_venv", start_recording, output_dir="/tmp/replays", fps=5)
        
        await asyncio.sleep(5)
        
        await computer.venv_exec("demo_venv", stop_recording)

asyncio.run(main())