import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents.runner import run_agents


def main() -> None:
    load_dotenv(find_dotenv())

    specs = [
        {
            "persona": "agent",
            "container_name": os.getenv("CUA_CONTAINER_NAME"),
            "instructions": [
                {"role": "user", "content": "Open the browser, go to https://google.com, describe the page."}
            ],
        },
        {
            "persona": "agent2",
            "container_name": os.getenv("CUA_CONTAINER_NAME2"),
            "instructions": [
                {"role": "user", "content": "Open https://www.github.com, describe the page."}
            ],
        },
    ]

    summary = asyncio.run(run_agents(specs))
    print(summary)


if __name__ == "__main__":
    main()
