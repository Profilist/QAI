import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from ..agents.runner import run_agents


def main() -> None:
    load_dotenv(find_dotenv())

    specs = [
        {
            "persona": "navigation",
            "container_name": os.getenv("CUA_CONTAINER_NAME"),
            "suite": "navigation",
            "tests": [
                {
                    "name": "admissions-header",
                    "instructions": [
                        {
                            "role": "user",
                            "content": (
                                "Go to https://uwaterloo.ca. "
                                "Click the header link labeled \"Admissions\". "
                                "Confirm that the page you land on is related to Admissions."
                            ),
                        }
                    ],
                },
                {
                    "name": "about-header",
                    "instructions": [
                        {
                            "role": "user",
                            "content": (
                                "On https://uwaterloo.ca, click the header link labeled \"About Waterloo\". "
                                "Confirm you navigated to an About page."
                            ),
                        }
                    ],
                },
            ],
        },
        {
            "persona": "events",
            "container_name": os.getenv("CUA_CONTAINER_NAME2") or os.getenv("CUA_CONTAINER_NAME"),
            "suite": "events",
            "tests": [
                {
                    "name": "first-event",
                    "instructions": [
                        {
                            "role": "user",
                            "content": (
                                "Go to https://uwaterloo.ca. Scroll down to the Events section. "
                                "Click the first event shown and confirm you navigated to the event details."
                            ),
                        }
                    ],
                }
            ],
        },
    ]

    summary = asyncio.run(run_agents(specs))
    print(summary)


if __name__ == "__main__":
    main()
