import pygame


class UI:
    def __init__(self, font_path, window_size, start_background_path=None, button_paths=None):
        self.window_width, self.window_height = window_size
        self.window_size = window_size
        self.font_error = None
        self.start_background_error = None
        self.button_errors = {}
        self.title_font = self._load_font(font_path, 46)
        self.large_font = self._load_font(font_path, 34)
        self.text_font = self._load_font(font_path, 26)
        self.small_font = self._load_font(font_path, 22)
        self.start_background = self._load_background(start_background_path)
        self.buttons = self._load_buttons(button_paths or {})

    def _load_font(self, font_path, size):
        try:
            return pygame.font.Font(str(font_path), size)
        except Exception as exc:
            self.font_error = str(exc)
            return pygame.font.Font(None, size)

    def _load_background(self, path):
        if path is None:
            return None

        try:
            image = pygame.image.load(path).convert()
            return pygame.transform.smoothscale(image, self.window_size)
        except Exception as exc:
            self.start_background_error = str(exc)
            return None

    def _load_buttons(self, button_paths):
        buttons = {}
        for name, path in button_paths.items():
            try:
                buttons[name] = pygame.image.load(path).convert_alpha()
            except Exception as exc:
                self.button_errors[name] = str(exc)
        return buttons

    def draw_start(self, surface):
        # 夜空渐变背景
        for row in range(self.window_height):
            t = row / max(1, self.window_height - 1)
            r = int(8 + t * 12)
            g = int(10 + t * 25)
            b = int(35 + t * 45)
            pygame.draw.line(surface, (r, g, b), (0, row), (self.window_width, row))

        # 星星
        import random
        rng = random.Random(42)
        for _ in range(80):
            x = rng.randint(20, self.window_width - 20)
            y = rng.randint(10, self.window_height // 2)
            size = rng.randint(1, 3)
            alpha = rng.randint(120, 255)
            color = (255, 248, 210, alpha)
            star_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, color, (size + 1, size + 1), size)
            surface.blit(star_surf, (x - size, y - size))

        # 月亮
        moon_x, moon_y = self.window_width - 120, 90
        moon_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(moon_surf, (255, 248, 200, 230), (50, 50), 40)
        pygame.draw.circle(moon_surf, (12, 14, 40, 200), (65, 42), 30)
        surface.blit(moon_surf, (moon_x - 50, moon_y - 50))

        # 远山轮廓
        mountain_color = (18, 20, 28)
        points1 = [(0, self.window_height), (0, 420),
                   (100, 370), (200, 400), (300, 340), (450, 380),
                   (550, 310), (700, 360), (self.window_width, 390),
                   (self.window_width, self.window_height)]
        pygame.draw.polygon(surface, mountain_color, points1)

        mountain_color2 = (14, 16, 22)
        points2 = [(0, self.window_height), (0, 450),
                   (150, 420), (280, 440), (400, 410), (520, 435),
                   (650, 400), (self.window_width, 430),
                   (self.window_width, self.window_height)]
        pygame.draw.polygon(surface, mountain_color2, points2)

        # 标题区域 - 金色装饰线
        title_y = 150
        line_y = title_y + 40
        line_width = 160
        for offset in range(line_width):
            t_val = abs(offset - line_width // 2) / (line_width // 2)
            alpha = int(180 * (1 - t_val))
            c = (232 - int(150 * t_val), 214 - int(140 * t_val), 150, alpha)
            dot_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            dot_surf.fill(c)
            surface.blit(dot_surf, (self.window_width // 2 - line_width // 2 + offset - 190, line_y))

        # 标题文字
        self._draw_center_text(surface, self.title_font, "🐵 西游记观音院 🐵", title_y, (255, 232, 150))

        # 副标题
        subtitle_y = title_y + 55
        subtitle_surf = self.text_font.render("—— 祸起观音院 ——", True, (220, 200, 150))
        subtitle_rect = subtitle_surf.get_rect(center=(self.window_width // 2, subtitle_y))
        surface.blit(subtitle_surf, subtitle_rect)

        # 故事简介
        intro_y = subtitle_y + 45
        intro_lines = [
            "唐僧师徒西行途中，夜宿观音院。",
            "黑熊精趁夜盗走锦斓袈裟，",
            "孙悟空奉命降妖，夺回宝物！",
        ]
        for i, line in enumerate(intro_lines):
            line_surf = pygame.Surface(
                (self.text_font.size(line)[0] + 20, 28), pygame.SRCALPHA
            )
            line_surf.fill((0, 0, 0, 100))
            pygame.draw.rect(line_surf, (180, 160, 100, 80), line_surf.get_rect(), 1)
            surface.blit(
                line_surf,
                ((self.window_width - line_surf.get_width()) // 2, intro_y + i * 32),
            )
            self._draw_text(
                surface, self.small_font, line,
                (self.window_width - self.small_font.size(line)[0]) // 2,
                intro_y + i * 32 + 4,
                (235, 225, 195),
            )

        # 底部按钮区域
        btn_base_y = self.window_height - 130
        self._draw_button_hint(surface, "ok", "按 Enter 开始游戏", btn_base_y)
        self._draw_button_hint(surface, None, "按 H 查看操作说明", btn_base_y + 46, font=self.small_font)
        self._draw_button_hint(surface, "no", "按 Esc 退出", btn_base_y + 92, font=self.small_font)

        # 底部版权
        copyright_surf = self.small_font.render(
            "Pygame RPG · 2026", True, (120, 120, 130)
        )
        surface.blit(copyright_surf, (16, self.window_height - 26))

    def draw_help(self, surface):
        surface.fill((20, 24, 30))
        self._draw_center_text(surface, self.large_font, "操作说明", 92, (255, 232, 150))
        lines = [
            "方向键 / WASD：移动",
            "E / 空格：对话 / 交互",
            "J：战斗攻击",
            "M：静音 / 恢复音频",
            "P：暂停游戏",
            "F11 / Alt+Enter：全屏 / 窗口切换",
            "Esc：返回 / 退出",
        ]
        self._draw_panel_lines(surface, lines, 150, line_height=42)
        self._draw_button_hint(surface, "no", "按 Esc 返回开始界面", 520, font=self.small_font)

    def draw_pause(self, surface):
        overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))
        panel = pygame.Rect(170, 185, self.window_width - 340, 190)
        pygame.draw.rect(surface, (24, 28, 34), panel)
        pygame.draw.rect(surface, (232, 214, 160), panel, 3)
        self._draw_center_text(surface, self.large_font, "游戏已暂停", panel.top + 44, (255, 232, 150))
        self._draw_button_hint(surface, "ok", "按 P 继续", panel.top + 104)
        self._draw_button_hint(surface, "no", "按 Esc 退出", panel.top + 148, font=self.small_font)

    def draw_controls_hint(self, surface, muted, fullscreen=False):
        mute_text = "静音" if muted else "音频开"
        fs_text = "全屏" if fullscreen else "窗口"
        hint = f"WASD/方向键移动  E/空格对话  J攻击  P暂停  M静音  F11{fs_text}  Esc退出  [{mute_text}]"
        text_surface = self.small_font.render(hint, True, (255, 255, 255))
        bg_rect = text_surface.get_rect(topleft=(12, 10)).inflate(16, 8)
        bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        surface.blit(bg, bg_rect.topleft)
        surface.blit(text_surface, (bg_rect.left + 8, bg_rect.top + 4))

    def draw_temple_prompt(self, surface, text="按 E / 空格进入观音院"):
        panel = pygame.Rect(214, self.window_height - 110, self.window_width - 428, 76)
        prompt = pygame.Surface(panel.size, pygame.SRCALPHA)
        prompt.fill((0, 0, 0, 145))
        pygame.draw.rect(prompt, (232, 214, 160), prompt.get_rect(), 2)
        surface.blit(prompt, panel.topleft)

        self._draw_image_center(surface, "temple", (panel.left + 70, panel.centery), 116, 42)
        self._draw_image_center(surface, "small_temple", (panel.right - 44, panel.centery), 44, 44)
        self._draw_text(surface, self.small_font, text, panel.left + 128, panel.centery - 12, (255, 245, 215))

    def draw_return_prompt(self, surface, text="妖怪已除，按 E / 空格返回村庄复命"):
        panel = pygame.Rect(196, self.window_height - 110, self.window_width - 392, 76)
        prompt = pygame.Surface(panel.size, pygame.SRCALPHA)
        prompt.fill((0, 0, 0, 145))
        pygame.draw.rect(prompt, (232, 214, 160), prompt.get_rect(), 2)
        surface.blit(prompt, panel.topleft)

        self._draw_image_center(surface, "village", (panel.left + 70, panel.centery), 116, 42)
        self._draw_text(surface, self.small_font, text, panel.left + 132, panel.centery - 12, (255, 245, 215))

    def draw_banner(self, surface, text):
        panel = pygame.Rect(0, 150, self.window_width, 70)
        banner = pygame.Surface(panel.size, pygame.SRCALPHA)
        banner.fill((90, 0, 0, 190))
        surface.blit(banner, panel.topleft)
        pygame.draw.rect(surface, (235, 90, 80), panel, 3)
        self._draw_center_text(surface, self.large_font, text, panel.centery, (255, 226, 150))

    def draw_result(self, surface, image, title, lines, hint, actions=None):
        self._draw_full_background(surface, image, (18, 18, 24), 170)
        panel = pygame.Rect(86, 160, self.window_width - 172, 250)
        pygame.draw.rect(surface, (24, 28, 32), panel)
        pygame.draw.rect(surface, (232, 214, 160), panel, 3)
        self._draw_center_text(surface, self.large_font, title, panel.top + 44, (255, 232, 150))

        y = panel.top + 104
        for line in lines:
            self._draw_center_text(surface, self.text_font, line, y, (245, 245, 245))
            y += 42

        if actions:
            self._draw_action_row(surface, actions, panel.bottom - 34)
        else:
            self._draw_center_text(surface, self.small_font, hint, panel.bottom - 34, (215, 215, 215))

    def _draw_full_background(self, surface, image, fallback_color, overlay_alpha):
        if image:
            surface.blit(image, (0, 0))
        else:
            surface.fill(fallback_color)

        overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        surface.blit(overlay, (0, 0))

    def _draw_panel_lines(self, surface, lines, start_y, line_height):
        panel = pygame.Rect(150, start_y - 24, self.window_width - 300, len(lines) * line_height + 46)
        pygame.draw.rect(surface, (29, 34, 40), panel)
        pygame.draw.rect(surface, (232, 214, 160), panel, 2)
        y = start_y
        for line in lines:
            self._draw_center_text(surface, self.text_font, line, y, (245, 245, 245))
            y += line_height

    def _draw_action_row(self, surface, actions, y):
        total_width = sum(190 for _ in actions) + max(0, len(actions) - 1) * 24
        x = (self.window_width - total_width) // 2
        for button_name, text in actions:
            self._draw_button_hint(surface, button_name, text, y, center_x=x + 95, font=self.small_font)
            x += 214

    def _draw_button_hint(self, surface, button_name, text, y, center_x=None, font=None):
        font = font or self.text_font
        center_x = center_x or self.window_width // 2
        text_surface = font.render(text, True, (245, 245, 245))
        button = self._scaled_image(button_name, 42, 32)
        width = text_surface.get_width() + 14
        if button:
            width += button.get_width() + 10

        rect = pygame.Rect(0, 0, width + 24, max(42, text_surface.get_height() + 16))
        rect.center = (center_x, y)
        pygame.draw.rect(surface, (28, 32, 38), rect)
        pygame.draw.rect(surface, (232, 214, 160), rect, 2)

        x = rect.left + 12
        if button:
            button_rect = button.get_rect(midleft=(x, rect.centery))
            surface.blit(button, button_rect)
            x = button_rect.right + 10
        else:
            fallback_rect = pygame.Rect(x, rect.centery - 14, 34, 28)
            pygame.draw.rect(surface, (75, 83, 92), fallback_rect)
            pygame.draw.rect(surface, (232, 214, 160), fallback_rect, 1)
            x = fallback_rect.right + 10

        text_rect = text_surface.get_rect(midleft=(x, rect.centery))
        surface.blit(text_surface, text_rect)

    def _draw_image_center(self, surface, image_name, center, max_width, max_height):
        image = self._scaled_image(image_name, max_width, max_height)
        if image:
            surface.blit(image, image.get_rect(center=center))

    def _scaled_image(self, image_name, max_width, max_height):
        image = self.buttons.get(image_name)
        if not image:
            return None

        scale = min(max_width / image.get_width(), max_height / image.get_height(), 1)
        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )
        if size == image.get_size():
            return image
        return pygame.transform.smoothscale(image, size)

    def _draw_text(self, surface, font, text, x, y, color):
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def _draw_center_text(self, surface, font, text, y, color):
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect(center=(self.window_width // 2, y))
        surface.blit(text_surface, rect)
