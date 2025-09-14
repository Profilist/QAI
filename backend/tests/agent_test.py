import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from ..agents.runner import run_agents


def main() -> None:
    load_dotenv(find_dotenv())

    specs = [
        {
            "name": "navigation",
            "suite_id": 1,
            "container_name": os.getenv("CUA_CONTAINER_NAME"),
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
            "name": "events",
            "suite_id": 2,
            "container_name": os.getenv("CUA_CONTAINER_NAME2"),
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

    pr_name = os.getenv("PR_NAME", "local-dev")
    pr_link = os.getenv("PR_LINK", "http://localhost")
    summary = asyncio.run(run_agents(specs, pr_name, pr_link))
    print(summary)


if __name__ == "__main__":
    main()
