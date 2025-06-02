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
        # Ensure you are using the corrected CSV file, e.g., "fixed.csv"
        df = pd.read_csv("fixed.csv", dtype={'filename': str}).head(4) # [MODIFIED]

        # === Colors ===
        GT_COLOR = "#89CFF0" # Baby Blue for Ground Truth
        MATCH_COLOR = GREEN
        MISMATCH_COLOR = RED

        # === Image Display Scale Factor ===
        # Adjust this factor to control the size of the displayed images and their bounding boxes.
        # Try values between 0.5 and 1.0 or higher if needed.
        IMAGE_DISPLAY_SCALE_FACTOR = 0.65 # [NEW & MODIFIED] Example: increased from an effective 0.36

        image_mobs = []
        true_texts = []
        pred_texts = []
        gt_box_groups = []
        pred_box_groups = []

        for idx, row in df.iterrows():
            # Load image
            img_path = os.path.join("fixed", str(row["filename"]))
            # Scale the image using the defined factor
            image = ImageMobject(img_path).scale(IMAGE_DISPLAY_SCALE_FACTOR) # [MODIFIED]
            image_mobs.append(image)

            # Group for ground truth bounding boxes and labels
            gt_group = VGroup()
            if pd.notna(row["true_boxes"]) and row["true_boxes"].lower() != "none" and row["true_boxes"].strip() != "": # [MODIFIED] Added check for NaN and empty string
                gt_boxes_data = str(row["true_boxes"]).split(";") # Ensure it's a string before split
                gt_labels = str(row["true_labels"]).split("|")    # Ensure it's a string
                for i, box_coords_str in enumerate(gt_boxes_data):
                    if not box_coords_str.strip(): continue # Skip if box string is empty after split
                    x1, y1, x2, y2 = map(int, box_coords_str.split(","))
                    w_orig, h_orig = x2 - x1, y2 - y1

                    # Scale bounding box dimensions
                    w_scaled = w_orig * IMAGE_DISPLAY_SCALE_FACTOR # [MODIFIED]
                    h_scaled = h_orig * IMAGE_DISPLAY_SCALE_FACTOR # [MODIFIED]

                    rect = Rectangle(width=w_scaled, height=h_scaled, color=GT_COLOR, stroke_width=2) # [MODIFIED] stroke_width can be adjusted

                    # Calculate scaled center coordinates for positioning
                    center_x_orig_pixels = x1 + w_orig / 2
                    center_y_orig_pixels = y1 + h_orig / 2

                    # Position the center of the scaled rectangle relative to the scaled image's top-left corner
                    rect.move_to(
                        image.get_corner(UP + LEFT) + 
                        RIGHT * center_x_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR + 
                        DOWN * center_y_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR  # [MODIFIED] Consistent scaling factor
                    )
                    
                    label = gt_labels[i % len(gt_labels)]
                    label_text = Text(label, font_size=18, color=GT_COLOR).scale(IMAGE_DISPLAY_SCALE_FACTOR*0.7) # [MODIFIED] Scale font slightly with image
                    label_text.next_to(rect.get_corner(UP + LEFT), UP, buff=0.05 * IMAGE_DISPLAY_SCALE_FACTOR) # [MODIFIED] Scale buff
                    gt_group.add(rect, label_text)

            # Group for predicted bounding boxes and labels
            pred_group = VGroup()
            if pd.notna(row["pred_boxes"]) and row["predicted_labels"].lower() != "none" and row["pred_boxes"].strip() != "": # [MODIFIED]
                pred_boxes_data = str(row["pred_boxes"]).split(";") # Ensure it's a string
                pred_labels = str(row["predicted_labels"]).split("|") if pd.notna(row["predicted_labels"]) and str(row["predicted_labels"]).lower() != "none" else [] # Ensure it's a string
                true_labels_list = str(row["true_labels"]).split("|") if pd.notna(row["true_labels"]) and str(row["true_labels"]).lower() != "none" else [] # Ensure it's a string

                for i, box_coords_str in enumerate(pred_boxes_data):
                    if not box_coords_str.strip(): continue
                    x1, y1, x2, y2 = map(int, box_coords_str.split(","))
                    w_orig, h_orig = x2 - x1, y2 - y1
                    
                    w_scaled = w_orig * IMAGE_DISPLAY_SCALE_FACTOR # [MODIFIED]
                    h_scaled = h_orig * IMAGE_DISPLAY_SCALE_FACTOR # [MODIFIED]

                    label = pred_labels[i] if i < len(pred_labels) else "?"
                    color = MATCH_COLOR if label in true_labels_list else MISMATCH_COLOR
                    
                    rect = Rectangle(width=w_scaled, height=h_scaled, color=color, stroke_width=2) # [MODIFIED]

                    center_x_orig_pixels = x1 + w_orig / 2
                    center_y_orig_pixels = y1 + h_orig / 2
                    
                    rect.move_to(
                        image.get_corner(UP + LEFT) + 
                        RIGHT * center_x_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR + 
                        DOWN * center_y_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR # [MODIFIED]
                    )
                    
                    label_text = Text(label, font_size=18, color=color).scale(IMAGE_DISPLAY_SCALE_FACTOR*0.7) # [MODIFIED]
                    label_text.next_to(rect.get_corner(UP + LEFT), UP, buff=0.05 * IMAGE_DISPLAY_SCALE_FACTOR) # [MODIFIED]
                    pred_group.add(rect, label_text)

            # Texts under each image
            true_text = Text(f"True: {row['true_labels']}", font_size=20).set_color(GT_COLOR).scale(IMAGE_DISPLAY_SCALE_FACTOR) # [MODIFIED]
            pred_text = Text(f"Pred: {row['predicted_labels']}", font_size=20).set_color(WHITE).scale(IMAGE_DISPLAY_SCALE_FACTOR) # [MODIFIED]

            image_mobs.append(image) # This was already there, ensure it's not duplicated if you copy-paste
            true_texts.append(true_text)
            pred_texts.append(pred_text)
            gt_box_groups.append(gt_group)
            pred_box_groups.append(pred_group)

        # Arrange images
        # Consider removing or adjusting the .scale() here if IMAGE_DISPLAY_SCALE_FACTOR is large enough
        image_group = Group(*image_mobs).arrange(RIGHT, buff=0.5).to_edge(UP, buff=1.5) # [MODIFIED] Example: removed .scale(0.9)

        # Position labels under each image
        for i in range(len(image_mobs)): # [MODIFIED] Use len(image_mobs) in case fewer than 4 images are processed
            if i < len(true_texts): true_texts[i].next_to(image_mobs[i], DOWN, buff=0.2 * IMAGE_DISPLAY_SCALE_FACTOR) # [MODIFIED]
            if i < len(pred_texts): pred_texts[i].next_to(true_texts[i], DOWN, buff=0.15 * IMAGE_DISPLAY_SCALE_FACTOR) # [MODIFIED]

        all_true_texts = VGroup(*true_texts)
        all_pred_texts = VGroup(*pred_texts)
        all_gt_boxes = VGroup(*gt_box_groups)
        all_pred_boxes = VGroup(*pred_box_groups)

        # === Animation ===
        self.play(FadeIn(image_group), run_time=2)
        self.wait(0.5)

        # Show Ground Truth
        for i in range(len(gt_box_groups)): # [MODIFIED]
            if gt_box_groups[i].submobjects: # Only play if there's something to create
                self.play(Create(gt_box_groups[i]), FadeIn(true_texts[i]), run_time=1.5)
        self.wait(2)

        # Show Predictions
        for i in range(len(pred_box_groups)): # [MODIFIED]
            if gt_box_groups[i].submobjects: self.play(FadeOut(gt_box_groups[i]), run_time=0.5)
            if pred_box_groups[i].submobjects: # Only play if there's something to create
                self.play(Create(pred_box_groups[i]), FadeIn(pred_texts[i]), run_time=1.5)

        self.wait(3)
        # Ensure all groups actually contain mobjects before trying to fade them out
        mobjects_to_fade = [m for m in [all_pred_boxes, all_true_texts, all_pred_texts, image_group, title] if m.submobjects or isinstance(m, Text)] # [MODIFIED]
        if mobjects_to_fade:
            self.play(*[FadeOut(m) for m in mobjects_to_fade]) # [MODIFIED]
