import json
import math
import os
import uuid
from pathlib import Path
from typing import List, Union, Dict

import aiohttp
import requests
import yaml

from oatlas.tools.nettacker.core.template import TemplateLoader


def read_from_file(filename: str) -> List[str]:
    """
    Returns a list from a file
    Args:
        filename: Name of the file
    Returns:
        List of each line in the file
    """
    with Path(filename).open() as file:
        return [line.strip() for line in file.readlines()]


def read_file(filename: str) -> str:
    """
    Returns a string form a file, a normal read operation
    Args:
        filename: Path to the file
    """
    with Path(filename).open() as file:
        return file.read()


def generate_random_token() -> str:
    """
    Generates a unique token using the UUID module
    Returns:
    A unique hex string
    """
    return uuid.uuid4().hex


def get_lines(s: str, line: int, context: int = 0) -> Dict[int, str]:
    """
    Extract lines with context from the given string.

    Return dict with lines range and the extracted lines.

    Note
    ----
    It is supposed that `line` parameter is 1-indexed.

    This is used in trufflehog
    """
    lines = s.splitlines()
    lower = max(0, line - context - 1)
    upper = min(len(lines), line + context)

    return {f"{i + 1}": lines[i] for i in range(lower, upper)}


def get_strings(s: str, alphabet: str, minlen: int) -> List[str]:
    """
    Extract substrings of given alphabet from the string.

    Examples
    --------
    Basic usage examples

    >>> get_strings("testing get_strings", "abcdefghijklmnopqrstuvwxyz", 5)
    ['testing', 'strings']
    >>> get_strings("something about deadbeef", "0123456789abcdef", 5)
    ['deadbeef']

    This is used in trufflehog
    """
    chars = ""
    count = 0

    sub = []
    for char in s:
        if char in alphabet:
            chars += char
            count += 1
        else:
            if count >= minlen:
                sub.append(chars)

            chars = ""
            count = 0

    if count > minlen:
        sub.append(chars)

    return sub


def shannon_entropy(s: str, alphabet: str) -> float:
    """
    Calculate Shannon entropy for given string of alphabet characters.

    Note
    ----
    Return zero for empty string.

    Examples
    --------
    Basic usage examples

    >>> shannon_entropy("", "abcdefghijklmnopqrstuvwxyz")
    0.0
    >>> shannon_entropy("abcd", "abcdefghijklmnopqrstuvwxyz")
    2.0
    >>> shannon_entropy("1234abcd", "0123456789abcdef")
    3.0

    This is used in trufflehog
    """
    entropy = 0.0
    if not s:
        return entropy

    for x in alphabet:
        px = float(s.count(x)) / len(s)
        if px > 0:
            entropy += -px * math.log(px, 2)

    return entropy


def nettacker_module_names() -> List[str]:
    """
    Generate (or load cached) list of all Nettacker module names.

    Behavior:
      - If a cache file exists (e.g. nettacker_module_configs.json -> nettacker_module_configs_names.json),
        load and return it (only if it is a list).
      - Otherwise scan the Nettacker modules directory, build the list of module names,
        write it to the cache file atomically, and return it.

    Returns:
        List[str]: A list of module names (titles from YAML info.name).

    So this ended up being more helpful. Keeping a cache added almost a 40% reduced start time! Beautiful
    """
    from oatlas.config import Config

    cache_path = Config.path.nettacker_cached_function_configs
    names_cache = cache_path.with_name(cache_path.stem + "_names.json")

    if names_cache.exists():
        try:
            with names_cache.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and all(isinstance(x, str) for x in data):
                    return data
        except Exception:
            pass

    output: List[str] = []
    for module_path in sorted(Config.path.nettacker_modules_dir.glob("**/*.yaml")):
        library = str(module_path).split("/")[-1].split(".")[0]
        category = str(module_path).split("/")[-2]
        module = f"{library}_{category}"

        try:
            contents = yaml.safe_load(TemplateLoader(module).open().split("payload:")[0])
            info = contents.get("info", {}) if isinstance(contents, dict) else {}
            module_name = info.get("name", "")
            if module_name:
                output.append(module_name)
        except Exception:
            continue

    try:
        tmp = names_cache.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        tmp.replace(names_cache)
    except Exception:
        pass

    return output


async def _fetch_single(session: aiohttp.ClientSession, url: str) -> Dict[str, Union[int, str]]:
    """
    Internal helper to fetch a single URL asynchronously.

    This is used by the GetPagesEngine for making GET requests to multiple websites in a bulk
    using aiohttp.
    """
    from atlas.config import Request

    headers = {"User-Agent": Request.user_agents.common_linux, "Accept": "application/json"}

    try:
        async with session.get(url, headers=headers) as resp:
            text = await resp.text()
            return {"status": resp.status, "text": text}
    except Exception as e:
        return {"status": -1, "text": str(e)}


def download_image_from_url(image_url: str, filename: str) -> bool:
    """
    As the name suggests -> Downloads an image to the
    `scraped` directory from the URL

    Args:
        image_url: URL for the image file
        filename: The name of the file to be saved as
    Returns:
        Boolean True/False depending on success
    """
    CWD = Path.cwd()
    download_dir = CWD / "oatlas/data/"
    # Just making sure it exists
    os.makedirs(download_dir, exist_ok=True)
    save_path = os.path.join(download_dir, filename)
    response = requests.get(image_url)

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    else:  # Something went wrong
        return False
