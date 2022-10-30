from manim import *

class SeedHeuristic(Scene):
    def construct(self):
        query = MathTex("ACG","TTA","GTA","GCC")
        query_label = MathTex("q")
        query_label.next_to(query, LEFT)
        self.play(Write(query_label))
        self.play(Write(query))

        seeds = VGroup()
        for i in range(0,4):
            seed_label = MathTex("s_" + str(i))
            seed_box = SurroundingRectangle(query[i], buff=0.0)
            seed_box.set_fill(YELLOW, opacity=0.2)
            seed_label.next_to(seed_box, UP, buff=0.1)
            seeds.add(VGroup(seed_box, seed_label))
            self.play(Create(seed_box), Write(seed_label))

        seeds_brace_label = BraceLabel(seeds, "seeds", brace_direction=UP)
        self.play(Create(seeds_brace_label))