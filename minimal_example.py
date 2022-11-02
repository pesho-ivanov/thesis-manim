from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from manim_voiceover.services.azure import AzureService
import os

class TestScene(VoiceoverScene):
    def construct(self):
        os.environ["AZURE_SUBSCRIPTION_KEY"] = "60c24696a4da49ba94a903def1577350"
        os.environ["AZURE_SERVICE_REGION"] = "eastus"
        self.set_speech_service(
            AzureService(
                voice="en-US-AriaNeural",
                style="newscast-casual",  # global_speed=1.15
            )
        )

        #dot = Dot().set_color(GREEN)
        #self.add_sound("click.wav")
        #self.add(dot)
        #self.wait()
        #self.add_sound("click.wav")
        #dot.set_color(BLUE)
        #self.wait()
        #self.add_sound("click.wav")
        #dot.set_color(RED)
        #self.wait()
        
#        self.set_speech_service(GTTSService())
#        print(sys.modules["manim.__main__"])
#        print('\n'.join(sys.modules))


        #print(os.environ["AZURE_SUBSCRIPTION_KEY"])
        #print(os.environ["AZURE_SERVICE_REGION"])

        #self.add_sound('media/tts/878efa499350c975497cae445577e4d415642de11a199eca88de36ae07ad3fdb.mp3')
        #self.add_sound('media/tts/fb0b3c83970d5ddd277f61ade5830f13eec5003ffb8a615b674da9230aef9945.mp3')
        circle = Circle()
        with self.voiceover(text="First.") as tracker:
            self.play(Create(circle))#, run_time=tracker.duration)
            self.play(Wiggle(circle))#, run_time=tracker.duration)
        #self.wait(5)
        
        #self.add_sound('media/tts/fb0b3c83970d5ddd277f61ade5830f13eec5003ffb8a615b674da9230aef9945.mp3')
        square = Square()
        with self.voiceover(text="Second.") as tracker:
            self.play(Create(square))#, run_time=tracker.duration)

        self.wait()