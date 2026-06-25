"""回合制战斗系统：战斗面板绘制、双方血条、攻击动画、怪物自动反击、胜负判定。"""
import pygame

from .settings import (
    BATTLE_EFFECT_FRAME_LIMIT,
    BATTLE_EFFECT_FRAME_TIME,
    BATTLE_HIT_FLASH_TIME,
    BATTLE_VICTORY_SECONDS,
    MAGIC_APPEAR_DIR,
    MONSTER_FIRST_ATTACK_DELAY,
    PLAYER_ATTACK_DAMAGE,
    PLAYER_MAX_HEALTH,
    SWK_DIR,
)


class Battle:
    def __init__(self, monster, font_path, window_size):
        self.monster = monster
        self.player_health = PLAYER_MAX_HEALTH
        self.victory = False
        self.finished = False
        self.player_defeated = False
        self.victory_timer = BATTLE_VICTORY_SECONDS
        self.monster_attack_timer = MONSTER_FIRST_ATTACK_DELAY
        self.hit_flash_timer = 0.0
        self.window_width, self.window_height = window_size
        self.font_error = None
        self.effect_error = None
        self.effect_frames = self._load_effect_frames()
        self.effect_index = 0
        self.effect_time = 0.0
        self.effect_active = False
        self.attack_animation_error = None
        self.attack_frames = self._load_attack_frames()
        self.attack_active = False
        self.title_font = self._load_font(font_path, 36)
        self.text_font = self._load_font(font_path, 24)
        self.monster.set_state("fight")

    def _load_font(self, font_path, size):
        try:
            return pygame.font.Font(str(font_path), size)
        except Exception as exc:
            self.font_error = str(exc)
            return pygame.font.Font(None, size)

    def _load_effect_frames(self):
        frames = []
        try:
            paths = sorted(MAGIC_APPEAR_DIR.glob("*.tga"))[:BATTLE_EFFECT_FRAME_LIMIT]
            for path in paths:
                image = pygame.image.load(path).convert_alpha()
                width = max(1, round(image.get_width() * 0.45))
                height = max(1, round(image.get_height() * 0.45))
                frames.append(pygame.transform.smoothscale(image, (width, height)))
        except Exception as exc:
            self.effect_error = str(exc)
        return frames

    def _load_attack_frames(self):
        """加载探索风格的孙悟空下行帧作为战斗形象。"""
        BATTLE_SCALE = 0.85
        frames = []
        try:
            for name in ["00000.tga", "00001.tga", "00002.tga", "00003.tga"]:
                image = pygame.image.load(SWK_DIR / name).convert_alpha()
                w = max(1, round(image.get_width() * BATTLE_SCALE))
                h = max(1, round(image.get_height() * BATTLE_SCALE))
                frames.append(pygame.transform.smoothscale(image, (w, h)))
        except Exception as exc:
            self.attack_animation_error = str(exc)
            placeholder = pygame.Surface((60, 90), pygame.SRCALPHA)
            placeholder.fill((220, 70, 70))
            frames = [placeholder]
        self._attack_frame_index = 0
        self._attack_frame_timer = 0.0
        return frames

    def attack(self):
        if self.victory or self.finished or self.player_defeated:
            return None

        if self.attack_active and self._attack_frame_timer <= 0 and self._attack_frame_index >= len(self.attack_frames):
            return None

        self._start_attack_animation()
        self._start_effect()
        self.monster.take_damage(PLAYER_ATTACK_DAMAGE)
        if self.monster.defeated:
            self.victory = True
            self.victory_timer = BATTLE_VICTORY_SECONDS
            return "victory"

        return "hit"

    def update(self, dt):
        self.monster.update(dt)
        self._update_attack_animation(dt)
        self._update_effect(dt)
        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

        if self.victory:
            self.victory_timer -= dt
            if self.victory_timer <= 0 and self.monster.removed:
                self.finished = True
            return

        if self.finished or self.player_defeated:
            return

        self._update_monster_attack(dt)

    def _update_monster_attack(self, dt):
        self.monster_attack_timer -= dt
        if self.monster_attack_timer > 0:
            return

        self.monster_attack_timer = self.monster.attack_cooldown
        self.player_health = max(0, self.player_health - self.monster.attack_damage)
        self.hit_flash_timer = BATTLE_HIT_FLASH_TIME
        swing = self.monster.animations.get(self.monster.state)
        if swing:
            swing.reset()
        if self.player_health <= 0:
            self.player_defeated = True

    def _start_effect(self):
        if not self.effect_frames:
            return

        self.effect_active = True
        self.effect_index = 0
        self.effect_time = 0.0

    def _update_effect(self, dt):
        if not self.effect_active or not self.effect_frames:
            return

        self.effect_time += dt
        if self.effect_time >= BATTLE_EFFECT_FRAME_TIME:
            self.effect_time = 0.0
            self.effect_index += 1
            if self.effect_index >= len(self.effect_frames):
                self.effect_active = False
                self.effect_index = 0

    def _start_attack_animation(self):
        self.attack_active = True
        self._attack_frame_index = 0
        self._attack_frame_timer = 0.0

    def _update_attack_animation(self, dt):
        if not self.attack_active:
            return
        self._attack_frame_timer -= dt
        if self._attack_frame_timer > 0:
            return
        self._attack_frame_index += 1
        self._attack_frame_timer = 0.1
        if self._attack_frame_index >= len(self.attack_frames):
            self.attack_active = False
            self._attack_frame_index = 0

    def draw(self, surface):
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(60, 72, self.window_width - 120, 340)

        # 双层边框：外层半透明深色 + 内层金色
        outer = panel.inflate(8, 8)
        pygame.draw.rect(surface, (0, 0, 0, 120), outer, border_radius=10)
        pygame.draw.rect(surface, (30, 30, 42), panel, border_radius=8)
        pygame.draw.rect(surface, (210, 180, 120), panel, 2, border_radius=8)

        # 标题
        if self.victory:
            title = "战斗胜利"
            title_color = (120, 255, 120)
        elif self.player_defeated:
            title = "战斗失败"
            title_color = (255, 100, 100)
        else:
            title = f"遭遇{self.monster.title}"
            title_color = (255, 232, 150)
        self._blit_text(surface, self.title_font, title, panel.left + 28, panel.top + 20, title_color)

        # 分割线
        sep_y = panel.top + 62
        pygame.draw.line(surface, (80, 75, 60), (panel.left + 20, sep_y), (panel.right - 20, sep_y), 1)

        # 血条区域
        bar_x = panel.left + 28
        bar_w = panel.width - 56
        self._draw_health_bar(surface, "玩家血量", self.player_health, PLAYER_MAX_HEALTH, bar_x, panel.top + 72, bar_w)
        self._draw_health_bar(
            surface,
            "怪物血量",
            self.monster.health,
            self.monster.max_health,
            bar_x,
            panel.top + 132,
            bar_w,
        )

        # 怪物名字标签
        name_surf = self.text_font.render(self.monster.title, True, (220, 180, 140))
        name_rect = name_surf.get_rect(centerx=panel.right - 112, top=panel.top + 196)
        surface.blit(name_surf, name_rect)

        # 角色
        self._draw_player(surface, panel)
        self._draw_monster(surface, panel)

        # 底部提示文字
        if self.victory:
            hint = "战斗胜利，正在返回寺庙。"
        elif getattr(self.monster, "enraged", False):
            hint = f"{self.monster.title}暴怒，攻势凶猛！按 J 拼命反击！"
        elif self.hit_flash_timer > 0:
            hint = "妖怪反击,损失血量!按 J 反击,按 Esc 撤退。"
        else:
            hint = "按 J 攻击妖怪，按 Esc 撤退。当心妖怪反击！"
        self._blit_text(surface, self.text_font, hint, panel.left + 28, panel.bottom - 38, (245, 245, 245))

    def _draw_health_bar(self, surface, label, value, maximum, x, y, width):
        ratio = max(0, value) / maximum if maximum else 0

        # 动态颜色：绿 → 黄 → 红
        if ratio >= 0.6:
            bar_color = (60, 190, 80)
        elif ratio >= 0.3:
            bar_color = (220, 190, 50)
        else:
            bar_color = (200, 55, 55)

        self._blit_text(surface, self.text_font, f"{label}: {value}/{maximum}", x, y, (245, 245, 245))

        # 血条背景（圆角）
        bar_rect = pygame.Rect(x, y + 30, width, 22)
        pygame.draw.rect(surface, (50, 50, 58), bar_rect, border_radius=6)

        # 填充
        fill_w = round(bar_rect.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
            pygame.draw.rect(surface, bar_color, fill_rect, border_radius=6)

        # 内阴影（顶部高光）
        highlight = pygame.Surface((bar_rect.width, 4), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 30), (0, 0, bar_rect.width, 4), border_radius=4)
        surface.blit(highlight, bar_rect.topleft)

        # 边框
        pygame.draw.rect(surface, (180, 180, 180), bar_rect, 1, border_radius=6)

        # 百分比文字
        pct = f"{round(ratio * 100)}%"
        pct_surf = self.text_font.render(pct, True, (220, 220, 220))
        surface.blit(pct_surf, (bar_rect.right + 10, bar_rect.y + 2))

    def _draw_monster(self, surface, panel):
        monster_rect = self.monster.image.get_rect(midbottom=(panel.right - 112, panel.bottom - 28))
        # 放大怪物形象
        img = self.monster.image
        new_w = max(1, round(img.get_width() * 1.3))
        new_h = max(1, round(img.get_height() * 1.3))
        scaled = pygame.transform.smoothscale(img, (new_w, new_h))
        monster_rect = scaled.get_rect(midbottom=(panel.right - 112, panel.bottom - 28))
        surface.blit(scaled, monster_rect)

        if self.effect_active and self.effect_frames:
            effect = self.effect_frames[self.effect_index]
            effect_rect = effect.get_rect(center=monster_rect.center)
            surface.blit(effect, effect_rect)

    def _draw_player(self, surface, panel):
        player_anchor = (panel.left + 112, panel.bottom - 28)
        if self.attack_active:
            image = self.attack_frames[self._attack_frame_index]
        else:
            image = self.attack_frames[0]
        # 放大玩家形象
        new_w = max(1, round(image.get_width() * 1.3))
        new_h = max(1, round(image.get_height() * 1.3))
        scaled = pygame.transform.smoothscale(image, (new_w, new_h))
        player_rect = scaled.get_rect(midbottom=player_anchor)
        surface.blit(scaled, player_rect)

        if self.hit_flash_timer > 0:
            flash = pygame.Surface(player_rect.size, pygame.SRCALPHA)
            alpha = int(150 * (self.hit_flash_timer / BATTLE_HIT_FLASH_TIME))
            flash.fill((220, 40, 40, alpha))
            surface.blit(flash, player_rect)

    def _blit_text(self, surface, font, text, x, y, color):
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))
