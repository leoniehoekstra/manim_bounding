from manim import *
import pandas as pd
import os

class SampleBoundingBoxes(Scene):
    def construct(self):
        # === Title ===
        title = Text("Ground Truth vs Predicted Labels", font_size=42, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)

        # === Load CSV and filenames ===
        df = pd.read_csv("fixed.csv", dtype={'filename': str}).head(4)
        filenames = df["filename"].tolist()

        # === Directories ===
        base_dir = "sampled_images_bounding_v3"
        gt_dir = "output_ground_truth"
        pred_dir = "output_predicted"

        # === Image scale factor ===
        SCALE = 0.6

        # === Phase 1: Original Images ===
        orig_images = []
        for fname in filenames:
            path = os.path.join(base_dir, fname)
            img = ImageMobject(path).scale(SCALE)
            orig_images.append(img)

        orig_group = VGroup(*orig_images).arrange_in_grid(rows=2, cols=2, buff=0.7)
        orig_group.move_to(ORIGIN)

        self.play(FadeIn(orig_group), run_time=2)

        narration1 = Paragraph("Here are 4 sampled validation images.",
                               "They are shown without any annotations.",
                               font_size=28, alignment="center", line_spacing=0.7).set_color(WHITE)
        narration1.width = config.frame_width - 2
        narration1.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(narration1))
        self.wait(3)

        # === Phase 2: Ground Truth Overlays ===
        gt_images = []
        for fname in filenames:
            gt_name = "gt_" + fname
            path = os.path.join(gt_dir, gt_name)
            img = ImageMobject(path).scale(SCALE)
            gt_images.append(img)

        gt_group = VGroup(*gt_images).arrange_in_grid(rows=2, cols=2, buff=0.7)
        gt_group.move_to(orig_group)

        self.play(FadeOut(narration1), run_time=1)
        narration2 = Paragraph("Now we overlay the ground truth bounding boxes.",
                               "These are the human-annotated reference objects.",
                               font_size=28, alignment="center", line_spacing=0.7).set_color("#89CFF0")
        narration2.width = config.frame_width - 2
        narration2.to_edge(DOWN, buff=0.4)

        self.play(ReplacementTransform(orig_group, gt_group), FadeIn(narration2), run_time=2)
        self.wait(3)

        # === Phase 3: Predicted Overlays ===
        pred_images = []
        for fname in filenames:
            pred_name = "pred_" + fname
            path = os.path.join(pred_dir, pred_name)
            img = ImageMobject(path).scale(SCALE)
            pred_images.append(img)

        pred_group = VGroup(*pred_images).arrange_in_grid(rows=2, cols=2, buff=0.7)
        pred_group.move_to(gt_group)

        self.play(FadeOut(narration2), run_time=1)
        narration3 = Paragraph("Finally, here are the model's predicted bounding boxes.",
                               "Green means correct, red means incorrect class prediction.",
                               font_size=28, alignment="center", line_spacing=0.7).set_color(WHITE)
        narration3.width = config.frame_width - 2
        narration3.to_edge(DOWN, buff=0.4)

        self.play(ReplacementTransform(gt_group, pred_group), FadeIn(narration3), run_time=2)
        self.wait(4)

        # === End ===
        self.play(FadeOut(pred_group), FadeOut(narration3), FadeOut(title))
        self.wait(1)
