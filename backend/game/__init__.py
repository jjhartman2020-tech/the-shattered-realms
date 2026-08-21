"""Core game-state and simulation systems for The Shattered Realms."""

from .dice import roll
from .state import GameState
from .world import WorldSimulator
from .loot_runtime import install_loot_runtime

# Install persistent inventory pickup/loot handling as soon as the game package loads.
install_loot_runtime()

__all__ = ["GameState", "WorldSimulator", "roll"]
