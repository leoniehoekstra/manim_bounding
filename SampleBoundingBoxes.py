from manim import *
import pandas as pd
import os

class SampleBoundingBoxes(Scene):
    def construct(self):
        # === Title ===
        title = Text("Ground Truth vs Predicted Labels", font_size=42, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        # === Load CSV ===
        df = pd.read_csv("sample_results_bounding_v3.csv").head(4)

        # === Colors ===
        GT_COLOR = "#89CFF0"
        MATCH_COLOR = GREEN
        MISMATCH_COLOR = RED

        image_mobs = []
        true_texts = []
        pred_texts = []
        gt_box_groups = []
        pred_box_groups = []

        for idx, row in df.iterrows():
            # Load image
            img_path = os.path.join("fixed", str(row["filename"]))
            image = ImageMobject(img_path).scale(0.4)

            # Group for ground truth bounding boxes and labels
            gt_group = VGroup()
            if row["true_boxes"] != "none":
                gt_boxes = row["true_boxes"].split(";")
                gt_labels = row["true_labels"].split("|")
                for i, box in enumerate(gt_boxes):
                    x1, y1, x2, y2 = map(int, box.split(","))
                    w, h = x2 - x1, y2 - y1
                    rect = Rectangle(width=w, height=h, color=GT_COLOR, stroke_width=3)
                    rect.move_to(image.get_corner(UP + LEFT) + RIGHT * (x1 + w/2) * 0.4 + DOWN * (y1 + h/2) * 0.4)
                    label = gt_labels[i % len(gt_labels)]  # in case fewer labels than boxes
                    label_text = Text(label, font_size=20, color=GT_COLOR)
                    label_text.next_to(rect.get_corner(UP + LEFT), UP, buff=0.05)
                    gt_group.add(rect, label_text)

            # Group for predicted bounding boxes and labels
            pred_group = VGroup()
            if row["pred_boxes"] != "none":
                pred_boxes = row["pred_boxes"].split(";")
                pred_labels = row["predicted_labels"].split("|") if row["predicted_labels"] != "none" else []
                true_labels = row["true_labels"].split("|") if row["true_labels"] != "none" else []
                for i, box in enumerate(pred_boxes):
                    x1, y1, x2, y2 = map(int, box.split(","))
                    w, h = x2 - x1, y2 - y1
                    label = pred_labels[i] if i < len(pred_labels) else "?"
                    color = MATCH_COLOR if label in true_labels else MISMATCH_COLOR
                    rect = Rectangle(width=w, height=h, color=color, stroke_width=3)
                    rect.move_to(image.get_corner(UP + LEFT) + RIGHT * (x1 + w/2) * 0.4 + DOWN * (y1 + h/2) * 0.4)
                    label_text = Text(label, font_size=20, color=color)
                    label_text.next_to(rect.get_corner(UP + LEFT), UP, buff=0.05)
                    pred_group.add(rect, label_text)

            # Texts under each image
            true_text = Text(f"True: {row['true_labels']}", font_size=22).set_color(GT_COLOR)
            pred_text = Text(f"Pred: {row['predicted_labels']}", font_size=22).set_color(WHITE)

            image_mobs.append(image)
            true_texts.append(true_text)
            pred_texts.append(pred_text)
            gt_box_groups.append(gt_group)
            pred_box_groups.append(pred_group)

        # Arrange images
        image_group = VGroup(*image_mobs).arrange(RIGHT, buff=0.5).scale(0.9).to_edge(UP, buff=1.5)

        # Position labels under each image
        for i in range(4):
            true_texts[i].next_to(image_mobs[i], DOWN, buff=0.2)
            pred_texts[i].next_to(true_texts[i], DOWN, buff=0.15)

        all_true_texts = VGroup(*true_texts)
        all_pred_texts = VGroup(*pred_texts)
        all_gt_boxes = VGroup(*gt_box_groups)
        all_pred_boxes = VGroup(*pred_box_groups)

        # === Animation ===
        self.play(FadeIn(image_group), run_time=2)
        self.wait(0.5)

        # Show Ground Truth
        for i in range(4):
            self.play(Create(gt_box_groups[i]), FadeIn(true_texts[i]), run_time=1.5)
        self.wait(2)

        # Show Predictions
        for i in range(4):
            self.play(FadeOut(gt_box_groups[i]), run_time=0.5)
            self.play(Create(pred_box_groups[i]), FadeIn(pred_texts[i]), run_time=1.5)

        self.wait(3)
        self.play(FadeOut(all_pred_boxes), FadeOut(all_true_texts), FadeOut(all_pred_texts), FadeOut(image_group), FadeOut(title))
