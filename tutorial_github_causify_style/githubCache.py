"""
Import as:

import tutorial_github_causify_style.githubCache as tgcastgi
"""

import datetime
import hashlib
import json
import logging
import os
from typing import Any

_LOG = logging.getLogger(__name__)


# #############################################################################
# GitHubCache
# #############################################################################


class GitHubCache:
    """
    Custom cache that excludes the client object from cache keys.
    """

    def __init__(self, cache_dir: str = "."):
        self.cache_dir = cache_dir

    def get(self, func_name: str, args: tuple) -> Any:
        """
        Get a value from cache.

        :param func_name: name of the function
        :param args: function arguments
        :return: cached value or None if not found
        """
        cache_path = self._get_cache_path(func_name)
        # Check if cache file exists.
        if not os.path.exists(cache_path):
            return None
        # Load cache file.
        with open(cache_path, "r") as f:
            cache_data = json.load(f)
        # Generate key and look up value.
        key = self._make_key(func_name, args)
        return cache_data.get(key)

    def set(self, func_name: str, args: tuple, value: Any) -> None:
        """
        Set a value in cache.

        :param func_name: name of the function
        :param args: function arguments
        :param value: value to cache
        """
        cache_path = self._get_cache_path(func_name)
        # Load existing cache or create new.
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
        else:
            cache_data = {}
        # Add new entry.
        key = self._make_key(func_name, args)
        cache_data[key] = value
        # Write back to file.
        with open(cache_path, "w") as f:
            json.dump(cache_data, f, indent=2)

    def _make_key(
        self, func_name: str, args: tuple, skip_first: bool = True
    ) -> str:
        """
        Create a cache key from function name and arguments.

        :param func_name: name of the function
        :param args: function arguments
        :param skip_first: Skip first argument (client) when building
            key
        :return: cache key string
        """
        # Skip the client argument when building the key.
        cache_args = args[1:] if skip_first else args
        # Convert arguments to a string representation.
        key_parts = [func_name]
        for arg in cache_args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif isinstance(arg, datetime.datetime):
                key_parts.append(arg.isoformat())
            elif isinstance(arg, tuple):
                # Handle period tuples.
                key_parts.append(f"{arg[0].isoformat()}_{arg[1].isoformat()}")
            else:
                # Hash complex objects.
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        # Create a hash of the key for consistent length.
        full_key = "_".join(key_parts)
        res = hashlib.md5(full_key.encode()).hexdigest()
        return res

    def _get_cache_path(self, func_name: str) -> str:
        """
        Get the cache file path for a function.

        :param func_name: name of the function
        :return: path to the cache file
        """
        path = os.path.join(self.cache_dir, f"cache.{func_name}.json")
        return path
