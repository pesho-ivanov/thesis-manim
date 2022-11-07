from contextlib import contextmanager
from typing import Optional, Generator
from manim import Scene, ChangeSpeed, AnimationGroup, Wait, DEFAULT_WAIT_TIME, Animation

class NormedPlayer:
    def __init__(self, scene: Scene, target_duration: float):
        self.scene = scene
        self.target_duration = target_duration 
        self.plays = []
        self.total_duration: float = 0.0
    
    def play(self, *args, **kwargs):
        animations = self.scene.compile_animations(*args, **kwargs)
        duration = self.scene.get_run_time(animations)
        self.total_duration += duration
        self.plays.append((animations, kwargs))
        print(animations)

    def wait(self, duration: float = DEFAULT_WAIT_TIME, **kwargs):
        self.total_duration += duration
        animations = (Wait(duration),)
        assert 'run_time' not in kwargs
        kwargs['run_time'] = duration
        self.plays.append((animations, kwargs))

    def pause(self, duration: float = DEFAULT_WAIT_TIME):
        self.wait(duration=duration, frozen_frame=True)

    def wait_until(self, *args, **kwargs):
        self.wait(*args, **kwargs)

    def execute_plays(self):
        speed_factor = self.total_duration / self.target_duration
        for (animations, kwargs) in self.plays:
            anim_group = AnimationGroup(*animations)

            if 'subcaption_duration' in kwargs and kwargs['subcaption_duration'] is not None:
                kwargs['subcaption_duration'] *= speed_factor
            if 'subcaption_offset' in kwargs and kwargs['subcaption_offset'] is not None:
                kwargs['subcaption_offset'] *= speed_factor

            ch_speed = ChangeSpeed(anim_group, speedinfo={0.0: speed_factor})
            self.scene.play(ch_speed, **kwargs)

class NormPlay(Scene):
    current_player: Optional[NormedPlayer]

    @contextmanager
    def norm_play(self, duration: float) -> Generator[NormedPlayer, None, None]:
        assert duration > 0.0
        try:
            self.current_player = NormedPlayer(self, duration)
            yield self.current_player
        finally:
            self.current_player.execute_plays()