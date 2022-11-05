import string
import random

from manim import *
from manim_voiceover import VoiceoverScene
#from manim_voiceover.services.gtts import GTTSService
from manim_voiceover.services.azure import AzureService
import re
import regex  # for finding the shortest edit distance

from contextlib import contextmanager
from norm_play import NormPlay

#import pdb; pdb.set_trace()

# TODO:
# - after first seeds, matches, crumbs: introduce the concept
# - parallelize the matching and the crumbs after showing one
# - build a trie
# - spread the crumbs up the trie
# - another scene: Alignmnet

#seeds_brace_label = BraceLabel(seeds, "seeds", label_constructor=Text, brace_direction=UP, font_size=font_sz)
#self.play(Create(seeds_brace_label))

class SeedHeuristicPrecomputation(VoiceoverScene, MovingCameraScene, NormPlay):
    def setup_voiceover(self):
        os.environ["AZURE_SUBSCRIPTION_KEY"] = "60c24696a4da49ba94a903def1577350"
        os.environ["AZURE_SERVICE_REGION"] = "eastus"

        #self.set_speech_service(GTTSService())
        self.set_speech_service(
            AzureService(
                voice = "en-CA-LiamNeural",
                #voice = "en-NZ-MitchellNeural",
                #voice = "en-CA-ClaraNeural",
                #voice = "en-US-AriaNeural",
                style = "friendly", # "shouting", #"whispering",
                #style = "advertisement_upbeat",
                #style ="poetry-reading",
                #style ="newscast-casual",
                #global_speed = 1.15
            )
        )

    def construct(self):
        self.setup_voiceover()
        n = 1
        k = 2
        query = Text("AACCGGTT")
        ref = Text("...GGAAGTCAACCGATT...") #\n\n..GATCCGGCTT..")

        font_sz = 28

        # colors [dark, light]
        grey = "#888888"
        blues = ["#6C8EBF", "#DAE8FC"]
        yellows = ["#D79B00", "#FFE6CC"]
        purples = ["#9673A6", "#E1D5E7"]
        greens = ["#82B366", "#D5E8D4"]
        colors = [blues, yellows, purples, greens]
        delta = [0.08*d for d in [UP+LEFT, UP+RIGHT, DOWN+LEFT, DOWN+RIGHT]]

        #background = ImageMobject("external/blackboard-huge.jpg")
        #background.to_edge(RIGHT)
        #self.bring_to_back(background)
        #self.add(background)

        #self.camera.background_image = "external/blackboard-medium.jpg"
        #self.camera.init_background()

        #for i in range(n):
        #    q_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=len(query.text)))
        #    q = Text(q_text, slant=ITALIC, font_size=font_sz, color=grey)
        #    self.play(FadeIn(q))

        with self.voiceover(text="DNA sequencing machines produce large amount of \"reads\".") as tracker:
            print(tracker.duration)
            with self.norm_play(2*tracker.duration) as normed:
                query.shift(1.0*(UP+RIGHT))
                query_label = Text("Query", slant=ITALIC, font_size=font_sz, color=grey)
                query_label.next_to(query, 15 * LEFT)
                normed.play(FadeIn(query_label, run_time=5.0))
                normed.play(
                    #FadeIn(query_label),
                    Write(query, run_time=1.0)
                    )
                self.wait(10.0)
        return

        with self.voiceover(text="If we analyse a known organism, we can compare the new data to a reference genome.") as tracker:
            ref.next_to(query, UP, buff=1.0)
            ref_label = Text("Reference", slant=ITALIC, font_size=font_sz, color=grey)
            ref_label.next_to(ref, LEFT)
            ref_label.align_to(query_label, LEFT)
            self.play(
                FadeIn(ref_label),
                Write(ref),
                run_time=tracker.duration)
            self.mywait()

        with self.voiceover(text="We will now show how to find the where each query read aligns in a reference.") as tracker:
            # TODO: visualize the mistakes and talk about edit distance

            # search for the best match (edit distance)
            r = regex.search(r'(?b:{})'.format(query.text)+"{e}", ref.text)

            # fly a box from the seed to a match
            fly = query.copy()
            target = ref[r.start():r.end()]
            target_box = SurroundingRectangle(target, buff=0.06)
            self.play(fly.animate.become(target))
            self.play(
                ShowPassingFlash(
                    target_box,
                    #run_time=1.0,
                    time_width=2.0))
