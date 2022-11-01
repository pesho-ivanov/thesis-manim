from manim import *
import re

#import pdb; pdb.set_trace()

class SeedHeuristicPrecomputation(Scene):
    def construct(self):
        # TODO:
        # - after first seeds, matches, crumbs: introduce the concept
        # - parallelize the matching and the crumbs after showing one
        # - build a trie
        # - spread the crumbs up the trie
        # - another scene: Alignmnet
        k = 2
        query = Text("AACC")
        #query = Text("AACCGGTT")
        ref = Text("...GGAAGTCAACCGATT...") #\n\n..GATCCGGCTT..")

        fsz = 28

        # colors [dark, light]
        grey = "#888888"
        blues = ["#6C8EBF", "#DAE8FC"]
        yellows = ["#D79B00", "#FFE6CC"]
        purples = ["#9673A6", "#E1D5E7"]
        greens = ["#82B366", "#D5E8D4"]
        colors = [blues, yellows, purples, greens]
        delta = [0.08*d for d in [UP+LEFT, UP+RIGHT, DOWN+LEFT, DOWN+RIGHT]]

        # introduce query
        query.shift(1.0*(UP+RIGHT))
        query_label = Text("query", slant=ITALIC, font_size=fsz, color=grey)
        query_label.next_to(query, 15 * LEFT)
        self.play(
            Write(query_label),
            Write(query))

        # introduce reference
        ref.next_to(query, DOWN, buff=1.0)
        ref_label = Text("reference", slant=ITALIC, font_size=fsz, color=grey)
        ref_label.next_to(ref, LEFT)
        ref_label.align_to(query_label, LEFT)
        self.play(Write(ref_label),
        Write(ref))

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
                Write(seed_label),
                seed.animate.set_color(c[0]),
                ShowPassingFlash(
                    seed.seed_box,
                    run_time=2,
                    time_width=2.0))
            num += 1

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

                self.play(Create(ul), Create(crumb), Flash(crumb, color=c, line_length=SMALL_BUFF))
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
                self.play(
                    Uncreate(ul),
                    FadeOut(fly))


        #seeds_brace_label = BraceLabel(seeds, "seeds", label_constructor=Text, brace_direction=UP, font_size=fsz)
        #self.play(Create(seeds_brace_label))