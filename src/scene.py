"""场景管理器：加载并切换三个游戏场景（村庄、郊外、观音院），管理 NPC 和怪物列表。"""
from pathlib import Path

import pygame

from .monster import Monster
from .npc import NPC
from .settings import MONSTER_LAYERS, NPC_LAYERS
from .tmx_map import TmxMap


class Scene:
    def __init__(self, name, map_path, default_spawn, npc_layers=(), monster_layers=()):
        self.name = name
        self.map_path = map_path
        self._load_map(map_path)
        self.player_spawn = self.map.get_object_position(
            "actor",
            "sun",
            default_spawn,
        )
        self.pixel_size = self.map.pixel_size
        self.npcs = self._load_npcs(npc_layers)
        self.monsters = self._load_monsters(monster_layers)
        self.boss = None
        self.boss_spawned = False
        self.boss_spawn = self._compute_boss_spawn()

    def _load_map(self, map_path):
        path = Path(map_path)
        if path.suffix.lower() == ".tmx":
            self.map = TmxMap(map_path)
            # 使用 TMX 内建的障碍物层
            self.obstacle_rects = self.map.obstacle_rects
        else:
            # 静态图片背景：创建 ImageBackdrop 替代 TMX
            self.map = ImageBackdrop(map_path)
            self.obstacle_rects = []

    def set_obstacle_rects(self, rects):
        """允许外部手动设置碰撞区域（用于图片背景场景）。"""
        self.obstacle_rects = list(rects)

    @classmethod
    def village(cls, map_path, default_spawn):
        return cls("village", map_path, default_spawn, NPC_LAYERS)

    @classmethod
    def outskirts(cls, map_path, default_spawn):
        return cls("outskirts", map_path, default_spawn, NPC_LAYERS)

    @classmethod
    def temple(cls, map_path, default_spawn):
        return cls("temple", map_path, default_spawn, monster_layers=MONSTER_LAYERS)

    def _load_npcs(self, npc_layers):
        npcs = []
        for obj in self.map.get_objects(npc_layers):
            npcs.append(
                NPC(
                    obj["layer"],
                    obj["name"],
                    (obj["x"], obj["y"]),
                )
            )
        return npcs

    def _load_monsters(self, monster_layers):
        monsters = []
        for obj in self.map.get_objects(monster_layers):
            monsters.append(
                Monster(
                    obj["name"],
                    obj["x"],
                    obj["y"],
                    obj["width"],
                    obj["height"],
                )
            )
        return monsters

    def _compute_boss_spawn(self):
        # 复用第一只小怪的合法落点作为 Boss 出生点，保证可走、可见、贴近战场。
        if self.monsters:
            first = self.monsters[0].hitbox
            return (first.x, first.y, first.width, first.height)
        return None

    def spawn_boss(self, boss):
        self.monsters.append(boss)
        self.boss = boss
        self.boss_spawned = True

    @property
    def active_monsters(self):
        return [monster for monster in self.monsters if monster.is_active]

    def update_monsters(self, dt, player_hitbox=None):
        for monster in self.active_monsters:
            monster.update_exploration(
                dt,
                player_hitbox,
                self.obstacle_rects,
                self.pixel_size,
            )

    def update_npcs(self, dt):
        for npc in self.npcs:
            npc.update(dt)

    def draw_map(self, surface, camera):
        self.map.draw(surface, camera)


class ImageBackdrop:
    """把单张图片包装成和 TmxMap 一样的 draw 接口，兼容现有 Scene 结构。"""

    def __init__(self, image_path):
        try:
            image = pygame.image.load(str(image_path)).convert_alpha()
        except Exception:
            # .jpg 没有 alpha 通道，回退到 convert()
            image = pygame.image.load(str(image_path)).convert()
        self.pixel_size = (image.get_width(), image.get_height())
        self.obstacle_rects = []
        self._image = image

    def get_object_position(self, _layer_name, _object_name, default):
        return default

    def get_objects(self, _layer_names):
        return []

    def draw(self, target_surface, camera):
        target_surface.blit(self._image, camera.apply_pos((0, 0)))
