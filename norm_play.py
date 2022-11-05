from contextlib import contextmanager
from typing import Optional, Generator
from manim import Scene, ChangeSpeed, AnimationGroup

class NormedPlayer:
    def __init__(self, scene: Scene, target_duration: float):
        self.scene = scene
        self.target_duration = target_duration 
        self.plays = []
        self.total_duration: float = 0.0
    
    def play(
        self,
        *args,
        subcaption=None,
        subcaption_duration=None,
        subcaption_offset=0,
        **kwargs,
    ):
        duration = self.scene.get_run_time(args)
        self.total_duration += duration
        self.plays.append(tuple((args, subcaption, subcaption_duration, subcaption_offset, kwargs)))
        #self.plays.append(tuple((args, subcaption, subcaption_duration, subcaption_offset, kwargs)))

    #def wait(
    #    self,
    #    duration: float = DEFAULT_WAIT_TIME,
    #    stop_condition: Callable[[], bool] | None = None,
    #    frozen_frame: bool | None = None,
    #):
    #    self.total_duration += duration
    #    args = (Wait,)
    #    self.plays.append(tuple((args, subcaption, subcaption_duration, subcaption_offset, kwargs)))
    #    self.play(
    #        Wait(
    #            run_time=duration,
    #            stop_condition=stop_condition,
    #            frozen_frame=frozen_frame,
    #        )
    #    )

    def execute_plays(self):
        speed_factor = self.total_duration / self.target_duration
        for (args, subcaption, subcaption_duration, subcaption_offset, kwargs) in self.plays:
            anims = AnimationGroup(*args)
            self.scene.play(
                ChangeSpeed(anims, speedinfo={0.0: speed_factor}),
                subcaption = subcaption,
                subcaption_duration = subcaption_duration*speed_factor if subcaption_duration is not None else None,
                subcaption_offset = subcaption_offset*speed_factor if subcaption_offset is not None else None,
                **kwargs)

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