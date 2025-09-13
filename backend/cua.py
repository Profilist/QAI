from computer import Computer
import os
import asyncio
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

async def main():
    print("Starting CUA")
    
    async with Computer(
        os_type="linux",
        provider_type="cloud",
        name=os.getenv("CUA_CONTAINER_NAME"),
        api_key=os.getenv("CUA_API_KEY")
    ) as computer:
        # Take screenshot
        screenshot = await computer.interface.screenshot()
        # Click and type
        await computer.interface.left_click(100, 100)

if __name__ == "__main__":
    asyncio.run(main())