"""Core game-state and simulation systems for The Shattered Realms."""

from .dice import roll
from .state import GameState
from .world import WorldSimulator

__all__ = ["GameState", "WorldSimulator", "roll"]
