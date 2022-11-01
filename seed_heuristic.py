from manim import *
import re

class SeedHeuristic(Scene):
    def construct(self):
        # TODO: pause on first seeds, matches, crumbs
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
        query.shift(1.0*(UP+RIGHT))
        #import pdb; pdb.set_trace()
        query_label = Text("query", slant=ITALIC, font_size=fsz)
        query_label.next_to(query, 15 * LEFT)
        self.play(Write(query_label))
        self.play(Write(query))

        # introduce reference
        ref = Text("..GGAAGTCAACCGATT..") #\n\n..GATCCGGCTT..")
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
            seed.seed_box = BackgroundRectangle(seed, buff=0.0, color=c[0])
            #seed_box.set_fill(color=c[1], opacity=1)
            seed_label.next_to(seed.seed_box, UP, buff=0.1)
            seeds.add(VGroup(seed, seed_label))
            self.play(Create(seed.seed_box), Write(seed_label))
            num += 1

        #seeds_brace_label = BraceLabel(seeds, "seeds", label_constructor=Text, brace_direction=UP, font_size=fsz)
        #self.play(Create(seeds_brace_label))

        def CrumbFactory(num, c):
            sq_f = lambda: Square(color=c, fill_color=c, fill_opacity=1, side_length=1.0).scale(0.1)
            tri_f = lambda: Triangle(color=c, fill_color=c, fill_opacity=1).scale(0.06)
            romb_f = lambda: Square(color=c, fill_color=c, fill_opacity=1, side_length=1.0).scale(0.1).rotate(PI/4)
            dot_f = lambda: Dot(color=c)
            crumb_constructor = [ sq_f, tri_f, romb_f, dot_f ]
            return crumb_constructor[num]

        # match the seeds into the reference
        for (seed, label) in seeds:
            c = seed.get_color()
            num = seed.num
            Crumb = CrumbFactory(num, c)
            self.play(Wiggle(Group(seed, seed.seed_box)))
            for m in re.finditer(seed.text, ref.text):
                match_box = seed.seed_box.copy()
                match_box.generate_target()
                j = m.start()  # in ref
                target_box = SurroundingRectangle(ref[j:m.end()], buff=0.0)
                match_box.target.move_to(target_box)
                self.play(MoveToTarget(match_box))
                # add crumbs before this match
                crumb = Crumb()
                crumb.next_to(ref[j], UP, buff=SMALL_BUFF)
                crumb.shift(delta[num])
#                self.add(crumb)
                self.play(Create(crumb), Flash(crumb, color=c, line_length=SMALL_BUFF))
                for i in range(seed.i, 0, -1): # i in query
                    j -= 1
                    if j<0 or ref.text[j]=='.': break
                    crumb = crumb.copy()
                    trace = TracedPath(crumb.get_center, dissipating_time=0.5, stroke_opacity=[0, 1], stroke_color=c, stroke_width=4.0)
                    self.add(crumb, trace)
                    crumb_to = Crumb()
                    crumb_to.next_to(ref[j], UP, buff=SMALL_BUFF)
                    crumb_to.shift(delta[num])
                    self.play(crumb.animate(path_arc=PI/2).move_to(crumb_to))
