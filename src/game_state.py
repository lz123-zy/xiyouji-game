"""游戏状态枚举：定义所有可能的游戏状态，供 game.py 状态机使用。"""
from enum import Enum, auto


class GameState(Enum):
    START = auto()
    HELP = auto()
    PAUSED = auto()
    VILLAGE_EXPLORING = auto()
    OUTSKIRTS_EXPLORING = auto()
    TEMPLE_EXPLORING = auto()
    BATTLE = auto()
    BATTLE_VICTORY = auto()
    NARRATIVE = auto()
    COMPLETE = auto()
    FAILED = auto()
