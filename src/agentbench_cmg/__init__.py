"""Backward-compatible alias for agent_config_bench. """

from agent_config_bench import __version__
from agent_config_bench.analyze import main

__all__ = ["__version__", "main"]
