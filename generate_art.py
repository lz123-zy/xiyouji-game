"""生成与西游记观音院游戏风格一致的图片素材，保存到桌面。"""

import math
import random
from pathlib import Path

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

OUTPUT_DIR = Path.home() / "Desktop" / "xyl_game_art"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 800, 600

# ── 调色盘 ──
# 暗夜系
NIGHT_TOP = (8, 11, 40)
NIGHT_BOT = (22, 28, 40)
MOON = (255, 248, 200)
MOON_DARK = (14, 16, 42)
STAR = (255, 245, 200)
MOUNTAIN_FAR = (16, 19, 30)
MOUNTAIN_NEAR = (20, 24, 38)

# 国风古寺
TEMPLE_ROOF = (95, 38, 28)
TEMPLE_WALL = (180, 150, 120)
TEMPLE_WALL_DARK = (140, 115, 90)
TEMPLE_PILLAR = (145, 60, 40)
TEMPLE_EAVE = (190, 160, 50)
TEMPLE_TILE = (60, 24, 16)

# 自然色
CLOUD = (210, 195, 160, 160)
CLOUD_LIGHT = (235, 225, 200, 120)
TREE_TRUNK = (65, 40, 25)
TREE_LEAF = (28, 55, 30)
TREE_LEAF_LIGHT = (42, 72, 38)
GRASS = (25, 50, 22)
PATH = (130, 115, 85)
FIRE_RED = (220, 55, 30)

# 金色 / 文字
GOLD = (255, 232, 150)
GOLD_DIM = (200, 175, 100)
WHITE_SOFT = (235, 230, 215)
RED_ACCENT = (190, 50, 35)


def _create_surface(w=W, h=H):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _fill_night_gradient(surf):
    """夜空从上到下渐变。"""
    for row in range(H):
        t = row / max(1, H - 1)
        r = int(NIGHT_TOP[0] + t * (NIGHT_BOT[0] - NIGHT_TOP[0]))
        g = int(NIGHT_TOP[1] + t * (NIGHT_BOT[1] - NIGHT_TOP[1]))
        b = int(NIGHT_TOP[2] + t * (NIGHT_BOT[2] - NIGHT_TOP[2]))
        pygame.draw.line(surf, (r, g, b), (0, row), (W, row))


