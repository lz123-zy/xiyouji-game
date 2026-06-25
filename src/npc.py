"""NPC 实体：支持动画帧或静态图片，每个 NPC 有固定台词，部分支持多句推进对话。"""
import pygame

from .animation import Animation
from .settings import (
    ELDER_DIR,
    GOD_DIR,
    NPC1_DIR,
    NPC2_DIR,
    NPC_IDLE_FRAME_LIMIT,
    NPC_IDLE_FRAME_TIME,
    NPC_INTERACTION_PADDING,
    NPC_SCALE,
)


class NPC:
    """支持动画帧或静态图片的 NPC 精灵。"""

    boss_defeated = False

    # 按图层的兜底对话（找不到具体角色台词时使用）。
    DIALOGS = {
        "god": ("土地公", "大圣，前方就是观音院，小心妖怪。"),
        "elder": ("老人", "村里最近不太安宁。"),
        "child": ("孩童", "我好像看到有妖怪往寺庙方向去了。"),
        "guard": ("村民", "......"),
        "apprentice": ("村民", "......"),
        "herbalist": ("村民", "......"),
        "merchant": ("村民", "......"),
    }

    # 按对象名的专属对话，让每个村民各有性格。
    OBJECT_DIALOGS = {
        # 老人们（原版）
        "elder1": ("张老汉", "听闻观音院的禅师都被妖怪掳走了，大圣可要救救他们啊。"),
        "elder2": ("王婆婆", "哎哟，这不是齐天大圣吗！老身年轻时也见过妖怪作乱，那回还是一位高僧把妖降住的。大圣若要去降妖，可得小心那黑熊精的蛮力，它力气大着呢！"),
        "elder3": ("张大爷", "大圣来了！俺这几天在村口守着，远远瞧见观音院那边黑气冲天，怕是那妖怪又在作祟。大圣若要去，俺给你备些干粮路上吃！"),
        "elder4": ("赵老伯", "大圣若要进观音院，记得先找土地公问个明白。"),
        "elder5": ("李婆婆", "大圣来啦！老身听说那观音院里的妖怪可厉害了，连院里的老禅师都被困住了。大圣您神通广大，一定要小心那妖怪的暗器呀！"),
        # 孩童们
        "boy1": ("小石头", "大圣大圣！你真会七十二变吗？变只猴子给俺瞧瞧嘛！"),
        "boy2": ("二娃", "俺哥说那妖怪有两只大角，可吓人了，你打得过它吗？"),
        "girl1": ("阿香", "我的花猫昨天跑去观音院就没回来，你能帮我找找它吗？"),
        "girl2": ("翠儿", "娘说天黑了不许出门，因为妖怪会抓小孩呢……"),
        "girl3": ("莲妹", "大圣加油！打跑了妖怪，我就给你摘最甜的桃子！"),
        # 郊外自定义 NPC
        "guard": ("小林", "我是这林子的守林人。前方妖怪横行，大圣若要去观音院，务必多加小心。"),
        "apprentice": ("小陆", "我跟着师父学采药，听说观音院的药园里有一味灵芝...可惜被妖怪占了。"),
        "herbalist": ("芸娘", "大圣若在林间受伤，可到我这儿来讨些草药。妖怪虽凶，这山里的药草也是灵得很。"),
        "merchant": ("沈老板", "唉，这妖怪一闹，我这生意也做不成了。大圣若能除掉那黑熊精，我请全村人喝酒！"),
    }

    POST_BOSS_DIALOGS = {
        "god": ("土地公", "大圣果然神通广大！那牛魔王已被降服，观音院的妖怪也被一网打尽，这片土地总算安宁了！"),
        "elder1": ("张老汉", "大圣回来啦！听闻妖怪已被打跑了，禅师们也都获救了，真是天大的好消息啊！"),
        "elder2": ("王婆婆", "哎哟，大圣凯旋啦！老身就知道大圣一定能降住那妖怪，果然是齐天大圣！"),
        "elder3": ("张大爷", "大圣威武！那黑气终于散了，俺们村又能看到星星月亮了！"),
        "elder4": ("赵老伯", "大圣降妖归来，老夫备了些薄酒，大圣若不嫌弃，坐下来喝一杯！"),
    }

    def __init__(self, layer_name, object_name, position, static_image_path=None):
        self.layer_name = layer_name
        self.object_name = object_name
        self.position = pygame.Vector2(position)
        self.static_image_path = static_image_path
        self.display_name, self.dialog_text = self._resolve_dialog(layer_name, object_name)
        self.load_error = None
        self.animation_error = None
        self.frame_paths = []
        if static_image_path:
            self.animation = Animation([self._load_static_image(static_image_path)], NPC_IDLE_FRAME_TIME)
        else:
            self.animation = self._load_animation()
        self.image = self.animation.current_frame
        self.base_rect = self.image.get_rect(midbottom=self.position)
        self.rect = self.base_rect.copy()

    def _resolve_dialog(self, layer_name, object_name):
        if self.boss_defeated and object_name in self.POST_BOSS_DIALOGS:
            return self.POST_BOSS_DIALOGS[object_name]
        if object_name in self.OBJECT_DIALOGS:
            return self.OBJECT_DIALOGS[object_name]
        if layer_name in self.DIALOGS:
            return self.DIALOGS[layer_name]
        return (object_name or "村民", "……")

    def _load_animation(self):
        frame_paths = self._animation_paths()
        if not frame_paths:
            return Animation([self._load_static_image()], NPC_IDLE_FRAME_TIME)

        frames = []
        try:
            for path in frame_paths[:NPC_IDLE_FRAME_LIMIT]:
                frames.append(pygame.image.load(path).convert_alpha())
        except Exception as exc:
            self.animation_error = str(exc)
            frames = []

        if not frames:
            return Animation([self._load_static_image()], NPC_IDLE_FRAME_TIME)

        self.frame_paths = frame_paths[: len(frames)]
        return Animation(frames, NPC_IDLE_FRAME_TIME)

    def _animation_paths(self):
        if self.layer_name == "god":
            return sorted(GOD_DIR.glob("0214-16505471-000*.tga"))

        if self.layer_name == "elder" and self.object_name:
            return sorted(ELDER_DIR.glob(f"{self.object_name}-*.tga"))

        if self.layer_name == "guard":
            return sorted(NPC1_DIR.glob("屏幕截图_2026-06-23_200921_*.png"))

        if self.layer_name == "apprentice":
            return sorted(NPC2_DIR.glob("屏幕截图_2026-06-23_203200_*.png"))

        return []

    def _load_static_image(self, image_path=None):
        if image_path is not None:
            try:
                image = pygame.image.load(str(image_path)).convert_alpha()
                # 缩放自定义 NPC 截图，使其尺寸接近孙悟空 (156x199 -> ~100高)
                w, h = image.get_width(), image.get_height()
                new_w = max(1, round(w * NPC_SCALE))
                new_h = max(1, round(h * NPC_SCALE))
                image = pygame.transform.smoothscale(image, (new_w, new_h))
                return image
            except Exception as exc:
                self.load_error = str(exc)
                return self._placeholder_image()

        image_path = self._image_path()
        if image_path is None and self.layer_name == "child":
            return self._child_image()

        try:
            if image_path is None:
                raise FileNotFoundError(f"no configured image for {self.layer_name}:{self.object_name}")
            return pygame.image.load(image_path).convert_alpha()
        except Exception as exc:
            self.load_error = str(exc)
            return self._placeholder_image()

    def _image_path(self):
        if self.layer_name == "god":
            return GOD_DIR / "0214-16505471-00000.tga"

        if self.layer_name == "elder" and self.object_name:
            path = ELDER_DIR / f"{self.object_name}-00000.tga"
            if path.exists():
                return path

        return None

    def _child_image(self):
        image = pygame.Surface((40, 58), pygame.SRCALPHA)
        pygame.draw.ellipse(image, (245, 205, 150), (9, 2, 22, 22))
        pygame.draw.arc(image, (65, 45, 35), (8, 0, 24, 18), 3.2, 6.1, 3)
        pygame.draw.circle(image, (45, 35, 30), (16, 13), 2)
        pygame.draw.circle(image, (45, 35, 30), (24, 13), 2)
        pygame.draw.arc(image, (130, 64, 50), (15, 12, 10, 7), 0.2, 2.9, 1)
        pygame.draw.polygon(image, (92, 178, 118), [(12, 25), (28, 25), (34, 50), (6, 50)])
        pygame.draw.line(image, (235, 220, 150), (20, 27), (20, 48), 2)
        pygame.draw.rect(image, (70, 95, 135), (11, 49, 7, 8))
        pygame.draw.rect(image, (70, 95, 135), (22, 49, 7, 8))
        pygame.draw.line(image, (80, 55, 40), (18, 57), (14, 57), 2)
        pygame.draw.line(image, (80, 55, 40), (26, 57), (30, 57), 2)
        return image

    def _placeholder_image(self):
        colors = {
            "god": (230, 190, 75),
            "elder": (120, 170, 230),
            "child": (110, 210, 140),
            "guard": (140, 180, 160),
            "apprentice": (100, 200, 150),
            "herbalist": (240, 180, 160),
            "merchant": (200, 180, 120),
        }
        image = pygame.Surface((42, 58), pygame.SRCALPHA)
        image.fill(colors.get(self.layer_name, (190, 120, 210)))
        pygame.draw.rect(image, (255, 255, 255), image.get_rect(), 2)
        return image

    @property
    def interaction_rect(self):
        return self.base_rect.inflate(NPC_INTERACTION_PADDING, NPC_INTERACTION_PADDING)

    @staticmethod
    def _draw_shadow(surface, camera, rect):
        """在地面绘制软阴影，分离地面感和融入感。"""
        shadow_rect = camera.apply_rect(rect)
        cx = shadow_rect.centerx
        # 阴影落在角色底部附近
        shadow_y = shadow_rect.bottom - 3
        shadow_w = int(shadow_rect.width * 0.55)
        shadow_h = max(2, int(shadow_rect.height * 0.10))

        # 三层渐变软阴影
        layers = [
            (int(shadow_w), shadow_h, (12, 28, 6), 70),
            (int(shadow_w * 0.75), max(1, int(shadow_h * 0.6)), (16, 35, 8), 45),
            (int(shadow_w * 0.45), max(1, int(shadow_h * 0.3)), (20, 40, 10), 25),
        ]
        for w, h, color, alpha in layers:
            if w < 2 or h < 1:
                continue
            shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # 椭圆软阴影
            for dy in range(h):
                progress = dy / h
                current_w = int(w * (1 - progress * progress) ** 0.5)
                if current_w < 2:
                    continue
                fade = int(alpha * (1 - progress) * (1 - progress))
                if fade < 2:
                    continue
                sx = (w - current_w) // 2
                for dx in range(current_w):
                    shadow_surf.set_at((sx + dx, dy), (*color, fade))
            sx = cx - w // 2
            sy = shadow_y - h // 2
            surface.blit(shadow_surf, (sx, sy))

    def update(self, dt):
        self.animation.update(dt)
        self.image = self.animation.current_frame
        self.rect = self.image.get_rect(midbottom=self.position)

    def draw(self, surface, camera):
        if self.layer_name in ("guard", "apprentice"):
            self._draw_shadow(surface, camera, self.rect)
        surface.blit(self.image, camera.apply_rect(self.rect))
