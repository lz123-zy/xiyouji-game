"""通用帧动画控制器：按固定间隔切换帧，支持循环/单次播放。被 NPC、怪物等模块复用。"""


class Animation:
    def __init__(self, frames, frame_time, loop=True):
        self.frames = frames
        self.frame_time = frame_time
        self.loop = loop
        self.frame_index = 0
        self.elapsed = 0.0
        self.finished = False

    @property
    def current_frame(self):
        return self.frames[self.frame_index]

    def reset(self):
        self.frame_index = 0
        self.elapsed = 0.0
        self.finished = False

    def update(self, dt):
        if self.finished or len(self.frames) <= 1:
            return

        self.elapsed += dt
        if self.elapsed < self.frame_time:
            return

        self.elapsed = 0.0
        self.frame_index += 1
        if self.frame_index < len(self.frames):
            return

        # 循环播放回到第一帧，单次播放则停在最后一帧
        if self.loop:
            self.frame_index = 0
        else:
            self.frame_index = len(self.frames) - 1
            self.finished = True