def _draw_stars(surf, count=100):
    rng = random.Random(42)
    for _ in range(count):
        x = rng.randint(10, W - 10)
        y = rng.randint(5, H // 2 - 20)
        size = rng.randint(1, 3)
        alpha = rng.randint(80, 240)
        color = (255, 248, 210, alpha)
        star = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(star, color, (size + 1, size + 1), size)
        surf.blit(star, (x - size, y - size))


def _draw_moon(surf, cx, cy, r=40):
    moon_surf = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
    pygame.draw.circle(moon_surf, (*MOON, 230), (r * 3 // 2, r * 3 // 2), r)
    pygame.draw.circle(moon_surf, (*MOON_DARK, 210), (r * 3 // 2 + r // 3, r * 3 // 2 - r // 4), int(r * 0.72))
    surf.blit(moon_surf, (cx - r * 3 // 2, cy - r * 3 // 2))


def _draw_mountains(surf, base_y, layers, color_a, color_b):
    """画锯齿状山峦。"""
    for i, (h_max, h_min) in enumerate(layers):
        t = i / max(1, len(layers) - 1)
        r = int(color_a[0] + t * (color_b[0] - color_a[0]))
        g = int(color_a[1] + t * (color_b[1] - color_a[1]))
        b = int(color_a[2] + t * (color_b[2] - color_a[2]))
        color = (r, g, b)

        points = [(0, H)]
        step = 60 + i * 20
        x = 0
        while x < W + step:
            h = base_y - h_max - random.Random(x + i * 1000).randint(-h_min // 2, h_min // 2)
            points.append((x, h))
            x += step
        points.append((W, H))

        if len(points) >= 3:
            pygame.draw.polygon(surf, color, points)


def _draw_cloud(surf, cx, cy, w, h, alpha=160):
    cloud = pygame.Surface((w, h), pygame.SRCALPHA)
    for px in range(w):
        for py in range(h):
            dx = (px - w / 2) / (w / 2)
            dy = (py - h / 2) / (h / 2)
            dist = dx * dx * 0.6 + dy * dy
            if dist < 0.95:
                a = int(alpha * max(0, (1 - dist)))
                cloud.set_at((px, py), (220, 210, 185, a))
    surf.blit(cloud, (cx - w // 2, cy - h // 2))


def _draw_horizontal_gradient_line(surf, y, width_px, color_start, color_end):
    for ox in range(width_px):
        t = ox / max(1, width_px - 1)
        r = int(color_start[0] + t * (color_end[0] - color_start[0]))
        g = int(color_start[1] + t * (color_end[1] - color_start[1]))
        b = int(color_start[2] + t * (color_end[2] - color_start[2]))
        px_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
        px_surf.fill((r, g, b, 200))
        surf.blit(px_surf, ((W - width_px) // 2 + ox, y))


def _draw_text(surf, text, y, font_size, color, bold=False):
    font = pygame.font.Font(None, font_size)
    font.bold = bold
    text_surf = font.render(text, True, color)
    x = (W - text_surf.get_width()) // 2
    surf.blit(text_surf, (x, y))


def _draw_boxed_text(surf, text, y, font_size, color, border_color, bg_alpha=80):
    font = pygame.font.Font(None, font_size)
    text_surf = font.render(text, True, color)
    tw, th = text_surf.get_size()
    box = pygame.Surface((tw + 30, th + 14), pygame.SRCALPHA)
    box.fill((0, 0, 0, bg_alpha))
    pygame.draw.rect(box, border_color, box.get_rect(), 1)
    surf.blit(box, ((W - tw - 30) // 2, y - 7))
    surf.blit(text_surf, ((W - tw) // 2, y))


def _draw_frame(surf, rect, color, width=2):
    pygame.draw.rect(surf, color, rect, width)


def _save(surf, filename):
    path = OUTPUT_DIR / filename
    pygame.image.save(surf, str(path))
    print(f"  [OK] {filename}")


# ══════════════════════════════════════════════════════════
# 1. 启动画面大背景  start_bg.png
# ══════════════════════════════════════════════════════════
def make_start_bg():
    surf = _create_surface()
    _fill_night_gradient(surf)
    _draw_stars(surf, 90)
    _draw_moon(surf, W - 130, 95, 42)

    # 三层远山
    _draw_mountains(surf, H, [(140, 30), (180, 40), (240, 50)], (16, 19, 30), (14, 16, 22))

    # 祥云
    for cx, cy, cw, ch in [(180, 310, 160, 50), (550, 350, 140, 45), (400, 380, 180, 55)]:
        _draw_cloud(surf, cx, cy, cw, ch, 120)

    # 金色标题装饰线
    _draw_horizontal_gradient_line(surf, 190, 260, (0, 0, 0, 0), GOLD)
    _draw_horizontal_gradient_line(surf, 192, 260, GOLD, (0, 0, 0, 0))

    _draw_text(surf, "西游記觀音院", 110, 60, GOLD)
    _draw_text(surf, "—— 祸起观音院 ——", 180, 32, GOLD_DIM)

    # 底部装饰
    _draw_horizontal_gradient_line(surf, H - 100, 300, (80, 40, 20), (40, 20, 10))
    _save(surf, "start_bg.png")


# ══════════════════════════════════════════════════════════
# 2. 观音院场景  temple_scene.png
# ══════════════════════════════════════════════════════════
def make_temple_scene():
    surf = _create_surface()
    # 天空
    for row in range(H):
        t = row / max(1, H - 1)
        r = int(15 + t * 10)
        g = int(12 + t * 15)
        b = int(28 + t * 35)
        pygame.draw.line(surf, (r, g, b), (0, row), (W, row))

    _draw_stars(surf, 40)
    _draw_moon(surf, W - 100, 70, 35)

    # 远山
    _draw_mountains(surf, H, [(120, 40), (200, 50)], (18, 22, 34), (22, 26, 40))

    # 松树
    rng = random.Random(7)
    for tx in [60, 120, 190, 640, 710, 760]:
        h = rng.randint(140, 220)
        y_top = H - h
        # 树干
        trunk_w = rng.randint(10, 18)
        trunk_rect = pygame.Rect(tx - trunk_w // 2, y_top + h // 2, trunk_w, h // 2)
        pygame.draw.rect(surf, TREE_TRUNK, trunk_rect)
        # 树冠 — 三角形层叠
        for level in range(3):
            cy = y_top + level * 35
            ch = 50 + level * 15
            cw = 70 + level * 25
            color = TREE_LEAF_LIGHT if level < 2 else TREE_LEAF
            tri_points = [(tx, cy - ch // 2), (tx - cw // 2, cy + ch // 2), (tx + cw // 2, cy + ch // 2)]
            pygame.draw.polygon(surf, color, tri_points)

    # 寺庙主体
    temple_cx = W // 2
    temple_base_y = 520

    # 台基
    base_rect = pygame.Rect(temple_cx - 140, temple_base_y - 20, 280, 40)
    pygame.draw.rect(surf, (130, 120, 105), base_rect)
    pygame.draw.rect(surf, (100, 90, 78), base_rect, 2)

    # 墙面
    wall_rect = pygame.Rect(temple_cx - 110, temple_base_y - 160, 220, 140)
    pygame.draw.rect(surf, TEMPLE_WALL, wall_rect)
    pygame.draw.rect(surf, TEMPLE_WALL_DARK, wall_rect, 3)

    # 柱子
    for px in [temple_cx - 90, temple_cx + 90]:
        pillar_rect = pygame.Rect(px - 8, temple_base_y - 155, 16, 140)
        pygame.draw.rect(surf, TEMPLE_PILLAR, pillar_rect)

    # 大门
    door_rect = pygame.Rect(temple_cx - 35, temple_base_y - 115, 70, 95)
    pygame.draw.rect(surf, (60, 30, 18), door_rect)
    pygame.draw.rect(surf, TEMPLE_EAVE, door_rect, 3)

    # 门钉
    for dx in [-16, 16]:
        for dy in [-36, -10, -58]:
            pygame.draw.circle(surf, TEMPLE_EAVE, (temple_cx + dx, temple_base_y + dy), 5)

    # 窗户
    for side, sx in [(-1, -70), (1, 70)]:
        win_rect = pygame.Rect(temple_cx + sx - 20, temple_base_y - 90, 40, 50)
        pygame.draw.rect(surf, (22, 15, 10), win_rect)
        pygame.draw.rect(surf, TEMPLE_EAVE, win_rect, 2)
        pygame.draw.line(surf, TEMPLE_EAVE, win_rect.midtop, win_rect.midbottom, 1)
        pygame.draw.line(surf, TEMPLE_EAVE, win_rect.midleft, win_rect.midright, 1)

    # 屋顶 — 弧形飞檐
    roof_top_y = temple_base_y - 200
    roof_points = [
        (temple_cx - 160, temple_base_y - 160),
        (temple_cx - 170, roof_top_y + 20),
        (temple_cx - 100, roof_top_y - 5),
        (temple_cx, roof_top_y),
        (temple_cx + 100, roof_top_y - 5),
        (temple_cx + 170, roof_top_y + 20),
        (temple_cx + 160, temple_base_y - 160),
    ]
    pygame.draw.polygon(surf, TEMPLE_ROOF, roof_points)
    pygame.draw.polygon(surf, TEMPLE_TILE, roof_points, 3)

    # 牌匾
    plaque_rect = pygame.Rect(temple_cx - 55, roof_top_y + 35, 110, 32)
    pygame.draw.rect(surf, (40, 18, 8), plaque_rect)
    pygame.draw.rect(surf, TEMPLE_EAVE, plaque_rect, 2)
    _draw_text(surf, "观音院", roof_top_y + 36, 24, GOLD)

    # 地面
    ground_rect = pygame.Rect(0, temple_base_y + 20, W, H - temple_base_y - 20)
    pygame.draw.rect(surf, (30, 35, 25), ground_rect)

    # 石板路
    path_points = [(temple_cx - 60, temple_base_y + 20), (temple_cx - 80, H),
                   (temple_cx + 50, H), (temple_cx + 40, temple_base_y + 20)]
    pygame.draw.polygon(surf, PATH, path_points)

    # 灯笼
    for lx in [temple_cx - 120, temple_cx + 120]:
        lantern_surf = pygame.Surface((14, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(lantern_surf, (220, 55, 30, 220), (0, 0, 14, 22))
        pygame.draw.rect(lantern_surf, (160, 40, 20), (5, 0, 4, 5))
        surf.blit(lantern_surf, (lx, roof_top_y + 70))

    _save(surf, "temple_scene.png")


# ══════════════════════════════════════════════════════════
# 3. 村庄场景  village_scene.png
# ══════════════════════════════════════════════════════════
def make_village_scene():
    surf = _create_surface()
    # 黄昏 / 清晨天空
    for row in range(H):
        t = row / max(1, H - 1)
        r = int(30 + t * 20)
        g = int(25 + t * 30)
        b = int(40 + t * 20)
        pygame.draw.line(surf, (r, g, b), (0, row), (W, row))

    # 太阳
    sun_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(sun_surf, (255, 210, 120, 150), (40, 40), 32)
    surf.blit(sun_surf, (W - 140, 30))

    # 远山（绿色调）
    _draw_mountains(surf, H, [(100, 30), (150, 50)], (22, 32, 22), (18, 26, 18))

    rng = random.Random(99)

    # 草屋
    def draw_hut(cx, base_y, scale=1.0):
        s = scale
        # 墙
        w, h = int(80 * s), int(70 * s)
        wall = pygame.Rect(cx - w // 2, base_y - h, w, h)
        pygame.draw.rect(surf, (195, 175, 145), wall)
        pygame.draw.rect(surf, (160, 140, 110), wall, 2)
        # 门
        door = pygame.Rect(cx - int(14 * s), base_y - int(48 * s), int(28 * s), int(48 * s))
        pygame.draw.rect(surf, (80, 50, 30), door)
        # 草屋顶
        roof_w, roof_h = int(110 * s), int(45 * s)
        roof_top = base_y - h - roof_h // 3
        tri = [(cx - roof_w // 2, base_y - h + roof_h // 3),
               (cx + roof_w // 2, base_y - h + roof_h // 3),
               (cx, roof_top)]
        pygame.draw.polygon(surf, (110, 85, 40), tri)
        pygame.draw.polygon(surf, (85, 65, 28), tri, 2)

    hut_positions = [(160, 420, 1.0), (330, 440, 0.85), (530, 430, 1.1), (670, 450, 0.9)]
    for cx, by, sc in hut_positions:
        draw_hut(cx, by, sc)

    # 大树
    tree_x, tree_y = 420, 340
    pygame.draw.rect(surf, TREE_TRUNK, (tree_x - 12, tree_y - 20, 24, 80))
    for tier in range(3):
        tc_y = tree_y - 30 - tier * 28
        tw, th = 100 - tier * 15, 65 - tier * 10
        color = TREE_LEAF_LIGHT if tier == 0 else TREE_LEAF
        pygame.draw.ellipse(surf, color, (tree_x - tw // 2, tc_y - th // 2, tw, th))

    # 地面
    pygame.draw.rect(surf, GRASS, (0, 490, W, H - 490))

    # 土路
    path_pts = [(400, H), (380, 480), (W // 2, 460), (620, 400), (450, H)]
    pygame.draw.polygon(surf, PATH, path_pts)

    # 篱笆
    for fx in range(50, W - 50, 35):
        fy_base = 485 + rng.randint(-10, 10)
        pygame.draw.rect(surf, (140, 105, 55), (fx, fy_base - 35, 24, 35))
        pygame.draw.line(surf, (160, 125, 70), (fx, fy_base - 30), (fx + 24, fy_base - 30), 2)

    _save(surf, "village_scene.png")


# ══════════════════════════════════════════════════════════
# 4. 战斗场景底图  battle_bg.png
# ══════════════════════════════════════════════════════════
def make_battle_bg():
    surf = _create_surface()
    # 暗红天空
    for row in range(H):
        t = row / max(1, H - 1)
        r = int(35 + t * 8)
        g = int(10 + t * 18)
        b = int(12 + t * 20)
        pygame.draw.line(surf, (r, g, b), (0, row), (W, row))

    # 血色月
    moon_surf = pygame.Surface((90, 90), pygame.SRCALPHA)
    pygame.draw.circle(moon_surf, (230, 80, 50, 200), (45, 45), 32)
    surf.blit(moon_surf, (W // 2 - 45, 40))

    # 怪石嶙峋
    rock_color = (48, 42, 48)
    rock_color_dark = (35, 30, 35)
    rng = random.Random(13)
    for rx in [40, 100, 200, 440, 580, 700]:
        rh = rng.randint(120, 200)
        rw = rng.randint(40, 80)
        ry = H - rh
        rock_pts = [(rx, ry + rh), (rx + rw // 2, ry + rh),
                    (rx + rw, ry + rng.randint(20, 50)),
                    (rx + rw + rng.randint(-15, 10), ry),
                    (rx - rng.randint(0, 15), ry + rng.randint(30, 60))]
        pygame.draw.polygon(surf, rock_color, rock_pts)
        pygame.draw.polygon(surf, rock_color_dark, rock_pts, 2)

    # 地面
    pygame.draw.rect(surf, (42, 34, 40), (0, H - 90, W, 90))
    # 碎石
    for _ in range(30):
        sx, sy = rng.randint(10, W - 10), rng.randint(H - 80, H - 5)
        sr = rng.randint(3, 9)
        pygame.draw.ellipse(surf, (60, 50, 55), (sx, sy, sr, sr // 2))

    # 火星粒子
    for _ in range(60):
        fx = rng.randint(20, W - 20)
        fy = rng.randint(H // 2, H - 60)
        fire_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
        a = rng.randint(60, 200)
        fire_surf.fill((255, 140 + rng.randint(0, 100), 20, a))
        surf.blit(fire_surf, (fx, fy))

    _save(surf, "battle_bg.png")


# ══════════════════════════════════════════════════════════
# 5. 胜利 / 完成画面  win_bg.png
# ══════════════════════════════════════════════════════════
def make_win_bg():
    surf = _create_surface()
    # 金色天空
    for row in range(H):
        t = row / max(1, H - 1)
        r = int(20 + t * 40)
        g = int(18 + t * 35)
        b = int(30 + t * 50)
        pygame.draw.line(surf, (r, g, b), (0, row), (W, row))

    # 金色光晕
    glow = pygame.Surface((300, 140), pygame.SRCALPHA)
    for gx in range(300):
        for gy in range(140):
            dx = abs(gx - 150) / 150
            dy = abs(gy - 70) / 70
            d = dx * 0.4 + dy * 0.6
            if d < 1:
                a = int(180 * (1 - d))
                glow.set_at((gx, gy), (255, 230, 140, a))
    surf.blit(glow, (W // 2 - 150, 80))

    # 祥云
    for cx, cy, cw, ch in [(150, 360, 200, 60), (W // 2, 400, 220, 70), (W - 160, 340, 180, 55), (300, 440, 190, 60)]:
        _draw_cloud(surf, cx, cy, cw, ch, 150)

    # 装饰金线
    _draw_horizontal_gradient_line(surf, 120, 350, (0, 0, 0, 0), GOLD)
    _draw_horizontal_gradient_line(surf, 123, 350, GOLD, (0, 0, 0, 0))

    _draw_text(surf, "功德圆满", 160, 56, GOLD)
    _draw_text(surf, "观音院重归安宁", 230, 30, GOLD_DIM)

    _draw_horizontal_gradient_line(surf, H - 120, 280, GOLD_DIM, (0, 0, 0, 0))

    _save(surf, "win_bg.png")


# ══════════════════════════════════════════════════════════
# 6. 失败画面  fail_bg.png
# ══════════════════════════════════════════════════════════
def make_fail_bg():
    surf = _create_surface()
    # 暗紫天空
    for row in range(H):
        t = row / max(1, H - 1)
        r = int(22 + t * 5)
        g = int(8 + t * 12)
        b = int(18 + t * 22)
        pygame.draw.line(surf, (r, g, b), (0, row), (W, row))

    # 暗云
    for cx, cy, cw, ch in [(100, 200, 250, 70), (W - 130, 250, 220, 60), (300, 350, 280, 80)]:
        _draw_cloud(surf, cx, cy, cw, ch, 90)

    # 断剑标记（中央暗红色）
    mark_surf = pygame.Surface((80, 120), pygame.SRCALPHA)
    pygame.draw.line(mark_surf, RED_ACCENT + (180,), (40, 10), (40, 90), 4)
    pygame.draw.line(mark_surf, RED_ACCENT + (200,), (20, 15), (60, 30), 4)
    surf.blit(mark_surf, (W // 2 - 40, 140))

    _draw_text(surf, "挑战失败", 290, 48, (200, 50, 40))
    _draw_text(surf, "修行尚未圆满，还请重整旗鼓", 355, 26, (185, 160, 145))

    _save(surf, "fail_bg.png")


# ══════════════════════════════════════════════════════════
# 7. 郊外过渡场景  outskirts_scene.png
# ══════════════════════════════════════════════════════════
def make_outskirts_scene():
    surf = _create_surface()
    # 天空
    for row in range(H):
        t = row / max(1, H - 1)
        r = int(18 + t * 15)
        g = int(15 + t * 28)
        b = int(30 + t * 35)
        pygame.draw.line(surf, (r, g, b), (0, row), (W, row))

    _draw_stars(surf, 50)
    _draw_moon(surf, W - 140, 80, 35)

    # 远山
    _draw_mountains(surf, H, [(100, 30), (180, 50), (260, 40)], (16, 20, 30), (13, 17, 26))

    rng = random.Random(42)

    # 密林
    for tx in range(0, W + 20, 30):
        th = rng.randint(90, 200)
        ty = H - th
        tw = rng.randint(12, 22)
        pygame.draw.rect(surf, TREE_TRUNK, (tx - tw // 2, ty + th // 2, tw, th // 2))
        for level in range(2):
            cl_y = ty + level * 25
            cl_w = 35 + level * rng.randint(5, 15)
            cl_h = 40 + level * 10
            pygame.draw.ellipse(surf, TREE_LEAF if level else TREE_LEAF_LIGHT,
                                (tx - cl_w // 2, cl_y - cl_h // 2, cl_w, cl_h))

    # 蜿蜒小路
    path_pts = [(0, H - 30), (100, H - 50), (220, H - 20), (350, H - 60),
                (500, H - 40), (650, H - 70), (W, H - 50), (W, H), (0, H)]
    pygame.draw.polygon(surf, PATH, path_pts)

    # 远方观音院轮廓（小）
    temple_far_x, temple_far_y = W - 130, H - 220
    far_roof = [(temple_far_x - 30, temple_far_y + 10), (temple_far_x - 35, temple_far_y - 10),
                (temple_far_x, temple_far_y - 15), (temple_far_x + 35, temple_far_y - 10),
                (temple_far_x + 30, temple_far_y + 10)]
    pygame.draw.polygon(surf, (60, 25, 18), far_roof)
    wall_far = pygame.Rect(temple_far_x - 15, temple_far_y + 10, 30, 25)
    pygame.draw.rect(surf, (130, 105, 80), wall_far)

    _save(surf, "outskirts_scene.png")


# ══════════════════════════════════════════════════════════
# 8. 对话框底图  dialog_bg.png
# ══════════════════════════════════════════════════════════
def make_dialog_bg():
    w, h = 752, 160
    surf = _create_surface(w, h)
    # 深色羊皮纸感
    for row in range(h):
        t = row / max(1, h - 1)
        r = int(28 + t * 15)
        g = int(24 + t * 14)
        b = int(32 + t * 20)
        pygame.draw.line(surf, (r, g, b), (0, row), (w, row))
    # 金边框
    pygame.draw.rect(surf, (210, 180, 120), surf.get_rect(), 3)
    # 内边框
    inner = pygame.Rect(8, 8, w - 16, h - 16)
    pygame.draw.rect(surf, (150, 120, 70, 80), inner, 1)
    # 四角装饰
    for cx, cy in [(12, 12), (w - 12, 12), (12, h - 12), (w - 12, h - 12)]:
        pygame.draw.circle(surf, (210, 180, 120), (cx, cy), 5, 1)
    _save(surf, "dialog_bg.png")


# ══════════════════════════════════════════════════════════
# 9. Boss 横幅用底  boss_banner.png
# ══════════════════════════════════════════════════════════
def make_boss_banner():
    w, h = 800, 70
    surf = _create_surface(w, h)
    for row in range(h):
        a = 180 - int(row / h * 30)
        col = (90, 0, 0, max(0, a))
        line_surf = pygame.Surface((1, 1), pygame.SRCALPHA)
        line_surf.fill(col)
        surf.blit(line_surf, (0, row))
        # 梯度延伸
        for x in range(1, w):
            surf.set_at((x, row), col)
    # 上下边线
    pygame.draw.line(surf, (235, 90, 80, 220), (0, 0), (w, 0), 3)
    pygame.draw.line(surf, (235, 90, 80, 220), (0, h - 1), (w, h - 1), 3)
    _save(surf, "boss_banner.png")


# ══════════════════════════════════════════════════════════
# 10. 按钮底图  button_normal.png
# ══════════════════════════════════════════════════════════
def make_button():
    w, h = 160, 44
    surf = _create_surface(w, h)
    pygame.draw.rect(surf, (28, 32, 38, 230), surf.get_rect(), border_radius=6)
    pygame.draw.rect(surf, (210, 175, 110, 200), surf.get_rect(), 2, border_radius=6)
    # 高光线
    pygame.draw.line(surf, (255, 235, 160, 80), (10, 6), (w - 10, 6), 1)
    _save(surf, "button_normal.png")


# ══════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("正在生成西游记观音院美术素材...\n")
    make_start_bg()
    make_temple_scene()
    make_village_scene()
    make_battle_bg()
    make_win_bg()
    make_fail_bg()
    make_outskirts_scene()
    make_dialog_bg()
    make_boss_banner()
    make_button()
    print(f"\n全部完成! 图片保存在: {OUTPUT_DIR}")
    pygame.quit()
