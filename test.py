from manim import *

class CreateCircle(Scene):
    def construct(self):
        #circle = Circle()  # create a circle
        #circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
        #self.play(Create(circle))  # show the circle on screen

        seeds = VGroup()
        q = MathTex("ACG","TTA","GTA","GCC")
        self.add(q)
        for i in range(0,4):
            seed_label = MathTex("s_" + str(i))
            seed_box = SurroundingRectangle(q[i])
            seed_label.next_to(seed_box, UP, buff=0.1)
            seeds.add(VGroup(seed_box, seed_label))
#        seeds.arrange(buff=0.1)
        self.add(seeds)
        query_text = MathTex("q")
        query_text.next_to(seeds[0][0], LEFT)
        self.add(query_text)

        #self.play(Write(text))

        #seeds.next_to(circle, UP)