#                run_time=tracker.duration)
            self.mywait()

        with self.voiceover(text="We will use the A-star shortest path algorithm to find optimal alignments very efficiently.",
                      subcaption="We will use the A* shortest path algorithm to find optimal alignments very efficiently.") as tracker:
            # TODO: draw a magnet at node 9, or reverse the Flash ray direction
            self.camera.frame.save_state()
            EXP = GREEN
            TARGET = RED
            vertices = [1, 2, 3, 4, 5, 6, 7, 8, 9]  
            edges = [(1, 6), (1, 7), (7, 8),
                    (2, 3), (2, 4), (2, 5), (2, 8), (2, 6), (2, 7), 
                    (3, 4), (3, 6),
                    (4, 5), (4, 9)]  
            g = Graph(vertices, edges, layout="kamada_kawai", layout_scale=3, labels=True)
            g.scale(0.4)
            g.next_to(query, 0.3*DOWN + 2*RIGHT)
            self.play(Create(g))
            self.play(self.camera.frame.animate.scale(0.5).move_to(g))
            self.play(g.vertices[1].animate.set_color(EXP), Flash(g.vertices[1], color=EXP),
                      g.vertices[9].animate.set_color(TARGET), Flash(g.vertices[9], color=TARGET))
            self.play(g.edges[(1,6)].animate.set_stroke(EXP), g.vertices[6].animate.set_color(EXP), Flash(g.vertices[6], color=EXP))
            self.play(g.edges[(3,6)].animate.set_stroke(EXP), g.vertices[3].animate.set_color(EXP), Flash(g.vertices[3], color=EXP),
                      g.edges[(1,7)].animate.set_stroke(EXP), g.vertices[7].animate.set_color(EXP), Flash(g.vertices[7], color=EXP))
            self.play(g.edges[(2,6)].animate.set_stroke(EXP), g.vertices[2].animate.set_color(EXP), Flash(g.vertices[2], color=EXP),
                      g.edges[(3,4)].animate.set_stroke(EXP), g.vertices[4].animate.set_color(EXP), Flash(g.vertices[4], color=EXP))
            self.play(g.edges[(4,9)].animate.set_stroke(EXP), g.vertices[9].animate.set_color(EXP), Flash(g.vertices[9], color=EXP))
            self.mywait()
            self.play(
                Uncreate(g), 
                Restore(self.camera.frame),
                run_time=0.5)

        with self.voiceover(text="To direct the A-star search, we will first divide the read into short seeds.") as tracker:
            # split query into seeds
            seeds = VGroup()
            num = 0
            for i in range(0,len(query),k):
                c = colors[num%len(colors)]
                seed = query[i:i+k]
                seed.num = num%len(colors)
                seed.i = i
                seed.text = query.text[i:i+k]
                seed_label = Tex("$s_{}$".format(num), color=c[0])
                seed.seed_box = SurroundingRectangle(seed, buff=0.06, color=c[0])
                seed_label.next_to(seed.seed_box, UP, buff=0.1)
                seeds.add(VGroup(seed, seed_label))
                self.play(
                    FadeIn(seed_label),
                    seed.animate.set_color(c[0]),
                    ShowPassingFlash(
                        seed.seed_box,
                        #run_time=1.0,
                        time_width=0.5,
                        rate_func=rate_functions.ease_out_sine))
#                    run_time=tracker.duration)
                num += 1
        self.mywait()

        with self.voiceover(
            text="We will now match each seed to all its exact occurences and mark the preceding reference positions with what we call bread crumbs.\
                These crumbs will prove handy when we will want to know how promising a certain direction is for bringing us home, to our best alignment.") as tracker:
            def CrumbFactory(num, c):
                sq_f = lambda: Square(color=c, fill_color=c, fill_opacity=1, side_length=0.08)
                tri_f = lambda: Triangle(color=c, fill_color=c, fill_opacity=1).scale(0.05)
                romb_f = lambda: Square(color=c, fill_color=c, fill_opacity=1, side_length=0.08).rotate(PI/4)
                dot_f = lambda: Circle(color=c, fill_color=c, fill_opacity=1, radius=0.05)
                crumb_constructor = [ sq_f, tri_f, romb_f, dot_f ]
                return crumb_constructor[num]

            # match the seeds into the reference
            for (seed, label) in seeds:
                c = seed.get_color()
                num = seed.num
                Crumb = CrumbFactory(num, c)
                self.play(Wiggle(seed), scale_value=1.2, run_time=1.5)
                for m in re.finditer(seed.text, ref.text):
                    j = m.start()  # in ref

                    # fly a box from the seed to a match
                    fly = seed.copy()
                    fly.generate_target()
                    target_box = ref[j:m.end()]
                    fly.target.move_to(target_box)
                    self.play(MoveToTarget(fly))

                    # add crumbs before this match while moving a slider backwards through the query
                    crumb = Crumb()
                    crumb.next_to(ref[j], UP, buff=1.5*SMALL_BUFF)
                    crumb.shift(delta[num])
                    ul = Underline(query[seed.i], color=c)
                    first_crumb = fly.copy()

                    self.play(Create(ul), first_crumb.animate.become(crumb))
                    for i in range(seed.i-1, -1, -1): # i in query
                        j -= 1
                        if j<0 or ref.text[j]=='.': break
                        crumb = crumb.copy()
                        trace = TracedPath(crumb.get_center, dissipating_time=0.5, stroke_opacity=[0, 1], stroke_color=c, stroke_width=4.0)
                        self.add(crumb, trace)
                        crumb_to = Crumb()
                        crumb_to.next_to(ref[j], UP, buff=1.5*SMALL_BUFF)
                        crumb_to.shift(delta[num])
                        self.play(
                            crumb.animate(path_arc=PI/2).move_to(crumb_to),
                            ul.animate().move_to(Underline(query[i])))
                    self.play(Uncreate(ul))