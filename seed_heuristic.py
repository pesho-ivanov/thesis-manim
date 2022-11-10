import string
import random

from manim import *
from manim_voiceover import VoiceoverScene
#from manim_voiceover.services.gtts import GTTSService
from manim_voiceover.services.azure import AzureService
import re
import regex  # for finding the shortest edit distance
from typing import Generator

from contextlib import contextmanager
from norm_play import NormPlay, NormedPlayer

#import pdb; pdb.set_trace()

# TODO:
# - after first seeds, matches, crumbs: introduce the concept
# - parallelize the matching and the crumbs after showing one
# - build a trie
# - spread the crumbs up the trie
# - another scene: Alignmnet

n = 3 #10  # number of reads 
k = 2  # kmer size
d = 3  # trie depth
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

def mylabel(s):
    return Text(s, slant=ITALIC, font_size=font_sz, color=grey)

class Overline(Line):
    def __init__(self, mobject, buff=SMALL_BUFF, **kwargs):
        super().__init__(LEFT, RIGHT, buff=buff, **kwargs)
        self.match_width(mobject)
        self.next_to(mobject, UP, buff=self.buff)

class SeedHeuristicPrecomputation(VoiceoverScene, MovingCameraScene, NormPlay):
    
    @contextmanager
    def voiceover_norm(self, wait_after=1.0, **kwargs) -> Generator[NormedPlayer, None, None]:
        try:
            with self.voiceover(**kwargs) as tracker:
                with self.norm_play(tracker.duration) as normed:
                    yield normed
        finally:
            self.wait(wait_after)

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

    def ref_query(self):
        # show many reads
        with self.voiceover_norm(text="DNA sequencing machines produce large amount of \"reads\".") as normed:
            rand_vec = lambda : UP*random.normalvariate(0.0, 1.0) + RIGHT*random.normalvariate(0.0, 3.0)
            Q = [ Text(''.join(random.choices("ACGT", k=len(query.text)))).shift(rand_vec()) for _ in range(n) ]
            anims = [ Succession(FadeIn(q), FadeOut(q)) for q in Q ]
            normed.play(LaggedStart(*anims, lag_ratio=0.2))

        # shows query
        with self.voiceover_norm(text="Each of them originates from a certain genome location.") as normed:
            query.shift(1.0*(DOWN+RIGHT))
            query.label = mylabel("Query").next_to(query, 15 * LEFT)
            normed.play(FadeIn(query.label))
            normed.play(Write(query))

        # shows ref
        with self.voiceover_norm(text="If we analyse a known organism, we can compare the new data to a reference genome.") as normed:
            ref.next_to(query, UP, buff=1.0)
            ref.label = mylabel("Reference").next_to(ref, LEFT).align_to(query.label, LEFT)
            normed.play(FadeIn(ref.label), Write(ref))

        return ref, query

    def seeds_matches_crumbs(self, ref, query):
        # aligns whole query to best ref location
        with self.voiceover_norm(text="We will now show how to find where each query read aligns in a reference.") as normed:
                # TODO: visualize the mistakes and talk about edit distance

                # search for the best match (edit distance)
                r = regex.search(r'(?b:{})'.format(query.text)+"{e}", ref.text)

                # fly a box from the seed to a match
                query_copy = query.copy()
                query_match = ref[r.start():r.end()]
                query_match.box = SurroundingRectangle(query_match, buff=0.06)
                normed.play(query_copy.animate.become(query_match))
                normed.play(ShowPassingFlash(query_match.box, time_width=2.0))

        # A* search graph example 
        with self.voiceover_norm(text="We will use the A-star shortest path algorithm to find optimal alignments very efficiently.",
                      subcaption="We will use the A* shortest path algorithm to find optimal alignments very efficiently.") as normed:
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
            g.scale(0.4).next_to(query, 0.3*DOWN + 2*RIGHT)
            normed.play(Create(g), self.camera.frame.animate.scale(0.5).move_to(g))
            normed.play(g.vertices[1].animate.set_color(EXP), Flash(g.vertices[1], color=EXP),
                      g.vertices[9].animate.set_color(TARGET), Flash(g.vertices[9], color=TARGET))
            normed.play(g.edges[(1,6)].animate.set_stroke(EXP), g.vertices[6].animate.set_color(EXP), Flash(g.vertices[6], color=EXP))
            normed.play(g.edges[(3,6)].animate.set_stroke(EXP), g.vertices[3].animate.set_color(EXP), Flash(g.vertices[3], color=EXP),
                      g.edges[(1,7)].animate.set_stroke(EXP), g.vertices[7].animate.set_color(EXP), Flash(g.vertices[7], color=EXP))
            normed.play(g.edges[(2,6)].animate.set_stroke(EXP), g.vertices[2].animate.set_color(EXP), Flash(g.vertices[2], color=EXP),
                      g.edges[(3,4)].animate.set_stroke(EXP), g.vertices[4].animate.set_color(EXP), Flash(g.vertices[4], color=EXP))
            normed.play(g.edges[(4,9)].animate.set_stroke(EXP), g.vertices[9].animate.set_color(EXP), Flash(g.vertices[9], color=EXP))
            normed.wait()
            normed.play(
                Uncreate(g), 
                Restore(self.camera.frame),
                run_time=0.5)

        # split query into seeds
        with self.voiceover_norm(text="To direct the A-star search, we will first divide the read into short seeds.") as normed:
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
                seed_label.next_to(seed.seed_box, DOWN, buff=0.1)
                seeds.add(VGroup(seed, seed_label))
                normed.play(
                    FadeIn(seed_label),
                    seed.animate.set_color(c[0]),
                    ShowPassingFlash(
                        seed.seed_box,
                        time_width=0.5,
                        rate_func=rate_functions.ease_out_sine))
                num += 1
            seeds_brace_label = BraceLabel(seeds,
                text=("seeds", ),
                label_constructor=Text,
                brace_direction=DOWN,
                font_size=font_sz,
                color=grey,
                #slant=ITALIC,
                )
            self.play(FadeIn(seeds_brace_label))

        # matches all seeds on query and puts crumbs on reference
        with self.voiceover_norm(
            text="We will now match each seed to all its exact occurences and mark the preceding reference positions with what we call bread crumbs.\
                These crumbs will prove handy when we will want to know how promising a certain direction is for bringing us to a best alignment.") as normed:
            def CrumbFactory(num, c):
                sq_f = lambda: Square(color=c, fill_color=c, fill_opacity=1, side_length=0.08)
                tri_f = lambda: Triangle(color=c, fill_color=c, fill_opacity=1).scale(0.05)
                romb_f = lambda: Square(color=c, fill_color=c, fill_opacity=1, side_length=0.08).rotate(PI/4)
                dot_f = lambda: Circle(color=c, fill_color=c, fill_opacity=1, radius=0.05)
                crumb_constructor = [ sq_f, tri_f, romb_f, dot_f ]
                return crumb_constructor[num%len(crumb_constructor)]

            # match seeds onto reference
            for (seed, label) in seeds:
                c = seed.get_color()
                num = seed.num
                Crumb = CrumbFactory(num, c)
                normed.play(Wiggle(seed), scale_value=1.2, run_time=1.5)
                for m in re.finditer(seed.text, ref.text):
                    j = m.start()  # in ref

                    # fly the seed to a match
                    seed_copy = seed.copy()
                    seed_copy.generate_target()
                    match = ref[j:m.end()].set_color(c)
                    seed_copy.target.move_to(match)
                    arrow = Arrow(seed.get_top(), match.get_bottom(), stroke_width=3, tip_length=0.15, color=c,
                        max_stroke_width_to_length_ratio=1000, max_tip_length_to_length_ratio=1000).set_opacity(0.25)
                    normed.play(MoveToTarget(seed_copy), GrowArrow(arrow))

                    # add crumbs before this match while moving a slider backwards through the query
                    crumb = Crumb()
                    crumb.next_to(ref[j], UP, buff=1.5*SMALL_BUFF)
                    crumb.shift(delta[num])
                    slider = Overline(query[seed.i], color=c)
                    first_crumb = match.copy()
                    normed.play(Create(slider), first_crumb.animate.become(crumb))

                    for i in range(seed.i-1, -1, -1): # i in query
                        j -= 1
                        if j<0 or ref.text[j]=='.': break
                        crumb = crumb.copy()
                        trace = TracedPath(crumb.get_center, dissipating_time=0.5, stroke_opacity=[0, 1], stroke_color=c, stroke_width=4.0)
                        normed.add(crumb, trace)
                        crumb_to = Crumb()
                        crumb_to.next_to(ref[j], UP, buff=1.5*SMALL_BUFF)
                        crumb_to.shift(delta[num])
                        normed.play(
                            crumb.animate(path_arc=PI/2).move_to(crumb_to),
                            slider.animate().move_to(Overline(query[i])))
                    normed.play(Uncreate(slider))
    
    def trie(self, ref, query):
        # builds trie
        with self.voiceover_norm(text="In order to give the possibility to start our search from one place, we will aggregate the the whole reference into a trie index.") as normed:
            vertices = ['root', 'A', 'C', 'G', 'T']  
            edges = [('root', 'A'), ('root', 'C')]
            partitions = [['A', 'C', 'G', 'T'], ['root']]
            g = Graph(vertices, edges, layout="partite", partitions=partitions, layout_scale=3, layout_config={'align': 'horizontal'}, labels=True)
            g.scale(0.4).next_to(ref, UP)
            label_trie = mylabel('Trie').next_to(g, LEFT).align_to(ref.label, LEFT)
            normed.play(FadeIn(label_trie), Create(g))

            for i in range(0,len(ref),d):
                kmer = query[i:i+d]
                kmer.text = query.text[i:i+d]
                #kmer.box = SurroundingRectangle(kmer, buff=0.06, color=YELLOW)

            new_edges = [('root', 'G')]
            #edge_config = {('root', 'G'): {'weight': 0.6}}
            group = g.add_edges(*new_edges)
            #TexMobject(label).move_to(point)
            normed.play(Create(group))

            new_edges = [('root', 'G')]
            #edge_config = {('root', 'G'): {'weight': 0.6}}
            group = g.add_edges(*new_edges)
            #TexMobject(label).move_to(point)
            normed.play(Create(group))

        # crumbs on trie

    def construct(self):
        self.setup_voiceover()

        #background = ImageMobject("external/blackboard-huge.jpg")
        #background.to_edge(RIGHT)
        #self.bring_to_back(background)
        #self.add(background)

        #self.camera.background_image = "external/blackboard-medium.jpg"
        #self.camera.init_background()

        ref, query = self.ref_query()
        self.seeds_matches_crumbs(ref, query)
        self.trie(ref, query)
