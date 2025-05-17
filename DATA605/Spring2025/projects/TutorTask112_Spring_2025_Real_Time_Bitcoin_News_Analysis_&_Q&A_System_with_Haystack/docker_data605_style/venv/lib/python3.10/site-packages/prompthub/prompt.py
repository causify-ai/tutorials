from typing import Dict, List
from dataclasses import dataclass, asdict
import json
import os

import yaml
import requests


MAIN_ENDPOINT = os.getenv("PROMPTHUB_MAIN_ENDPOINT", "https://api.prompthub.deepset.ai")


@dataclass
class Prompt:
    """
    Prompt stores all the information of a single prompt.
    """

    name: str
    tags: List[str]
    meta: Dict[str, str]
    version: str
    text: str
    description: str

    def to_yaml(self, file: str):
        with open(file, "w") as f:
            yaml.safe_dump(asdict(self), f)

    def to_json(self, file: str):
        with open(file, "w") as f:
            json.dump(asdict(self), f)


def from_json(file: str):
    with open(file) as f:
        data = json.load(f)
        return Prompt(
            data["name"],
            data["tags"],
            data["meta"],
            data["version"],
            data["text"],
            data["description"],
        )


def from_yaml(file: str):
    with open(file) as f:
        data = yaml.safe_load(f)
        return Prompt(
            data["name"],
            data["tags"],
            data["meta"],
            data["version"],
            data["text"],
            data["description"],
        )


def fetch(name: str, timeout: float = 30.0):
    """
    Fetches the specified prompt from PromptHUB and
    returns a Prompt instance of it.

    :param name: Name of the prompt to fetch from PromptHUB
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up.
    :return: An instance of Prompt storing all its info
    """
    url = f"{MAIN_ENDPOINT}/prompts/{name}"
    res = requests.get(url, timeout=timeout)
    res.raise_for_status()
    j = res.json()
    return Prompt(
        j["name"],
        j["tags"],
        j["meta"],
        j["version"],
        j["text"],
        j["description"],
    )
