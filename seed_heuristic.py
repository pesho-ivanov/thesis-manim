from manim import *
import re

class SeedHeuristic(Scene):
    def construct(self):
        fsz = 28

        # colors [dark, light]
        blue = ["#6C8EBF", "#DAE8FC"]
        yellow = ["#D79B00", "#FFE6CC"]
        purple = ["#9673A6", "#E1D5E7"]
        green = ["#82B366", "#D5E8D4"]
        colors = [blue, yellow, purple, green]
        delta = [0.08*d for d in [UP+LEFT, UP+RIGHT, DOWN+LEFT, DOWN+RIGHT]]

        # introduce query
        k = 2
        query = Text("AACCGGTT")
        #import pdb; pdb.set_trace()
        query_label = Text("query", slant=ITALIC, font_size=fsz)
        query_label.next_to(query, 15 * LEFT)
        self.play(Write(query_label))
        self.play(Write(query))

        # introduce reference
        ref = Text("..GAAGTCAACCGATT..") #\n\n..GATCCGGCTT..")
        ref.next_to(query, DOWN, buff=1.0)
        ref_label = Text("reference", slant=ITALIC, font_size=fsz)
        ref_label.next_to(ref, LEFT)
        ref_label.align_to(query_label, LEFT)
        self.play(Write(ref_label))
        self.play(Write(ref))

        # split query into seeds
        seeds = VGroup()
        num = 0
        for i in range(0,len(query),k):
            c = colors[num%len(colors)]
            seed = query[i:i+k]
            seed.num = num%len(colors)
            seed.i = i
            seed.set_color(c[0])
            seed.text = query.text[i:i+k]
            seed_label = Tex("$s_{}$".format(num))
            #seed_box = SurroundingRectangle(seed, buff=0.0, color=c[0])
            seed_box = BackgroundRectangle(seed, buff=0.0, color=c[0])
            #seed_box.set_fill(color=c[1], opacity=1)
            seed_label.next_to(seed_box, UP, buff=0.1)
            seeds.add(VGroup(seed, seed_box, seed_label))
            self.play(Create(seed_box), Write(seed_label))
            num += 1

        seeds_brace_label = BraceLabel(seeds, "seeds", label_constructor=Text, brace_direction=UP, font_size=fsz)
        self.play(Create(seeds_brace_label))

        # match the seeds into the reference
        for (seed, seed_box, label) in seeds:
            c = seed.get_color()
            num = seed.num
            for m in re.finditer(seed.text, ref.text):
                match_box = seed_box.copy()
                match_box.generate_target()
                j = m.start()  # in ref
                target_box = SurroundingRectangle(ref[j:m.end()], buff=0.0)
                match_box.target.move_to(target_box)
                self.play(MoveToTarget(match_box))
                # add crumbs before this match
                dot = Dot(color=c)
                dot.next_to(ref[j], UP, buff=SMALL_BUFF)
                dot.shift(delta[num])
                self.add(dot)
                self.play(Flash(dot, color=c, line_length=SMALL_BUFF))
                for i in range(seed.i, 0, -1): # i in query
                    j -= 1
                    if j<0: break
                    dot = dot.copy()
                    trace = TracedPath(dot.get_center, dissipating_time=0.5, stroke_opacity=[0, 1], stroke_color=c, stroke_width=4.0)
                    self.add(dot, trace)
                    dot_to = Dot()
                    dot_to.next_to(ref[j], UP, buff=SMALL_BUFF)
                    dot_to.shift(delta[num])
                    self.play(dot.animate(path_arc=PI/2).move_to(dot_to))
