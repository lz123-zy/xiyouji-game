"""NPC抠图 v5：基于直方图的手动阈值色度键。

npc1: 69%像素离白距离 < 30 → 背景，40%像素 > 160 → 角色
明确分界在 dist ~ 30 附近。用 dist <= 20 → 透明，dist >= 100 → 不透明，平滑过渡。
"""
import os
import numpy as np
import pygame

SRC_DIRS = {"npc1": "NPC形象/npc1", "npc2": "NPC形象/npc2"}
DST_DIRS = {"npc1": "resource/img/npc1_processed", "npc2": "resource/img/npc2_processed"}

TARGET_HEIGHT = 99

# 每个NPC的色度键参数（离纯白(255,255,255)的欧氏距离）
KEY_PARAMS = {
    "npc1": {"full_trans": 18, "full_opaque": 95},
    "npc2": {"full_trans": 45, "full_opaque": 100},
}
# alpha < 此值的像素强制设为全透明，消除白色边框残留
# npc2 绿色角色与白色背景的抗锯齿边缘更难分离，需要更高阈值
CLIP_ALPHA = {"npc1": 35, "npc2": 75}

COLOR_GRADE = {
    "npc1": {
        "red_scale": 0.78, "green_scale": 1.08, "blue_scale": 0.82,
        "brightness": 0.92, "contrast": 1.04, "saturation": 0.88,
    },
    "npc2": {
        "red_scale": 0.72, "green_scale": 1.10, "blue_scale": 0.78,
        "brightness": 0.88, "contrast": 1.05, "saturation": 0.85,
    },
}


def chroma_key_surface(surface, full_trans, full_opaque, bg_ref=(255, 255, 255)):
    """将像素按离参考白色的距离映射为透明度。"""
    w, h = surface.get_width(), surface.get_height()
    alpha = pygame.surfarray.pixels_alpha(surface)
    rgb = pygame.surfarray.pixels3d(surface)

    bg = np.array(bg_ref, dtype=np.float64)

    for y in range(h):
        for x in range(w):
            r, g, b = rgb[x, y].astype(np.float64)
            d = np.sqrt((r - bg[0])**2 + (g - bg[1])**2 + (b - bg[2])**2)

            if d <= full_trans:
                alpha[x, y] = 0
            elif d >= full_opaque:
                alpha[x, y] = 255
            else:
                t = (d - full_trans) / (full_opaque - full_trans)
                alpha[x, y] = int(t * 255)

    return surface


def clip_edge_pixels(surface, clip_alpha, bg_ref=(255, 255, 255)):
    """缩放后裁剪边缘半透明像素，并压暗残留的浅色边缘。"""
    w, h = surface.get_width(), surface.get_height()
    alpha = pygame.surfarray.pixels_alpha(surface)
    rgb = pygame.surfarray.pixels3d(surface)

    # 裁剪低 alpha 像素为全透明
    alpha[alpha < clip_alpha] = 0

    # 移除接近白色且半透明的像素（背景残留边框）
    bg = np.array(bg_ref, dtype=np.float64)
    white_dist = np.sqrt(((rgb.astype(np.float64) - bg) ** 2).sum(axis=2))
    ghost_mask = (white_dist < 45) & (alpha > 0) & (alpha < 150)
    alpha[ghost_mask] = 0

    # 压暗半透明边缘像素：消除白色背景残留的浅色光晕
    # alpha 越低（越接近透明/背景），压暗越重
    edge_mask = (alpha > 0) & (alpha < 200)
    if edge_mask.any():
        a = alpha[edge_mask].astype(np.float64)
        factor = (a / 255.0) ** 2.5  # 强压暗，使边缘接近深色
        for c in range(3):
            rgb[:, :, c][edge_mask] = (rgb[:, :, c][edge_mask] * factor).astype(np.uint8)

    return surface


def apply_color_grading(surface, grade):
    w, h = surface.get_width(), surface.get_height()
    rgb = pygame.surfarray.pixels3d(surface)
    alpha = pygame.surfarray.pixels_alpha(surface)
    for y in range(h):
        for x in range(w):
            if alpha[x, y] < 10:
                continue
            r, g, b = rgb[x, y].astype(np.float64)
            r = min(255, r * grade["red_scale"])
            g = min(255, g * grade["green_scale"])
            b = min(255, b * grade["blue_scale"])
            avg = (r + g + b) / 3
            r = avg + (r - avg) * grade["saturation"]
            g = avg + (g - avg) * grade["saturation"]
            b = avg + (b - avg) * grade["saturation"]
            r = (r - 128) * grade["contrast"] + 128 * grade["brightness"]
            g = (g - 128) * grade["contrast"] + 128 * grade["brightness"]
            b = (b - 128) * grade["contrast"] + 128 * grade["brightness"]
            rgb[x, y] = np.clip([r, g, b], 0, 255).astype(np.uint8)
    return surface


def scale_to_target(surface, target_h):
    w, h = surface.get_width(), surface.get_height()
    scale = target_h / h
    new_w = max(1, int(w * scale))
    return pygame.transform.smoothscale(surface, (new_w, target_h))


def process_npc(name):
    src = SRC_DIRS[name]
    dst = DST_DIRS[name]
    os.makedirs(dst, exist_ok=True)
    files = sorted([f for f in os.listdir(src) if f.endswith('.tga')])
    if not files:
        return
    grade = COLOR_GRADE[name]
    params = KEY_PARAMS[name]
    print(f"  {name}: full_trans={params['full_trans']}, full_opaque={params['full_opaque']}")
    for i, f in enumerate(files):
        img = pygame.image.load(os.path.join(src, f)).convert_alpha()
        img = chroma_key_surface(img, **params)
        img = apply_color_grading(img, grade)
        img = scale_to_target(img, TARGET_HEIGHT)
        img = clip_edge_pixels(img, CLIP_ALPHA[name])
        if i == 0:
            w, h = img.get_width(), img.get_height()
            a = pygame.surfarray.pixels_alpha(img)
            t = int(np.sum(a < 10))
            o = int(np.sum(a > 240))
            print(f"    frame 0: {w}x{h}, trans={t}({100*t/(w*h):.0f}%), opaque={o}({100*o/(w*h):.0f}%)")
        out_name = os.path.splitext(f)[0] + ".png"
        pygame.image.save(img, os.path.join(dst, out_name))
    print(f"  -> {len(files)} frames")


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    print("NPC 抠图 v5：手动阈值色度键（基于直方图）")
    for name in ["npc1", "npc2"]:
        process_npc(name)
    pygame.quit()


if __name__ == "__main__":
    main()
